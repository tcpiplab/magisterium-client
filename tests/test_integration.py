#!/usr/bin/env python3

import unittest
import json
import os
from unittest.mock import patch, Mock, MagicMock
import sys
import requests

# Add the parent directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from magisterium_client import (
    make_chat_request,
    MagisteriumAPIError
)


class TestIntegration(unittest.TestCase):
    """Test integration scenarios with mocked API calls."""
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_success(self, mock_post):
        """Test successful API call with all features."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "The Trinity is..."
                    }
                }
            ],
            "related_questions": [
                "What is the Holy Spirit?",
                "How does the Trinity relate to salvation?"
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Make the request
        result = make_chat_request(
            message="What is the Trinity?",
            return_related_questions=True,
            safety_settings={"CATEGORY_NON_CATHOLIC": {"threshold": "OFF", "response": True}}
        )
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Check URL
        self.assertEqual(call_args[1]['json']['messages'][0]['content'], "What is the Trinity?")
        self.assertTrue(call_args[1]['json']['return_related_questions'])
        self.assertIn('safety_settings', call_args[1]['json'])
        
        # Check headers
        headers = call_args[1]['headers']
        self.assertEqual(headers['Authorization'], 'Bearer test_key_12345')
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(headers['User-Agent'], 'magisterium-client/1.0')
        
        # Check response
        self.assertIn('choices', result)
        self.assertIn('related_questions', result)
        self.assertEqual(len(result['related_questions']), 2)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_timeout(self, mock_post):
        """Test timeout handling."""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with self.assertRaises(MagisteriumAPIError) as context:
            make_chat_request("Hello", timeout=1)
        
        error_message = str(context.exception)
        self.assertIn("Request timed out after 1 seconds", error_message)
        self.assertIn("Please try again or increase the timeout value", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_connection_error(self, mock_post):
        """Test connection error handling."""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with self.assertRaises(MagisteriumAPIError) as context:
            make_chat_request("Hello")
        
        error_message = str(context.exception)
        self.assertIn("Failed to connect to API endpoint", error_message)
        self.assertIn("Please check your internet connection and the API URL", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'invalid_key'})
    @patch('requests.post')
    def test_make_chat_request_401_error(self, mock_post):
        """Test 401 authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Incorrect API key provided"}
        
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_post.side_effect = http_error
        
        with self.assertRaises(MagisteriumAPIError) as context:
            make_chat_request("Hello")
        
        error_message = str(context.exception)
        self.assertIn("Incorrect API key provided", error_message)
        self.assertIn("Please check your MAGISTERIUM_API_KEY environment variable", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_429_rate_limit(self, mock_post):
        """Test 429 rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Too many requests"}
        
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_post.side_effect = http_error
        
        with self.assertRaises(MagisteriumAPIError) as context:
            make_chat_request("Hello")
        
        error_message = str(context.exception)
        self.assertIn("Rate limit exceeded", error_message)
        self.assertIn("Please wait and try again, or upgrade your plan", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_500_server_error(self, mock_post):
        """Test 500 server error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_post.side_effect = http_error
        
        with self.assertRaises(MagisteriumAPIError) as context:
            make_chat_request("Hello")
        
        error_message = str(context.exception)
        self.assertIn("Internal server error", error_message)
        self.assertIn("This is an issue on Magisterium's end", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_invalid_json_response(self, mock_post):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            make_chat_request("Hello")
        
        error_message = str(context.exception)
        self.assertIn("Received invalid JSON response from API", error_message)
        self.assertIn("The service may be temporarily unavailable", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_invalid_response_format(self, mock_post):
        """Test handling of response missing required fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}  # Missing choices
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            make_chat_request("Hello")
        
        error_message = str(context.exception)
        self.assertIn("Invalid response format: missing choices", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_missing_message(self, mock_post):
        """Test handling of response missing message in choice."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"invalid": "choice"}  # Missing message
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        with self.assertRaises(ValueError) as context:
            make_chat_request("Hello")
        
        error_message = str(context.exception)
        self.assertIn("Invalid response format: missing message in choice", error_message)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    @patch('requests.post')
    def test_make_chat_request_custom_parameters(self, mock_post):
        """Test request with all custom parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "Response"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test with all custom parameters
        make_chat_request(
            message="Custom message",
            url="https://custom.api.com/v1/chat",
            user_agent="CustomClient/2.0",
            verify_ssl=False,
            proxies={"http": "http://proxy:8080"},
            timeout=60,
            model="custom-model",
            return_related_questions=True,
            safety_settings={"CATEGORY_NON_CATHOLIC": {"threshold": "OFF", "response": False}}
        )
        
        # Verify all parameters were passed correctly
        call_args = mock_post.call_args
        
        # Check URL
        self.assertEqual(call_args[0][0], "https://custom.api.com/v1/chat")
        
        # Check request data
        request_data = call_args[1]['json']
        self.assertEqual(request_data['model'], 'custom-model')
        self.assertEqual(request_data['messages'][0]['content'], 'Custom message')
        self.assertTrue(request_data['return_related_questions'])
        self.assertIn('safety_settings', request_data)
        
        # Check headers
        headers = call_args[1]['headers']
        self.assertEqual(headers['User-Agent'], 'CustomClient/2.0')
        
        # Check other parameters
        self.assertEqual(call_args[1]['verify'], False)
        self.assertEqual(call_args[1]['proxies'], {"http": "http://proxy:8080"})
        self.assertEqual(call_args[1]['timeout'], 60)


if __name__ == '__main__':
    # Run the tests with verbose output
    unittest.main(verbosity=2)