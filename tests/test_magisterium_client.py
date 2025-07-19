#!/usr/bin/env python3

import unittest
import json
import os
from unittest.mock import patch, Mock, MagicMock
import sys
import io

# Add the parent directory to the path so we can import our module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from magisterium_client import (
    create_safety_settings,
    create_chat_request, 
    create_headers,
    parse_api_error,
    MagisteriumAPIError,
    parse_arguments,
    get_api_key
)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions that don't require API calls."""
    
    def test_create_safety_settings_default(self):
        """Test create_safety_settings with default values."""
        result = create_safety_settings()
        expected = {
            "CATEGORY_NON_CATHOLIC": {
                "threshold": "BLOCK_ALL",
                "response": True
            }
        }
        self.assertEqual(result, expected)
    
    def test_create_safety_settings_custom(self):
        """Test create_safety_settings with custom values."""
        result = create_safety_settings(
            non_catholic_threshold="OFF",
            non_catholic_response=False
        )
        expected = {
            "CATEGORY_NON_CATHOLIC": {
                "threshold": "OFF",
                "response": False
            }
        }
        self.assertEqual(result, expected)
    
    def test_create_safety_settings_invalid_threshold(self):
        """Test create_safety_settings with invalid threshold."""
        with self.assertRaises(ValueError) as context:
            create_safety_settings(non_catholic_threshold="INVALID")
        
        self.assertIn("Invalid threshold 'INVALID'", str(context.exception))
        self.assertIn("Must be one of: ['BLOCK_ALL', 'OFF']", str(context.exception))
    
    def test_create_chat_request_basic(self):
        """Test create_chat_request with basic parameters."""
        result = create_chat_request("Hello world")
        expected = {
            "model": "magisterium-1",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello world"
                }
            ],
            "stream": False
        }
        self.assertEqual(result, expected)
    
    def test_create_chat_request_with_model(self):
        """Test create_chat_request with custom model."""
        result = create_chat_request("Hello", model="custom-model")
        self.assertEqual(result["model"], "custom-model")
        self.assertEqual(result["messages"][0]["content"], "Hello")
    
    def test_create_chat_request_with_related_questions(self):
        """Test create_chat_request with related questions enabled."""
        result = create_chat_request("Hello", return_related_questions=True)
        self.assertTrue(result["return_related_questions"])
        self.assertIn("return_related_questions", result)
    
    def test_create_chat_request_without_related_questions(self):
        """Test create_chat_request with related questions disabled."""
        result = create_chat_request("Hello", return_related_questions=False)
        self.assertNotIn("return_related_questions", result)
    
    def test_create_chat_request_with_safety_settings(self):
        """Test create_chat_request with safety settings."""
        safety_settings = create_safety_settings("OFF", False)
        result = create_chat_request("Hello", safety_settings=safety_settings)
        self.assertEqual(result["safety_settings"], safety_settings)
    
    def test_create_chat_request_without_safety_settings(self):
        """Test create_chat_request without safety settings."""
        result = create_chat_request("Hello")
        self.assertNotIn("safety_settings", result)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and parsing functions."""
    
    def test_parse_api_error_400_token_limit(self):
        """Test parsing 400 error for token limit exceeded."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Token limit exceeded"}
        
        result = parse_api_error(mock_response)
        expected = "Token limit exceeded. Your request is too long. Please shorten your message and try again."
        self.assertEqual(result, expected)
    
    def test_parse_api_error_400_general(self):
        """Test parsing general 400 error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Invalid request format"}
        
        result = parse_api_error(mock_response)
        self.assertEqual(result, "Bad request: Invalid request format")
    
    def test_parse_api_error_401_incorrect_key(self):
        """Test parsing 401 error for incorrect API key."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Incorrect API key provided"}
        
        result = parse_api_error(mock_response)
        expected = "Incorrect API key provided. Please check your MAGISTERIUM_API_KEY environment variable."
        self.assertEqual(result, expected)
    
    def test_parse_api_error_401_invalid_billing(self):
        """Test parsing 401 error for invalid billing."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid billing"}
        
        result = parse_api_error(mock_response)
        expected = "Invalid billing setup. Please check your billing configuration in your account dashboard."
        self.assertEqual(result, expected)
    
    def test_parse_api_error_401_tier_not_found(self):
        """Test parsing 401 error for tier not found."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Tier not found"}
        
        result = parse_api_error(mock_response)
        expected = "Invalid service tier. Please contact Magisterium support for assistance."
        self.assertEqual(result, expected)
    
    def test_parse_api_error_401_general(self):
        """Test parsing general 401 error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Unauthorized"}
        
        result = parse_api_error(mock_response)
        self.assertIn("Authentication error: Unauthorized", result)
        self.assertIn("Please check your API key", result)
    
    def test_parse_api_error_429_rate_limit(self):
        """Test parsing 429 rate limit error."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Too many requests"}
        
        result = parse_api_error(mock_response)
        expected = "Rate limit exceeded. You are making too many requests. Please wait and try again, or upgrade your plan."
        self.assertEqual(result, expected)
    
    def test_parse_api_error_500_server_error(self):
        """Test parsing 500 server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        
        result = parse_api_error(mock_response)
        expected = "Internal server error. This is an issue on Magisterium's end. Please try again later or contact support."
        self.assertEqual(result, expected)
    
    def test_parse_api_error_invalid_json(self):
        """Test parsing error when response is not valid JSON."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_response.text = "Bad Request"
        
        result = parse_api_error(mock_response)
        self.assertEqual(result, "Bad request: Bad Request")
    
    def test_magisterium_api_error_creation(self):
        """Test MagisteriumAPIError custom exception."""
        error = MagisteriumAPIError("Test error", status_code=401, error_code="AUTH_ERROR")
        
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.error_code, "AUTH_ERROR")


