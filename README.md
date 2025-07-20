# Magisterium Client

A Python command-line client for the Magisterium API, a Catholic AI assistant service. This client provides a simple and secure way to interact with Magisterium's chat completion endpoints, featuring comprehensive error handling, safety settings, and security options.

## Features

- **Simple CLI Interface** - Easy-to-use command-line tool with helpful defaults
- **Advanced Error Handling** - Specific error messages for different API failures
- **Safety Settings** - Configurable content filtering for Catholic/non-Catholic content
- **Related Questions** - Option to receive suggested follow-up questions
- **Security Options** - SSL verification control and Burp Suite proxy support
- **Comprehensive Testing** - Full unit and integration test suite
- **Type Safety** - Complete type hints throughout the codebase

## Installation

### Prerequisites

- Python 3.7 or higher
- An active Magisterium API key

### Option 1: System-wide Installation (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Magisterium_Client
   ```

2. **Install the package:**
   ```bash
   pip install .
   ```

3. **Set up your API key:**
   ```bash
   export MAGISTERIUM_API_KEY="your_api_key_here"
   # On Windows: set MAGISTERIUM_API_KEY=your_api_key_here
   ```

4. **Run from anywhere:**
   ```bash
   magisterium-client "What is the Trinity?"
   ```

### Option 2: Development Installation

For development or if you prefer not to install system-wide:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Magisterium_Client
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e .
   ```
   
   Or install dependencies only:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   ```bash
   export MAGISTERIUM_API_KEY="your_api_key_here"
   # On Windows: set MAGISTERIUM_API_KEY=your_api_key_here
   ```

5. **Run locally:**
   ```bash
   # If installed in development mode:
   magisterium-client "What is the Trinity?"
   
   # Or run directly:
   python3 magisterium_client.py "What is the Trinity?"
   ```

## Quick Start

### Basic Usage

```bash
# If installed system-wide (recommended):
magisterium-client "What is the Trinity?"

# Or use default question:
magisterium-client

# If running locally:
python3 magisterium_client.py "What is the Trinity?"
```

### With Related Questions

```bash
# System-wide installation:
magisterium-client "What is prayer?" --related-questions

# Local installation:
python3 magisterium_client.py "What is prayer?" --related-questions
```

### Custom Settings

```bash
# System-wide installation:
magisterium-client "Tell me about the Saints" \
    --related-questions \
    --non-catholic-threshold OFF \
    --timeout 60

# Local installation:
python3 magisterium_client.py "Tell me about the Saints" \
    --related-questions \
    --non-catholic-threshold OFF \
    --timeout 60
```

## Command-Line Options

### Basic Options

- `message` - The question or message to send (default: "What is the Magisterium?")
- `--model MODEL` - AI model to use (default: magisterium-1)
- `--timeout SECONDS` - Request timeout in seconds (default: 30)

### API Features

- `--related-questions` - Request related questions in the response
- `--non-catholic-threshold {BLOCK_ALL,OFF}` - Content filtering level (default: BLOCK_ALL)
- `--no-fallback-response` - Disable fallback response when content is blocked

### Security Options

