from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class ConversationService:
    """Service for managing conversation history and context"""
    
    def __init__(self):
        """Initialize the conversation service"""
        pass
    
    def format_conversation_for_llm(self, conversation_history: List[Dict[str, Any]], 
                                   system_prompt: str = None) -> List[Dict[str, str]]:
        """
        Format conversation history for LLM input
        
        Args:
            conversation_history: List of conversation messages
            system_prompt: Optional system prompt to include
            
        Returns:
            List of formatted messages for LLM
        """
        formatted_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add conversation history
        for message in conversation_history:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })
        
        return formatted_messages
    
    def add_context_from_plugin(self, messages: List[Dict[str, str]], 
                              plugin_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Add plugin context to conversation messages
        
        Args:
            messages: List of formatted messages for LLM
            plugin_info: Information about the plugin
            
        Returns:
            Updated list of messages with plugin context
        """
        # Create plugin context message
        plugin_context = f"""
        You have access to the following cybersecurity tool/API:
        Name: {plugin_info['name']}
        Description: {plugin_info['description']}
        API Endpoint: {plugin_info['api_endpoint']}
        
        When appropriate, suggest how this tool could be used to address the user's query.
        """
        
        # Find system message to append context
        for i, message in enumerate(messages):
            if message["role"] == "system":
                # Append to existing system message
                messages[i]["content"] += "\n\n" + plugin_context
                return messages
        
        # If no system message found, add new one
        messages.insert(0, {
            "role": "system",
            "content": plugin_context
        })
        
        return messages
    
    def extract_plugin_recommendations(self, llm_response: str) -> List[Dict[str, Any]]:
        """
        Extract plugin recommendations from LLM response
        
        Args:
            llm_response: Response from LLM
            
        Returns:
            List of plugin recommendations
        """
        try:
            # Try to find JSON array in response
            import re
            json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group(0))
                return recommendations
        except Exception as e:
            print(f"Error extracting plugin recommendations: {str(e)}")
        
        return []
