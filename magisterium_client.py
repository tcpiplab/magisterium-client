#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib3
from typing import Dict, Optional, Any

import requests


class MagisteriumAPIError(requests.RequestException):
    """Custom exception for Magisterium API errors with detailed error information."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


def get_api_key() -> str:
    """
    Retrieve the Magisterium API key from environment variables.
    
    Returns:
        str: The API key
        
    Raises:
        ValueError: If the API key is not found in environment variables
    """
    api_key = os.getenv("MAGISTERIUM_API_KEY")
    if not api_key:
        raise ValueError("MAGISTERIUM_API_KEY environment variable not set")
    return api_key


def create_headers(user_agent: str = "magisterium-client/1.0") -> Dict[str, str]:
    """
    Create HTTP headers for API requests.
    
    Args:
        user_agent: Custom User-Agent string
        
    Returns:
        Dict containing HTTP headers
        
    Raises:
        ValueError: If API key cannot be retrieved
    """
    api_key = get_api_key()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": user_agent
    }


def create_safety_settings(
    non_catholic_threshold: str = "BLOCK_ALL",
    non_catholic_response: bool = True
) -> Dict[str, Any]:
    """
    Create safety settings configuration.
    
    Args:
        non_catholic_threshold: Threshold for non-Catholic content (BLOCK_ALL or OFF)
        non_catholic_response: Whether to provide fallback response when blocked
        
    Returns:
        Dict containing safety settings
        
    Raises:
        ValueError: If threshold value is invalid
    """
    valid_thresholds = ["BLOCK_ALL", "OFF"]
    if non_catholic_threshold not in valid_thresholds:
        raise ValueError(f"Invalid threshold '{non_catholic_threshold}'. Must be one of: {valid_thresholds}")
    
    return {
        "CATEGORY_NON_CATHOLIC": {
            "threshold": non_catholic_threshold,
            "response": non_catholic_response
        }
    }


def parse_api_error(response: requests.Response) -> str:
    """
    Parse API error response and return a user-friendly error message.
    
    Args:
        response: The HTTP response object from requests
        
    Returns:
        str: A user-friendly error message
    """
    status_code = response.status_code
    
    # Try to parse JSON error response
    try:
        error_data = response.json()
        error_message = error_data.get('message', 'Unknown error')
    except (json.JSONDecodeError, ValueError):
        error_message = response.text or f"HTTP {status_code} error"
    
    # Map specific error codes to helpful messages
    if status_code == 400:
        if "token limit exceeded" in error_message.lower():
            return "Token limit exceeded. Your request is too long. Please shorten your message and try again."
        return f"Bad request: {error_message}"
    
    elif status_code == 401:
        if "incorrect api key" in error_message.lower():
            return "Incorrect API key provided. Please check your MAGISTERIUM_API_KEY environment variable."
        elif "invalid billing" in error_message.lower():
            return "Invalid billing setup. Please check your billing configuration in your account dashboard."
        elif "tier not found" in error_message.lower():
            return "Invalid service tier. Please contact Magisterium support for assistance."
        return f"Authentication error: {error_message}. Please check your API key."
    
    elif status_code == 429:
        return "Rate limit exceeded. You are making too many requests. Please wait and try again, or upgrade your plan."
    
    elif status_code == 500:
        return "Internal server error. This is an issue on Magisterium's end. Please try again later or contact support."
    
    elif status_code >= 500:
        return f"Server error ({status_code}): {error_message}. Please try again later."
    
    elif status_code >= 400:
        return f"Client error ({status_code}): {error_message}"
    
    return f"HTTP {status_code}: {error_message}"


def create_chat_request(
    message: str, 
    model: str = "magisterium-1", 
    return_related_questions: bool = False,
    safety_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a chat completion request payload.
    
    Args:
        message: The user message to send
        model: The model to use for completion
        return_related_questions: Whether to request related questions in response
        safety_settings: Optional safety settings configuration
        
    Returns:
        Dict containing the request payload
    """
    request_data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": False
    }
    
    if return_related_questions:
        request_data["return_related_questions"] = True
    
    if safety_settings:
        request_data["safety_settings"] = safety_settings
    
    return request_data