- `-k, --insecure` - Disable SSL certificate verification
- `--burp` - Route traffic through Burp Suite proxy (http://localhost:8080)
- `--user-agent AGENT` - Custom User-Agent header (default: magisterium-client/1.0)

### Advanced Options

- `--url URL` - Custom API endpoint URL
- `--help` - Show help message and exit

## Usage Examples

### Basic Questions

```bash
# Ask about Catholic doctrine
python3 magisterium_client.py "What is the Eucharist?"

# Ask about saints
python3 magisterium_client.py "Tell me about Saint Francis of Assisi"
```

### With Related Questions

```bash
python3 magisterium_client.py "What is the Trinity?" --related-questions
```

**Output:**
```json
{
  "role": "assistant",
  "content": "The Trinity is the central mystery of the Christian faith..."
}

--- Related Questions ---
1. How does the Trinity relate to salvation?
2. What is the role of the Holy Spirit?
3. Can you explain the term 'consubstantial'?
```

### Safety Settings

```bash
# Disable non-Catholic content filtering
python3 magisterium_client.py "What is meditation?" --non-catholic-threshold OFF

# Block non-Catholic content without fallback response
python3 magisterium_client.py "Tell me about Buddhism" --no-fallback-response
```

### Security Testing

```bash
# Route through Burp Suite for security analysis
python3 magisterium_client.py "What is the Mass?" --burp

# Disable SSL verification for testing
python3 magisterium_client.py "What is prayer?" --insecure

# Custom User-Agent for identification
python3 magisterium_client.py "What is faith?" --user-agent "MyApp/2.0"
```

## API Features

### Related Questions

The Magisterium API can provide suggested follow-up questions related to your query. Enable this feature with the `--related-questions` flag.

### Safety Settings

The client supports Magisterium's safety settings for content moderation:

- **BLOCK_ALL** (default) - Blocks queries unrelated to Catholicism
- **OFF** - Disables the non-Catholic content filter

You can also control whether blocked content returns a fallback response or a blank response.

## Development

### Running Tests

The project includes a comprehensive test suite with 38 tests covering all functionality:

```bash
# Run all tests
python3 run_tests.py

# Run only unit tests
python3 run_tests.py --unit-only

# Run only integration tests
python3 run_tests.py --integration-only

# Quiet mode
python3 run_tests.py -v 0

# Alternative: Use unittest directly
python -m unittest discover tests/ -v
```

### Code Style

The project follows strict functional programming principles defined in `docs/CODING_STYLE_RULES.md`:

- Functional over object-oriented programming
- Type hints for all functions
- Comprehensive error handling
- Security-first approach
- Google-style docstrings

### Making Changes

1. Read existing code to understand patterns
2. Follow functional programming approach
3. Add type hints to all new functions
4. Include proper error handling
5. Write tests for new functionality
6. Run tests before committing: `python3 run_tests.py`
7. Run security scans: `semgrep scan --config=auto`

## Error Handling

The client provides specific error messages for different failure scenarios:

### API Key Issues
- **Missing API key**: Set the `MAGISTERIUM_API_KEY` environment variable
- **Invalid API key**: Check your API key in the Magisterium dashboard
- **Billing issues**: Verify your billing setup in your account

### Rate Limiting
- **Too many requests**: Wait before trying again or upgrade your plan

### Network Issues
- **Connection failed**: Check internet connection and API URL
- **Timeout**: Increase timeout with `--timeout` or try again later

### Server Errors
- **Internal server error**: Issue on Magisterium's end, try again later

## Troubleshooting

### Common Issues

**"MAGISTERIUM_API_KEY environment variable not set"**
```bash
# Set your API key
export MAGISTERIUM_API_KEY="your_api_key_here"
```

**"Request timed out"**
```bash
# Increase timeout
python3 magisterium_client.py "Your question" --timeout 60
```

**"Failed to connect to API endpoint"**
- Check internet connection
- Verify API URL is correct
- Check firewall settings

**SSL Certificate Issues**
```bash
# Temporarily disable SSL verification (for testing only)
python3 magisterium_client.py "Your question" --insecure
```

### Debug Mode

For debugging network issues, use Burp Suite integration:

```bash
# Route through Burp Suite proxy for request inspection
python3 magisterium_client.py "Your question" --burp
```

## Security

- API keys are loaded from environment variables only
- HTTPS is used for all API communications by default
- SSL verification can be disabled for testing environments only
- Custom User-Agent headers help identify client requests
- Burp Suite proxy support for security analysis

## Dependencies

- **requests** - HTTP client library for API calls
- **Python 3.7+** - Standard library modules for argument parsing, JSON, etc.

## Contributing

1. Follow the coding standards in `docs/CODING_STYLE_RULES.md`
2. Write tests for new features
3. Ensure all tests pass: `python3 run_tests.py`
4. Run security scans before committing
5. Update documentation as needed

## Security and Coding Practices

This project follows the security and coding practices outlined in the project documentation. See `docs/CODING_STYLE_RULES.md` for detailed guidelines.

## Support

- This API client is designed to work with the Magisterium API service. But the developer of this client is not 
  affiliated with Magisterium.
- For issues with this client, check the error messages and troubleshooting section above or open an issue on the project's GitHub repository.
- For issues with the Magisterium API service, consult their [API documentation](https://www.magisterium.
com/developers) or contact [Magisterium support](https://www.magisterium.com/about/contact).
