#!/usr/bin/env python3

import argparse
import json
import os
import sys
import urllib3
from typing import Dict, Optional, Any

import requests


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


def create_chat_request(message: str, model: str = "magisterium-1") -> Dict[str, Any]:
    """
    Create a chat completion request payload.
    
    Args:
        message: The user message to send
        model: The model to use for completion
        
    Returns:
        Dict containing the request payload
    """
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": message
            }
        ],
        "stream": False
    }


def make_chat_request(
    message: str, 
    url: str = "https://www.magisterium.com/api/v1/chat/completions",
    user_agent: str = "magisterium-client/1.0",
    verify_ssl: bool = True,
    proxies: Optional[Dict[str, str]] = None,
    timeout: int = 30
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
        
    Returns:
        Dict containing the API response
        
    Raises:
        requests.RequestException: If the request fails
        ValueError: If the response format is invalid
    """
    headers = create_headers(user_agent)
    data = create_chat_request(message)
    
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
        raise requests.RequestException(f"Request timed out after {timeout} seconds")
    except requests.exceptions.ConnectionError:
        raise requests.RequestException("Failed to connect to API endpoint")
    except requests.exceptions.HTTPError as e:
        raise requests.RequestException(f"HTTP error: {e}")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response from API")


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
        response = make_chat_request(
            message=args.message,
            url=args.url,
            user_agent=args.user_agent,
            verify_ssl=not args.insecure,
            proxies=proxies,
            timeout=args.timeout
        )
        
        # Extract and print the response message
        message = response["choices"][0]["message"]
        print(json.dumps(message, indent=2))
        
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()