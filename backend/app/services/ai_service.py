import os
import json
import logging
import time
import requests
import random
from typing import List, Dict, Any, Optional, Iterator, Union
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from ..models.plugin_model import Plugin

# Try to import MLX libraries, but provide fallbacks if not available
USE_MLX = False
try:
    import mlx.core as mx
    from mlx_lm import load, generate, stream_generate
    USE_MLX = True
except ImportError:
    logging.warning("MLX libraries not available. Using mock implementation for demo.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIService:
    """Service for handling AI interactions with Apple's MLX framework"""
    
    def __init__(self):
        # Get configuration from environment variables
        self.model_repo = os.getenv("MLX_MODEL_REPO", "mlx-community/Mistral-7B-Instruct-v0.3-4bit")
        self.max_tokens = int(os.getenv("MLX_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("MLX_TEMPERATURE", "0.7"))
        
        # Initialize model and tokenizer to None (lazy loading)
        self.model = None
        self.tokenizer = None
        
        # Add USE_MLX as an instance attribute
        self.USE_MLX = USE_MLX
        
        logger.info(f"AI Service initialized with MLX model: {self.model_repo}")
        logger.info(f"Max tokens: {self.max_tokens}, Temperature: {self.temperature}")
    
    def _load_model(self) -> None:
        """
        Load the model and tokenizer if not already loaded
        """
        if self.model is None or self.tokenizer is None:
            try:
                logger.info(f"Loading model from {self.model_repo}...")
                start_time = time.time()
                
                if USE_MLX:
                    self.model, self.tokenizer = load(self.model_repo)
                    load_time = time.time() - start_time
                    logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
                else:
                    # Mock implementation for demo
                    logger.info("Using mock implementation for demo")
                    self.model = "mock_model"
                    self.tokenizer = type('MockTokenizer', (), {
                        'apply_chat_template': lambda self, messages, add_generation_prompt=False: 
                            "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                    })()
                    time.sleep(1)  # Simulate loading time
                    load_time = time.time() - start_time
                    logger.info(f"Mock model loaded in {load_time:.2f} seconds")
            except Exception as e:
                error_msg = f"Error loading model {self.model_repo}: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
    
    def process_query(self, query: str, plugin_id: Optional[int] = None, db: Session = None) -> Dict[str, Any]:
        """
        Process a user query with the selected plugin using MLX
        
        Args:
            query: The user's cybersecurity question
            plugin_id: Optional ID of the plugin to use
            db: Database session
            
        Returns:
            Dict containing the AI response
        """
        return self._generate_response(query=query, plugin_id=plugin_id, db=db)
    
    def process_query_with_history(self, query: str, conversation_history: List[Dict[str, str]], 
                                  plugin_id: Optional[int] = None, db: Session = None) -> Dict[str, Any]:
        """
        Process a user query with conversation history and selected plugin using MLX
        
        Args:
            query: The user's cybersecurity question
            conversation_history: List of previous messages in the conversation
            plugin_id: Optional ID of the plugin to use
            db: Database session
            
        Returns:
            Dict containing the AI response
        """
        return self._generate_response(query=query, conversation_history=conversation_history, 
                                     plugin_id=plugin_id, db=db)
    
    def _generate_response(self, query: str, conversation_history: List[Dict[str, str]] = None,
                         plugin_id: Optional[int] = None, db: Session = None) -> Dict[str, Any]:
        """
        Internal method to generate a response with or without conversation history
        
        Args:
            query: The user's cybersecurity question
            conversation_history: Optional list of previous messages in the conversation
            plugin_id: Optional ID of the plugin to use
            db: Database session
            
        Returns:
            Dict containing the AI response
        """
        try:
            # Ensure model is loaded
            self._load_model()
            
            # If a plugin is specified, get its details
            plugin_context = None
            if plugin_id and db:
                plugin = db.query(Plugin).filter(Plugin.id == plugin_id).first()
                if plugin:
                    plugin_context = {
                        "name": plugin.name,
                        "description": plugin.description,
                        "api_endpoint": plugin.api_endpoint,
                        "parameters": json.loads(plugin.parameters) if isinstance(plugin.parameters, str) else plugin.parameters
                    }
            
            # Create system prompt with cybersecurity focus
            system_content = "You are a cybersecurity analyst assistant. Your goal is to provide accurate, helpful information about cybersecurity topics."
            
            # Add plugin context if available
            if plugin_context:
                plugin_prompt = f"""
                You have access to the following cybersecurity tool/API:
                Name: {plugin_context['name']}
                Description: {plugin_context['description']}
                API Endpoint: {plugin_context['api_endpoint']}
                
                When appropriate, suggest how this tool could be used to address the user's query.
                """
                system_content += "\n\n" + plugin_prompt
            
            # Format messages for MLX-LM
            if conversation_history:
                # Start with system message
                messages = [{"role": "system", "content": system_content}]
                
                # Add conversation history
                messages.extend(conversation_history)
                
                # Add current query as user message if not already included
                if not (conversation_history and conversation_history[-1]["role"] == "user" and conversation_history[-1]["content"] == query):
                    messages.append({"role": "user", "content": query})
            else:
                # Simple query without history
                messages = [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": query}
                ]
            
            # Apply chat template to format the prompt correctly for the model
            prompt = self.tokenizer.apply_chat_template(
                messages, 
                add_generation_prompt=True
            )
            
            logger.info(f"Generating response for query: {query[:50]}...")
            start_time = time.time()
            
            # Generate the response
            if USE_MLX:
                # Generate the response using MLX
                response_text = generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    verbose=False
                )
            else:
                # Mock response generation for demo
                cybersecurity_responses = [
                    "The most common cybersecurity threats include phishing attacks, malware, ransomware, and social engineering. To protect yourself, use strong passwords, enable two-factor authentication, keep software updated, and be cautious of suspicious emails and links.",
                    "Zero-day vulnerabilities are security flaws that are unknown to the software vendor and don't have patches available. They're particularly dangerous because attackers can exploit them before developers can create and distribute a fix.",
                    "To secure your home network, change default router passwords, use WPA3 encryption if available, create a guest network for visitors, keep firmware updated, and consider using a VPN for additional privacy.",
                    "Ransomware is malicious software that encrypts your files and demands payment for the decryption key. The best protection is maintaining regular backups, using security software, keeping systems updated, and training users to recognize phishing attempts.",
                    "Multi-factor authentication (MFA) adds an essential layer of security by requiring multiple forms of verification before granting access. Even if your password is compromised, attackers would still need access to your secondary authentication method."
                ]
                response_text = random.choice(cybersecurity_responses)
                # Simulate generation time
                time.sleep(2)
            
            generation_time = time.time() - start_time
            logger.info(f"Response generated in {generation_time:.2f} seconds")
            
            # Return the complete response
            return {
                "response": response_text,
                "plugin_used": plugin_context["name"] if plugin_context else None,
                "metadata": {
                    "generation_time": generation_time,
                    "model": self.model_repo,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            }
            
        except Exception as e:
            error_msg = f"Error generating response with MLX: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def get_plugin_recommendations(self, query: str, plugins: List[Plugin]) -> List[Dict[str, Any]]:
        """
        Recommend plugins that might be helpful for a given query using MLX
        
        Args:
            query: The user's cybersecurity question
            plugins: List of available plugins
            
        Returns:
            List of recommended plugins with relevance scores
        """
        if not plugins:
            return []
        
        try:
            # Ensure model is loaded
            self._load_model()
            
            # Create system prompt
            system_content = "You are a cybersecurity tool recommendation system. Your task is to rank the relevance of tools for a user query."
            
            # Format plugins information
            plugins_info = "\n".join([
                f"{i+1}. {plugin.name}: {plugin.description}" 
                for i, plugin in enumerate(plugins)
            ])
            
            # Create user message with query and plugins
            user_content = f"""
            User Query: {query}
            
            Available Tools:
            {plugins_info}
            
            Rank the tools by relevance to the query. Return a JSON array with objects containing 'id' and 'relevance_score' (0-10).
            Example: [{{'id': 1, 'relevance_score': 8}}, {{'id': 2, 'relevance_score': 3}}]
            
            IMPORTANT: Your response must contain only the JSON array and nothing else.
            """
            
            # Format messages for MLX-LM
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
            
            # Apply chat template to format the prompt correctly for the model
            prompt = self.tokenizer.apply_chat_template(
                messages, 
                add_generation_prompt=True
            )
            
            logger.info(f"Generating plugin recommendations for query: {query[:50]}...")
            start_time = time.time()
            
            # Generate the response
            if USE_MLX:
                # Generate the response using MLX with lower temperature for more deterministic output
                response_text = generate(
                    self.model,
                    self.tokenizer,
                    prompt=prompt,
                    max_tokens=500,  # Shorter response for recommendations
                    temperature=0.3,  # Lower temperature for more deterministic output
                    verbose=False
                )
            else:
                # Mock plugin recommendations for demo
                response_text = json.dumps([{"id": 1, "relevance_score": 8}, {"id": 2, "relevance_score": 5}])
            
            generation_time = time.time() - start_time
            logger.info(f"Recommendations generated in {generation_time:.2f} seconds")
            
            # Find JSON array in response
            import re
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                try:
                    recommendations = json.loads(json_match.group(0))
                    
                    # Map plugin IDs to actual plugins
                    result = []
                    for rec in recommendations:
                        plugin_id = rec.get("id")
                        if 1 <= plugin_id <= len(plugins):
                            plugin = plugins[plugin_id - 1]
                            result.append({
                                "id": plugin.id,
                                "name": plugin.name,
                                "description": plugin.description,
                                "relevance_score": rec.get("relevance_score", 0)
                            })
                    
                    # Sort by relevance score (descending)
                    return sorted(result, key=lambda x: x["relevance_score"], reverse=True)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON from model response: {e}")
                    return []
            else:
                logger.warning(f"No valid JSON array found in response: {response_text[:100]}...")
                return []
            
        except Exception as e:
            logger.error(f"Error in plugin recommendations: {str(e)}")
            return []
