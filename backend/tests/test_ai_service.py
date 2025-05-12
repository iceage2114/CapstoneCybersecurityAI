import unittest
import os
from unittest.mock import patch, MagicMock
import sys
import json
from dotenv import load_dotenv

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Mock the requests module before importing AIService
mock_response = MagicMock()
mock_response.status_code = 200
mock_response.json.return_value = {"models": [{"name": "llama2"}]}

with patch('requests.get', return_value=mock_response), \
     patch('requests.post', return_value=mock_response):
    from app.services.ai_service import AIService
    from app.models.plugin_model import Plugin

class TestAIService(unittest.TestCase):
    """Test cases for the AI Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create patch for requests.get
        self.get_patcher = patch('requests.get')
        self.mock_get = self.get_patcher.start()
        self.mock_get.return_value.status_code = 200
        self.mock_get.return_value.json.return_value = {"models": [{"name": "llama2"}]}
        
        # Create patch for requests.post
        self.post_patcher = patch('requests.post')
        self.mock_post = self.post_patcher.start()
        self.mock_post.return_value.status_code = 200
        
        # Initialize the service with mocks
        self.ai_service = AIService()
    
    def tearDown(self):
        """Clean up after tests"""
        self.get_patcher.stop()
        self.post_patcher.stop()
    
    def test_init(self):
        """Test initialization of AIService"""
        self.assertEqual(self.ai_service.ollama_host, os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        self.assertEqual(self.ai_service.model, os.getenv("OLLAMA_MODEL", "llama2"))
        
        # Verify that requests.get was called to check available models
        self.mock_get.assert_called_once_with(f"{self.ai_service.ollama_host}/api/tags")
    
    def test_process_query(self):
        """Test process_query with mocked Ollama API"""
        # Set up the mock response for the Ollama API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "This is a mocked response about cybersecurity."
            }
        }
        self.mock_post.return_value = mock_response
        
        query = "What is a common cybersecurity threat?"
        result = self.ai_service.process_query(query=query)
        
        # Check that we got the expected mocked response
        self.assertEqual(result["response"], "This is a mocked response about cybersecurity.")
        self.assertIsNone(result["plugin_used"])
        
        # Verify that requests.post was called with the correct arguments
        self.mock_post.assert_called_once()
        call_args, call_kwargs = self.mock_post.call_args
        self.assertEqual(call_args[0], f"{self.ai_service.ollama_host}/api/chat")
        payload = call_kwargs["json"]
        self.assertEqual(payload["model"], self.ai_service.model)
        self.assertEqual(len(payload["messages"]), 2)  # System message and user message
        self.assertEqual(payload["messages"][1]["content"], query)
    
    def test_process_query_with_plugin(self):
        """Test process_query with a plugin"""
        # Create a mock plugin
        mock_plugin = MagicMock(spec=Plugin)
        mock_plugin.id = 1
        mock_plugin.name = "Vulnerability Scanner"
        mock_plugin.description = "Scans for vulnerabilities in systems"
        mock_plugin.api_endpoint = "https://example.com/api/scan"
        mock_plugin.parameters = json.dumps({"target": "string", "scan_type": "string"})
        
        # Create a mock DB session
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_plugin
        
        # Set up the mock response for the Ollama API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "Response with plugin context."
            }
        }
        self.mock_post.return_value = mock_response
        
        query = "Scan my system for vulnerabilities"
        result = self.ai_service.process_query(query=query, plugin_id=1, db=mock_db)
        
        # Check that we got the expected response with plugin information
        self.assertEqual(result["response"], "Response with plugin context.")
        self.assertEqual(result["plugin_used"], "Vulnerability Scanner")
        
        # Verify that requests.post was called with the correct arguments
        self.mock_post.assert_called_once()
        call_args, call_kwargs = self.mock_post.call_args
        self.assertEqual(call_args[0], f"{self.ai_service.ollama_host}/api/chat")
        
        # Check that the plugin context was included in the system prompt
        payload = call_kwargs["json"]
        system_content = payload["messages"][0]["content"]
        self.assertIn("Vulnerability Scanner", system_content)
        self.assertIn("Scans for vulnerabilities in systems", system_content)
    
    def test_get_plugin_recommendations(self):
        """Test get_plugin_recommendations method"""
        # Create mock plugins with proper attribute access
        plugin1 = MagicMock(spec=Plugin)
        plugin1.id = 1
        plugin1.name = "Vulnerability Scanner"
        plugin1.description = "Scans for vulnerabilities"
        
        plugin2 = MagicMock(spec=Plugin)
        plugin2.id = 2
        plugin2.name = "Password Checker"
        plugin2.description = "Checks password strength"
        
        plugins = [plugin1, plugin2]
        
        # Set up the mock response for the Ollama API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "role": "assistant",
                "content": '[{"id": 1, "relevance_score": 8}, {"id": 2, "relevance_score": 3}]'
            }
        }
        self.mock_post.return_value = mock_response
        
        query = "How do I scan for vulnerabilities?"
        recommendations = self.ai_service.get_plugin_recommendations(query=query, plugins=plugins)
        
        # Check that we got the expected recommendations
        self.assertEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0]["id"], 1)
        self.assertEqual(recommendations[0]["name"], "Vulnerability Scanner")
        self.assertEqual(recommendations[0]["relevance_score"], 8)
        
        # Verify that requests.post was called with the correct arguments
        self.mock_post.assert_called_once()
        call_args, call_kwargs = self.mock_post.call_args
        self.assertEqual(call_args[0], f"{self.ai_service.ollama_host}/api/chat")
        
        # Check that the request payload was properly formatted
        payload = call_kwargs["json"]
        self.assertEqual(payload["model"], self.ai_service.model)
        self.assertEqual(len(payload["messages"]), 2)  # System message and user message
        self.assertIn("cybersecurity tool recommendation system", payload["messages"][0]["content"])
        self.assertIn("Vulnerability Scanner", payload["messages"][1]["content"])

if __name__ == "__main__":
    unittest.main()