def make_chat_request(
    message: str, 
    url: str = "https://www.magisterium.com/api/v1/chat/completions",
    user_agent: str = "magisterium-client/1.0",
    verify_ssl: bool = True,
    proxies: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    model: str = "magisterium-1",
    return_related_questions: bool = False,
    safety_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make a chat completion request to the Magisterium API.
    
    Args:
        message: The user message to send
        url: API endpoint URL
        user_agent: Custom User-Agent string
        verify_ssl: Whether to verify SSL certificates
        proxies: Optional proxy configuration
        timeout: Request timeout in seconds
        model: The model to use for completion
        return_related_questions: Whether to request related questions in response
        safety_settings: Optional safety settings configuration
        
    Returns:
        Dict containing the API response
        
    Raises:
        requests.RequestException: If the request fails
        ValueError: If the response format is invalid
    """
    headers = create_headers(user_agent)
    data = create_chat_request(message, model, return_related_questions, safety_settings)
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=data,
            verify=verify_ssl,
            proxies=proxies,
            timeout=timeout
        )
        response.raise_for_status()
        
        response_data = response.json()
        
        # Validate response format
        if "choices" not in response_data or not response_data["choices"]:
            raise ValueError("Invalid response format: missing choices")
        
        if "message" not in response_data["choices"][0]:
            raise ValueError("Invalid response format: missing message in choice")
            
        return response_data
        
    except requests.exceptions.Timeout:
        raise MagisteriumAPIError(f"Request timed out after {timeout} seconds. Please try again or increase the timeout value.")
    except requests.exceptions.ConnectionError:
        raise MagisteriumAPIError("Failed to connect to API endpoint. Please check your internet connection and the API URL.")
    except requests.exceptions.HTTPError as e:
        error_message = parse_api_error(e.response)
        raise MagisteriumAPIError(error_message, status_code=e.response.status_code)
    except json.JSONDecodeError:
        raise ValueError("Received invalid JSON response from API. The service may be temporarily unavailable.")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Magisterium API client for chat completions"
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        default="What is the Magisterium?",
        help="Message to send to the API (default: 'What is the Magisterium?')"
    )
    
    parser.add_argument(
        "--model",
        default="magisterium-1",
        help="Model to use for completion (default: magisterium-1)"
    )
    
    parser.add_argument(
        "--url",
        default="https://www.magisterium.com/api/v1/chat/completions",
        help="API endpoint URL"
    )
    
    parser.add_argument(
        "--user-agent",
        default="magisterium-client/1.0",
        help="Custom User-Agent header"
    )
    
    parser.add_argument(
        "-k", "--insecure",
        action="store_true",
        help="Disable SSL certificate verification"
    )
    
    parser.add_argument(
        "--burp",
        action="store_true",
        help="Route traffic through Burp Suite proxy (http://localhost:8080)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--related-questions",
        action="store_true",
        help="Request related questions in the response"
    )
    
    parser.add_argument(
        "--non-catholic-threshold",
        choices=["BLOCK_ALL", "OFF"],
        default="BLOCK_ALL",
        help="Threshold for non-Catholic content filtering (default: BLOCK_ALL)"
    )
    
    parser.add_argument(
        "--no-fallback-response",
        action="store_true",
        help="Disable fallback response when content is blocked (default: enabled)"
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main function to execute the Magisterium API client.
    """
    args = parse_arguments()
    
    # Configure SSL warnings if insecure mode is enabled
    if args.insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Configure proxy if Burp mode is enabled
    proxies = None
    if args.burp:
        proxies = {
            "http": "http://localhost:8080",
            "https": "http://localhost:8080"
        }
    
    try:
        # Configure safety settings
        safety_settings = None
        if args.non_catholic_threshold != "BLOCK_ALL" or args.no_fallback_response:
            try:
                safety_settings = create_safety_settings(
                    non_catholic_threshold=args.non_catholic_threshold,
                    non_catholic_response=not args.no_fallback_response
                )
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        
        response = make_chat_request(
            message=args.message,
            url=args.url,
            user_agent=args.user_agent,
            verify_ssl=not args.insecure,
            proxies=proxies,
            timeout=args.timeout,
            model=args.model,
            return_related_questions=args.related_questions,
            safety_settings=safety_settings
        )
        
        # Extract and print the response message
        message = response["choices"][0]["message"]
        print(json.dumps(message, indent=2))
        
        # Print related questions if they exist
        if "related_questions" in response and response["related_questions"]:
            print("\n--- Related Questions ---")
            for i, question in enumerate(response["related_questions"], 1):
                print(f"{i}. {question}")
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except MagisteriumAPIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()