class TestAPIKeyHandling(unittest.TestCase):
    """Test API key retrieval and header creation."""
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    def test_get_api_key_success(self):
        """Test successful API key retrieval."""
        result = get_api_key()
        self.assertEqual(result, 'test_key_12345')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_missing(self):
        """Test API key retrieval when not set."""
        with self.assertRaises(ValueError) as context:
            get_api_key()
        
        self.assertEqual(str(context.exception), "MAGISTERIUM_API_KEY environment variable not set")
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    def test_create_headers_default(self):
        """Test header creation with default user agent."""
        result = create_headers()
        expected = {
            "Authorization": "Bearer test_key_12345",
            "Content-Type": "application/json",
            "User-Agent": "magisterium-client/1.0"
        }
        self.assertEqual(result, expected)
    
    @patch.dict(os.environ, {'MAGISTERIUM_API_KEY': 'test_key_12345'})
    def test_create_headers_custom_user_agent(self):
        """Test header creation with custom user agent."""
        result = create_headers("MyClient/2.0")
        self.assertEqual(result["User-Agent"], "MyClient/2.0")
        self.assertEqual(result["Authorization"], "Bearer test_key_12345")


class TestArgumentParsing(unittest.TestCase):
    """Test command-line argument parsing."""
    
    def test_parse_arguments_defaults(self):
        """Test argument parsing with defaults."""
        # Mock sys.argv to simulate command line arguments
        test_args = ['magisterium_client.py']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            
            self.assertEqual(args.message, "What is the Magisterium?")
            self.assertEqual(args.model, "magisterium-1")
            self.assertEqual(args.timeout, 30)
            self.assertFalse(args.related_questions)
            self.assertEqual(args.non_catholic_threshold, "BLOCK_ALL")
            self.assertFalse(args.no_fallback_response)
    
    def test_parse_arguments_custom_message(self):
        """Test argument parsing with custom message."""
        test_args = ['magisterium_client.py', 'Custom message']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertEqual(args.message, "Custom message")
    
    def test_parse_arguments_related_questions(self):
        """Test argument parsing with related questions flag."""
        test_args = ['magisterium_client.py', '--related-questions']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertTrue(args.related_questions)
    
    def test_parse_arguments_safety_settings(self):
        """Test argument parsing with safety settings."""
        test_args = ['magisterium_client.py', '--non-catholic-threshold', 'OFF', '--no-fallback-response']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertEqual(args.non_catholic_threshold, "OFF")
            self.assertTrue(args.no_fallback_response)
    
    def test_parse_arguments_security_options(self):
        """Test argument parsing with security options."""
        test_args = ['magisterium_client.py', '--insecure', '--burp']
        with patch('sys.argv', test_args):
            args = parse_arguments()
            self.assertTrue(args.insecure)
            self.assertTrue(args.burp)


if __name__ == '__main__':
    # Run the tests with verbose output
    unittest.main(verbosity=2)