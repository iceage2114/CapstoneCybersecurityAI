from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, AsyncIterator
from pydantic import BaseModel
from ..database.database import get_db
from ..models.plugin_model import Plugin
from ..models.conversation_model import Conversation, Message, QueryWithHistory
from ..services.ai_service import AIService
from ..services.conversation_service import ConversationService
import json
import asyncio
import random

router = APIRouter()
ai_service = AIService()
conversation_service = ConversationService()

class QueryRequest(BaseModel):
    query: str
    plugin_id: Optional[int] = None
    auto_select_plugin: bool = False

class QueryResponse(BaseModel):
    response: str
    plugin_used: Optional[str] = None

class PluginRecommendation(BaseModel):
    id: int
    name: str
    description: str
    relevance_score: float

@router.post("/process", response_model=QueryResponse)
def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Process a cybersecurity query using the AI service
    """
    # Validate plugin_id if provided
    if request.plugin_id:
        plugin = db.query(Plugin).filter(Plugin.id == request.plugin_id).first()
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin with ID {request.plugin_id} not found"
            )
    
    # Process the query
    result = ai_service.process_query(
        query=request.query,
        plugin_id=request.plugin_id,
        db=db
    )
    
    # Check for errors
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    return QueryResponse(
        response=result["response"],
        plugin_used=result.get("plugin_used")
    )

@router.post("/process-with-history")
def process_query_with_history(request: QueryWithHistory, db: Session = Depends(get_db)):
    """
    Process a cybersecurity query with conversation history
    """
    # Validate plugin_id if provided
    if request.plugin_id:
        plugin = db.query(Plugin).filter(Plugin.id == request.plugin_id).first()
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin with ID {request.plugin_id} not found"
            )
    
    # Get conversation history if conversation_id is provided
    conversation_history = []
    if request.conversation_id:
        # Check if conversation exists
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {request.conversation_id} not found"
            )
        
        # Get messages for the conversation
        messages = db.query(Message).filter(Message.conversation_id == request.conversation_id).all()
        conversation_history = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]
    
    # Process the query with history
    result = ai_service.process_query_with_history(
        query=request.query,
        conversation_history=conversation_history,
        plugin_id=request.plugin_id,
        db=db
    )
    
    # Check for errors
    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["error"]
        )
    
    # If conversation_id is provided, save the interaction
    if request.conversation_id:
        # Save user message
        user_message = Message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.query
        )
        db.add(user_message)
        
        # Save assistant response
        assistant_message = Message(
            conversation_id=request.conversation_id,
            role="assistant",
            content=result["response"],
            plugin_used=result.get("plugin_used")
        )
        db.add(assistant_message)
        
        # Update conversation timestamp
        conversation = db.query(Conversation).filter(Conversation.id == request.conversation_id).first()
        db.commit()
    
    return QueryResponse(
        response=result["response"],
        plugin_used=result.get("plugin_used")
    )

@router.post("/stream")
async def stream_response(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Stream a response for a cybersecurity query
    """
    print(f"Received streaming request: {request.query}")
    
    # Handle automatic plugin selection if requested
    selected_plugin = None
    if request.auto_select_plugin:
        print("Auto plugin selection mode enabled")
        # Get all available plugins
        available_plugins = db.query(Plugin).all()
        
        # If we have plugins, determine if any should be used
        if available_plugins:
            # Simple keyword matching for demo purposes
            # In a real system, you would use a more sophisticated approach
            # such as embeddings or a classifier model
            query_lower = request.query.lower()
            for plugin in available_plugins:
                keywords = plugin.description.lower().split()
                # Check if any keywords from the plugin description are in the query
                if any(keyword in query_lower for keyword in keywords if len(keyword) > 3):
                    selected_plugin = plugin
                    print(f"Auto-selected plugin: {plugin.name}")
                    break
    # Validate plugin_id if provided
    elif request.plugin_id:
        selected_plugin = db.query(Plugin).filter(Plugin.id == request.plugin_id).first()
        if not selected_plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plugin with ID {request.plugin_id} not found"
            )
    
    async def generate_stream():
        try:
            print(f"Generating stream for query: {request.query}")
            
            # Ensure model is loaded
            try:
                ai_service._load_model()
                print("Model loaded successfully")
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                yield json.dumps({"error": f"Error loading model: {str(e)}"}) + "\n"
                return
            
            # Create system prompt with cybersecurity focus
            system_content = "You are a cybersecurity analyst assistant. Your goal is to provide accurate, helpful information about cybersecurity topics."
            
            # Add plugin context if available
            plugin_used = None
            if selected_plugin:
                plugin_context = {
                    "name": selected_plugin.name,
                    "description": selected_plugin.description,
                    "api_endpoint": selected_plugin.api_endpoint,
                    "parameters": json.loads(selected_plugin.parameters) if isinstance(selected_plugin.parameters, str) else selected_plugin.parameters
                }
                
                plugin_prompt = f"""
                You have access to the following cybersecurity tool/API:
                Name: {plugin_context['name']}
                Description: {plugin_context['description']}
                API Endpoint: {plugin_context['api_endpoint']}
                
                When appropriate, use this tool to address the user's query.
                """
                system_content += "\n\n" + plugin_prompt
                plugin_used = selected_plugin.name
                
                # Let the user know which plugin was auto-selected
                if request.auto_select_plugin:
                    yield json.dumps({"plugin_used": plugin_used}) + "\n"
                
                # If it's the IPinfo plugin, execute it and show the process
                if selected_plugin.name == "IPinfo":
                    # Step 1: Have the LLM acknowledge the request with reasoning
                    # Format a prompt for the LLM to make a decision about acknowledging the request
                    acknowledgment_prompt = f"""You are a cybersecurity assistant helping a user with their query: '{request.query}'
                    The IPinfo plugin has been selected to help answer this query.
                    
                    Provide a brief acknowledgment to the user about using the IPinfo tool.
                    Your response must be in valid JSON format with two fields:
                    1. 'reasoning': Explain why you're acknowledging the request
                    2. 'choice': The actual acknowledgment text to show the user
                    
                    Example response format:
                    {{"reasoning": "The user is asking about IP information, so I should acknowledge that I'll use the IPinfo tool.", "choice": "I'll help you get information about your IP address using the IPinfo tool."}}                    
                    """
                    
                    # Get the LLM's decision for acknowledgment
                    acknowledgment_response = ai_service.process_query(acknowledgment_prompt)["response"]
                    
                    # Extract the JSON from the response
                    try:
                        # Find JSON between curly braces
                        import re
                        json_match = re.search(r'\{[^\{\}]*"reasoning"[^\{\}]*"choice"[^\{\}]*\}', acknowledgment_response)
                        if json_match:
                            acknowledgment_json = json.loads(json_match.group(0))
                        else:
                            # Fallback if regex fails
                            acknowledgment_json = {"reasoning": "Processing your IP information request", "choice": "I'll help you get information about your IP address using the IPinfo tool."}
                    except Exception as e:
                        print(f"Error parsing acknowledgment JSON: {e}")
                        acknowledgment_json = {"reasoning": "Processing your IP information request", "choice": "I'll help you get information about your IP address using the IPinfo tool."}
                    
                    # Yield the acknowledgment with both reasoning and choice
                    yield json.dumps({
                        "text": acknowledgment_json["choice"],
                        "reasoning": acknowledgment_json["reasoning"],
                        "step": {
                            "id": 1,
                            "name": "acknowledge",
                            "role": "system"
                        }
                    }) + "\n"
                    
                    # Step 2: Have the LLM explain tool selection with reasoning
                    tool_selection_prompt = f"""You are a cybersecurity assistant helping with the query: '{request.query}'
                    The IPinfo plugin has been selected to retrieve IP information.
                    
                    Explain why you're selecting the IPinfo tool for this query.
                    Your response must be in valid JSON format with two fields:
                    1. 'reasoning': Explain why the IPinfo tool is appropriate for this query
                    2. 'choice': The actual explanation to show the user
                    
                    Example response format:
                    {{"reasoning": "The user is asking about IP addresses, and IPinfo is designed to provide IP information.", "choice": "I'm selecting the IPinfo tool because it can retrieve detailed information about IP addresses."}}                    
                    """
                    
                    # Get the LLM's decision for tool selection
                    tool_selection_response = ai_service.process_query(tool_selection_prompt)["response"]
                    
                    # Extract the JSON from the response
                    try:
                        # Find JSON between curly braces
                        json_match = re.search(r'\{[^\{\}]*"reasoning"[^\{\}]*"choice"[^\{\}]*\}', tool_selection_response)
                        if json_match:
                            tool_selection_json = json.loads(json_match.group(0))
                        else:
                            # Fallback if regex fails
                            tool_selection_json = {"reasoning": "IPinfo is the appropriate tool for IP lookup", "choice": "Selecting the IPinfo tool to retrieve IP information."}
                    except Exception as e:
                        print(f"Error parsing tool selection JSON: {e}")
                        tool_selection_json = {"reasoning": "IPinfo is the appropriate tool for IP lookup", "choice": "Selecting the IPinfo tool to retrieve IP information."}
                    
                    # Yield the tool selection with both reasoning and choice
                    yield json.dumps({
                        "text": tool_selection_json["choice"],
                        "reasoning": tool_selection_json["reasoning"],
                        "step": {
                            "id": 2,
                            "name": "tool_selection",
                            "role": "system"
                        }
                    }) + "\n"
                    
                    # Step 3: Have the LLM decide which endpoint to use based on the query
                    # Load the plugin endpoints
                    endpoints = json.loads(selected_plugin.endpoints) if isinstance(selected_plugin.endpoints, str) else selected_plugin.endpoints
                    
                    # Format a prompt for the LLM to decide which endpoint to use
                    endpoint_prompt = f"""You are a cybersecurity assistant helping with the query: '{request.query}'
                    The IPinfo plugin has multiple endpoints available:
                    1. 'basic': General IP information including location, hostname, and organization
                    2. 'geo': Detailed geolocation data
                    3. 'asn': Network provider information
                    
                    Decide which endpoint is most appropriate for this query.
                    Your response must be in valid JSON format with three fields:
                    1. 'reasoning': Explain why you chose this endpoint
                    2. 'choice': A brief explanation to show the user
                    3. 'endpoint': The endpoint name (must be exactly 'basic', 'geo', or 'asn')
                    
                    Example response format:
                    {{"reasoning": "The user is asking about their location, so the geo endpoint is most appropriate.", "choice": "Based on your query about location, I'll use the 'geo' endpoint for detailed geolocation data.", "endpoint": "geo"}}                    
                    """
                    
                    # Get the LLM's decision for endpoint selection
                    endpoint_response = ai_service.process_query(endpoint_prompt)["response"]
                    
                    # Extract the JSON from the response
                    try:
                        # Find JSON between curly braces
                        json_match = re.search(r'\{[^\{\}]*"reasoning"[^\{\}]*"choice"[^\{\}]*"endpoint"[^\{\}]*\}', endpoint_response)
                        if json_match:
                            endpoint_json = json.loads(json_match.group(0))
                            endpoint = endpoint_json["endpoint"]
                            # Validate endpoint
                            if endpoint not in ["basic", "geo", "asn"]:
                                endpoint = "basic"  # Default to basic if invalid
                        else:
                            # Fallback if regex fails
                            endpoint = "basic"  # Default endpoint
                            endpoint_json = {"reasoning": "The basic endpoint provides general IP information", "choice": "Using the 'basic' endpoint to get general IP information.", "endpoint": "basic"}
                    except Exception as e:
                        print(f"Error parsing endpoint JSON: {e}")
                        endpoint = "basic"  # Default endpoint
                        endpoint_json = {"reasoning": "The basic endpoint provides general IP information", "choice": "Using the 'basic' endpoint to get general IP information.", "endpoint": "basic"}
                    
                    # Yield the endpoint selection with reasoning, choice, and the selected endpoint
                    yield json.dumps({
                        "text": endpoint_json["choice"],
                        "reasoning": endpoint_json["reasoning"],
                        "endpoint": endpoint_json["endpoint"],
                        "step": {
                            "id": 3,
                            "name": "endpoint_selection",
                            "role": "system"
                        }
                    }) + "\n"
                    
                    # Step 4: Execution notification
                    yield json.dumps({
                        "text": "Executing API call to IPinfo service...",
                        "reasoning": "Now that we've selected the appropriate endpoint, we need to execute the API call to retrieve the information",
                        "step": {
                            "id": 4,
                            "name": "execution",
                            "role": "system"
                        }
                    }) + "\n"
                    
                    # Import the IPinfo service
                    from ..services.ipinfo_service import IPInfoService
                    ipinfo_service = IPInfoService()
                    
                    # Execute the API call
                    ip_param = None  # Use the caller's IP
                    if "ip" in request.query.lower():
                        # Try to extract an IP from the query if specified
                        import re
                        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', request.query)
                        if ip_match:
                            ip_param = ip_match.group(0)
                    
                    result = ipinfo_service.get_ip_info(ip_param, endpoint)
                    
                    # Step 5: Have the LLM format and present the API result
                    if result["success"]:
                        # Create a prompt for the LLM to format the API response
                        format_prompt = f"""You are a cybersecurity assistant helping with the query: '{request.query}'
                        You've received the following data from the IPinfo {endpoint} endpoint:
                        
                        ```json
                        {json.dumps(result['data'], indent=2)}
                        ```
                        
                        Format this data in a user-friendly way with appropriate emojis and formatting.
                        Your response must be in valid JSON format with two fields:
                        1. 'reasoning': Explain how you're formatting the data to make it user-friendly
                        2. 'choice': The formatted data presentation with emojis and markdown formatting
                        
                        Example response format:
                        {{"reasoning": "I'm formatting the IP data with emojis and clear labels to make it more readable and engaging.", "choice": "I found the following information about your IP address:\n\n📍 **Location**: Washington, District of Columbia, US\n🌐 **IP Address**: 98.204.101.22\n..."}}                    
                        """
                        
                        # Get the LLM's decision for formatting the API response
                        format_response = ai_service.process_query(format_prompt)["response"]
                        
                        # Extract the JSON from the response
                        try:
                            # Find JSON between curly braces
                            json_match = re.search(r'\{[^\{\}]*"reasoning"[^\{\}]*"choice"[^\{\}]*\}', format_response)
                            if json_match:
                                format_json = json.loads(json_match.group(0))
                            else:
                                # Fallback if regex fails - create a formatted response manually
                                formatted_data = "I found the following information about your IP address:\n\n"
                                
                                if endpoint == "basic" or endpoint == "geo":
                                    formatted_data += f"📍 **Location**: {result['data'].get('city', 'Unknown')}, {result['data'].get('region', 'Unknown')}, {result['data'].get('country', 'Unknown')}\n"
                                    formatted_data += f"🌐 **IP Address**: {result['data'].get('ip', 'Unknown')}\n"
                                    if 'hostname' in result['data'] and result['data']['hostname']:
                                        formatted_data += f"🖥️ **Hostname**: {result['data'].get('hostname', 'Unknown')}\n"
                                    if 'loc' in result['data']:
                                        formatted_data += f"🗺️ **Coordinates**: {result['data'].get('loc', 'Unknown')}\n"
                                    if 'timezone' in result['data']:
                                        formatted_data += f"⏰ **Timezone**: {result['data'].get('timezone', 'Unknown')}\n"
                                    if 'postal' in result['data']:
                                        formatted_data += f"📮 **Postal Code**: {result['data'].get('postal', 'Unknown')}\n"
                                
                                if endpoint == "basic" or endpoint == "asn":
                                    formatted_data += f"🔌 **Network Provider**: {result['data'].get('org', 'Unknown')}\n"
                                    if 'asn' in result['data']:
                                        formatted_data += f"🌐 **ASN**: {result['data'].get('asn', 'Unknown')}\n"
                                        
                                format_json = {"reasoning": "Formatting the IP data with emojis and clear labels for readability", "choice": formatted_data}
                        except Exception as e:
                            print(f"Error parsing format JSON: {e}")
                            # Fallback formatting
                            formatted_data = "I found the following information about your IP address:\n\n"
                            
                            if endpoint == "basic" or endpoint == "geo":
                                formatted_data += f"📍 **Location**: {result['data'].get('city', 'Unknown')}, {result['data'].get('region', 'Unknown')}, {result['data'].get('country', 'Unknown')}\n"
                                formatted_data += f"🌐 **IP Address**: {result['data'].get('ip', 'Unknown')}\n"
                                if 'hostname' in result['data'] and result['data']['hostname']:
                                    formatted_data += f"🖥️ **Hostname**: {result['data'].get('hostname', 'Unknown')}\n"
                                if 'loc' in result['data']:
                                    formatted_data += f"🗺️ **Coordinates**: {result['data'].get('loc', 'Unknown')}\n"
                                if 'timezone' in result['data']:
                                    formatted_data += f"⏰ **Timezone**: {result['data'].get('timezone', 'Unknown')}\n"
                                if 'postal' in result['data']:
                                    formatted_data += f"📮 **Postal Code**: {result['data'].get('postal', 'Unknown')}\n"
                            
                            if endpoint == "basic" or endpoint == "asn":
                                formatted_data += f"🔌 **Network Provider**: {result['data'].get('org', 'Unknown')}\n"
                                if 'asn' in result['data']:
                                    formatted_data += f"🌐 **ASN**: {result['data'].get('asn', 'Unknown')}\n"
                                    
                            format_json = {"reasoning": "Formatting the IP data with emojis and clear labels for readability", "choice": formatted_data}
                        
                        # Yield the formatted API response with reasoning and choice
                        yield json.dumps({
                            "text": format_json["choice"],
                            "reasoning": format_json["reasoning"],
                            "step": {
                                "id": 5,
                                "name": "api_response",
                                "role": "system"
                            }
                        }) + "\n"
                        
                        # Step 6: Have the LLM provide a concise summary and analysis
                        summary_prompt = f"""You are a cybersecurity assistant helping with the query: '{request.query}'
                        You've retrieved the following data from the IPinfo {endpoint} endpoint:
                        
                        ```json
                        {json.dumps(result['data'], indent=2)}
                        ```
                        
                        Provide a concise summary and analysis of this IP information, including security implications.
                        Your response must be in valid JSON format with two fields:
                        1. 'reasoning': Explain how you're interpreting the data and what insights you're providing
                        2. 'choice': The actual summary and analysis to show the user
                        
                        Example response format:
                        {{"reasoning": "I'm summarizing the key location and ISP details while adding security context about IP visibility.", "choice": "Based on the information I gathered, here's what I can tell you:\n\nYou're currently connecting from Washington, DC with IP 98.204.101.22. Your internet is provided by Comcast. This information is visible to websites you visit."}}                    
                        """
                        
                        # Get the LLM's decision for summarizing the data
                        summary_response = ai_service.process_query(summary_prompt)["response"]
                        
                        # Extract the JSON from the response
                        try:
                            # Find JSON between curly braces
                            json_match = re.search(r'\{[^\{\}]*"reasoning"[^\{\}]*"choice"[^\{\}]*\}', summary_response)
                            if json_match:
                                summary_json = json.loads(json_match.group(0))
                            else:
                                # Fallback if regex fails - create a summary manually
                                summary = "Based on the information I gathered, here's what I can tell you:\n\n"
                                
                                if endpoint == "basic" or endpoint == "geo":
                                    ip = result["data"].get("ip", "Unknown")
                                    city = result["data"].get("city", "Unknown")
                                    region = result["data"].get("region", "Unknown")
                                    country = result["data"].get("country", "Unknown")
                                    
                                    # Add location insights
                                    summary += f"You're currently connecting from **{city}, {region}, {country}** "
                                    summary += f"with the IP address **{ip}**. "
                                    
                                    # Add timezone information if available
                                    if "timezone" in result["data"]:
                                        timezone = result["data"].get("timezone", "Unknown")
                                        summary += f"Your local timezone is **{timezone}**. "
                                        
                                if endpoint == "basic" or endpoint == "asn":
                                    # Add ISP information
                                    org = result["data"].get("org", "Unknown")
                                    
                                    # Extract the ISP name from the ASN format (e.g., "AS7922 Comcast Cable Communications, LLC")
                                    if " " in org and org.startswith("AS"):
                                        parts = org.split(" ", 1)
                                        if len(parts) > 1:
                                            asn_num = parts[0]
                                            isp_name = parts[1]
                                            summary += f"Your internet connection is provided by **{isp_name}** "
                                            summary += f"(ASN: {asn_num}). "
                                        else:
                                            summary += f"Your internet service provider is **{org}**. "
                                    else:
                                        summary += f"Your internet service provider is **{org}**. "
                                
                                # Add a security note
                                summary += "\n\nThis information is what websites can see when you connect to them. "
                                summary += "Using a VPN can help mask this information if privacy is a concern."
                                
                                summary_json = {"reasoning": "Summarizing the key location and ISP details while adding security context", "choice": summary}
                        except Exception as e:
                            print(f"Error parsing summary JSON: {e}")
                            # Fallback summary
                            summary = "Based on the information I gathered, here's what I can tell you:\n\n"
                            
                            if endpoint == "basic" or endpoint == "geo":
                                ip = result["data"].get("ip", "Unknown")
                                city = result["data"].get("city", "Unknown")
                                region = result["data"].get("region", "Unknown")
                                country = result["data"].get("country", "Unknown")
                                
                                # Add location insights
                                summary += f"You're currently connecting from **{city}, {region}, {country}** "
                                summary += f"with the IP address **{ip}**. "
                                
                                # Add timezone information if available
                                if "timezone" in result["data"]:
                                    timezone = result["data"].get("timezone", "Unknown")
                                    summary += f"Your local timezone is **{timezone}**. "
                                    
                            if endpoint == "basic" or endpoint == "asn":
                                # Add ISP information
                                org = result["data"].get("org", "Unknown")
                                
                                # Extract the ISP name from the ASN format (e.g., "AS7922 Comcast Cable Communications, LLC")
                                if " " in org and org.startswith("AS"):
                                    parts = org.split(" ", 1)
                                    if len(parts) > 1:
                                        asn_num = parts[0]
                                        isp_name = parts[1]
                                        summary += f"Your internet connection is provided by **{isp_name}** "
                                        summary += f"(ASN: {asn_num}). "
                                    else:
                                        summary += f"Your internet service provider is **{org}**. "
                                else:
                                    summary += f"Your internet service provider is **{org}**. "
                            
                            # Add a security note
                            summary += "\n\nThis information is what websites can see when you connect to them. "
                            summary += "Using a VPN can help mask this information if privacy is a concern."
                            
                            summary_json = {"reasoning": "Summarizing the key location and ISP details while adding security context", "choice": summary}
                        
                        # Yield the summary with reasoning and choice
                        yield json.dumps({
                            "text": summary_json["choice"],
                            "reasoning": summary_json["reasoning"],
                            "step": {
                                "id": 6,
                                "name": "summary",
                                "role": "assistant"
                            }
                        }) + "\n"
                        
                        # Return early since we've handled the response
                        return
                    else:
                        # Handle error case with reasoning
                        error_message = f"Failed to get IP information from the {endpoint} endpoint: {result['message']}"
                        yield json.dumps({
                            "text": error_message,
                            "reasoning": "The API call to IPinfo failed, so I need to inform the user about the error",
                            "step": {
                                "id": 5,
                                "name": "error",
                                "role": "system"
                            }
                        }) + "\n"
                        return
            
            # Format messages for MLX-LM
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": request.query}
            ]
            
            print("Applying chat template")
            # Apply chat template
            try:
                prompt = ai_service.tokenizer.apply_chat_template(
                    messages, 
                    add_generation_prompt=True
                )
                print("Chat template applied successfully")
            except Exception as e:
                print(f"Error applying chat template: {str(e)}")
                yield json.dumps({"error": f"Error applying chat template: {str(e)}"}) + "\n"
                return
            
            # Stream the response
            if ai_service.USE_MLX:
                from mlx_lm import stream_generate
                
                for response in stream_generate(
                    ai_service.model,
                    ai_service.tokenizer,
                    prompt=prompt,
                    max_tokens=ai_service.max_tokens,
                    temperature=ai_service.temperature
                ):
                    # Yield each chunk as a JSON object
                    yield json.dumps({"text": response.text}) + "\n"
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)
            else:
                # Mock streaming response for demo
                print("Using mock implementation for streaming")
                cybersecurity_responses = [
                    "The most common cybersecurity threats include phishing attacks, malware, ransomware, and social engineering. To protect yourself, use strong passwords, enable two-factor authentication, keep software updated, and be cautious of suspicious emails and links.",
                    "Zero-day vulnerabilities are security flaws that are unknown to the software vendor and don't have patches available. They're particularly dangerous because attackers can exploit them before developers can create and distribute a fix.",
                    "To secure your home network, change default router passwords, use WPA3 encryption if available, create a guest network for visitors, keep firmware updated, and consider using a VPN for additional privacy.",
                    "Ransomware is malicious software that encrypts your files and demands payment for the decryption key. The best protection is maintaining regular backups, using security software, keeping systems updated, and training users to recognize phishing attempts.",
                    "Multi-factor authentication (MFA) adds an essential layer of security by requiring multiple forms of verification before granting access. Even if your password is compromised, attackers would still need access to your secondary authentication method."
                ]
                
                # Simple response for "hi" or greetings
                if request.query.lower() in ["hi", "hello", "hey"]:
                    response_text = "Hello! I'm your cybersecurity assistant. How can I help you with your cybersecurity questions today?"
                else:
                    response_text = random.choice(cybersecurity_responses)
                    
                print(f"Selected response: {response_text[:30]}...")
                
                # Stream the response word by word to simulate real-time generation
                words = response_text.split()
                for i, word in enumerate(words):
                    # Add a space before each word except the first one
                    prefix = " " if i > 0 else ""
                    yield json.dumps({"text": prefix + word}) + "\n"
                    # Add random delay to simulate thinking
                    await asyncio.sleep(0.05)
                
        except Exception as e:
            # Log and yield error message
            error_message = f"Error in stream generation: {str(e)}"
            print(error_message)
            yield json.dumps({"error": error_message}) + "\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="application/x-ndjson"
    )

@router.post("/recommend-plugins", response_model=List[PluginRecommendation])
def recommend_plugins(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Recommend plugins that might be helpful for a given query
    """
    # Get all available plugins
    plugins = db.query(Plugin).all()
    
    # Get plugin recommendations
    recommendations = ai_service.get_plugin_recommendations(
        query=request.query,
        plugins=plugins
    )
    
    return recommendations
