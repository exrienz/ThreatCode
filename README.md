# ThreatCode-Review

**Part of the [ThreatVault.io](https://threatvault.io) Ecosystem**

AI-Powered Security Code Scanner that uses Large Language Models to analyze source code for security vulnerabilities. ThreatCode-Review is a key component of the ThreatVault security tooling suite.

> **📖 New to ThreatCode-Review?** See [QUICKSTART.md](QUICKSTART.md) for the simplest way to get started!
> **⚡ Quick Reference:** See [CHEATSHEET.md](CHEATSHEET.md) for copy-paste commands!

## Features

- **Multi-Provider Support**: Works with OpenRouter, OpenAI, and custom LLM providers
- **Comprehensive Security Analysis**:
  - OWASP Top 10 vulnerability detection (Injection, Broken Auth, XSS, etc.)
  - Security misconfigurations and insecure coding practices
  - Business logic flaws and dependency vulnerabilities
  - CVSS-based severity scoring (Critical, High, Medium, Low, Informational)
  - Detailed remediation guidance with code examples
- **Enhanced JSON Parsing**:
  - Robust error recovery for malformed LLM responses
  - Automatic truncation detection and repair
  - Retry logic with exponential backoff
  - Increased token limits (16,000 tokens) to prevent truncation
- **Multiple Report Formats**: Generates professional HTML, CSV, and JSON reports
- **Docker-First Design**: Secure, containerized execution with non-root user
- **Parallel Processing**: Efficient scanning with async concurrent file processing
- **Smart Chunking**: Handles large codebases with intelligent file batching
- **Rate Limiting**: Configurable delays to respect API provider limits

## Quick Start

### Prerequisites

- Docker (recommended) or Python 3.9+
- API key from OpenRouter or OpenAI

### Using Docker (Recommended)

**Simple approach - output to /scan/reports subdirectory:**

1. **Build the image** (one-time):
```bash
cd /path/to/ThreatCode-Review
docker build -t security-scanner .
```

2. **Run the scan**:
```bash
cd /path/to/your/project

# Using OpenRouter
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=openrouter \
  -e OPENROUTER_API_KEY=your_key_here \
  -e OPENROUTER_MODEL=anthropic/claude-3-haiku \
  security-scanner scan \
  --input /scan \
  --output /scan/reports \
  --name "MyApplication"

# Using OpenAI
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=your_key_here \
  -e OPENAI_MODEL=gpt-4 \
  security-scanner scan \
  --input /scan \
  --output /scan/reports \
  --name "MyApplication"

# Using Custom Provider
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=custom \
  -e OPENROUTER_API_KEY=your_key_here \
  -e CUSTOM_PROVIDER_URL=https://my-llm.example.com/v1 \
  security-scanner scan \
  --input /scan \
  --output /scan/reports \
  --name "MyApplication"
```

**That's it!** Reports are created in `./reports/` subdirectory with no permission errors.

**Alternative: Using .env file**
```bash
# Create .env file
cat > .env << EOF
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku
EOF

# Run with --env-file
docker run --rm \
  -v $(pwd):/scan \
  --env-file .env \
  security-scanner scan \
  --input /scan \
  --output /scan/reports \
  --name "MyApplication"
```

### Local Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run a scan**:
```bash
python -m src.main scan \
  --input /path/to/code \
  --output ./reports \
  --name "MyApplication"
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `LLM_PROVIDER` | Provider choice: `openrouter`, `openai`, or `custom` | Yes | - |
| `OPENROUTER_API_KEY` | OpenRouter API key | If using OpenRouter | - |
| `OPENROUTER_MODEL` | Model name (e.g., `anthropic/claude-3-haiku`) | If using OpenRouter | - |
| `OPENAI_API_KEY` | OpenAI API key | If using OpenAI | - |
| `OPENAI_MODEL` | Model name (e.g., `gpt-4`) | If using OpenAI | - |
| `CUSTOM_PROVIDER_URL` | Custom provider base URL | If using custom provider | - |
| `RATE_LIMIT_DELAY` | Delay between API requests (seconds) | No | `0.5` |
| `ALLOW_ALL_CUSTOM_URLS` | Allow any custom URL (not recommended) | No | `false` |

### Supported File Types

- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Java (`.java`)
- Go (`.go`)
- Ruby (`.rb`)
- PHP (`.php`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)
- C# (`.cs`)

### File Selection Criteria

Files must meet **all** of the following criteria to be scanned:

1. **File Extension**: Must be one of the supported extensions listed above
2. **Not Excluded**: Files/directories matching these patterns are skipped:
   - `.git`, `__pycache__`, `node_modules`, `.venv`, `venv`
   - `*.min.js`, `*.min.css`, `.pyc`
3. **File Size**: Maximum 1MB (1,048,576 bytes) per file
4. **Regular File**: Directories, symlinks, and special files are excluded

## CLI Commands

### Scan Command

```bash
python -m src.main scan [OPTIONS]
```

**Options**:
- `--input, -i`: Input directory or file to scan (required)
- `--output, -o`: Output directory for reports (required)
- `--name, -n`: Application name for the report (default: "Application")
- `--max-file-size`: Maximum file size in bytes (default: 1048576)
- `--max-workers`: Maximum concurrent workers (default: 10)

### Other Commands

```bash
# Show version
python -m src.main version

# List supported providers
python -m src.main providers

# Show help
python -m src.main --help
```

## Reports

The scanner generates three types of reports:

1. **HTML Report** (`report.html`): Interactive, styled report with severity statistics
2. **CSV Report** (`report.csv`): Tabular format for spreadsheet analysis
3. **JSON Report** (`report.json`): Machine-readable format for integration

### Severity Levels

- **Critical**: Immediate action required (easily exploitable, high impact)
- **High**: Should be addressed soon (exploitable with moderate effort)
- **Medium**: Should be reviewed and addressed (requires specific conditions)
- **Low**: Minor issues or improvements (difficult to exploit or minimal impact)
- **Informational**: Best practices and recommendations (no direct security impact)

## Architecture

```
src/
├── main.py              # CLI entry point
├── scanner/
│   ├── file_collector.py # File discovery and batching
│   ├── providers/        # LLM provider implementations
│   │   ├── base.py       # Abstract provider interface
│   │   ├── openrouter.py # OpenRouter implementation
│   │   └── openai.py     # OpenAI implementation
│   └── analyzer.py       # Core analysis orchestration
├── templates/
│   └── report.html       # Jinja2 report template
└── utils/
    ├── config.py         # Configuration and data models
    └── formatters.py     # Report generation
```

### Recent Improvements

**Enhanced JSON Parsing & Error Recovery** (v1.1.0)

The scanner now includes robust error handling for LLM responses:

- **Increased Token Limits**: Raised from 4,000 to 16,000 tokens to prevent response truncation
- **JSON Mode**: OpenAI provider uses `response_format: {"type": "json_object"}` for guaranteed valid JSON
- **Automatic Repair**: Detects and repairs truncated JSON responses by adding missing closing braces
- **Regex Extraction**: Extracts JSON from mixed text responses when LLM adds explanatory text
- **Retry Logic**: Automatically retries up to 3 times with exponential backoff on parse failures
- **Field Validation**: Validates required fields and skips invalid findings while preserving valid ones
- **Partial Recovery**: Returns partial results instead of failing entirely on malformed responses

These improvements significantly reduce parsing errors and increase the reliability of security analysis.

## Security Features

- **API keys via environment variables only** - Never passed as CLI arguments
- **Path traversal protection** - Using `pathlib` for safe file operations
- **SSRF protection** - URL validation for custom provider endpoints with domain allowlist
- **Provider URL allowlist** - Custom providers restricted to trusted domains (api.openai.com, openrouter.ai, api.anthropic.com, etc.)
- **Rate limiting** - Configurable delays between API requests to prevent abuse and respect provider limits
- **Input sanitization** - Pydantic validation for all inputs
- **Request timeouts** - 30-second default timeout on all HTTP requests
- **Non-root Docker execution** - Runs as unprivileged user (appuser:1000)
- **Read-write isolation** - Safe file operations with proper permissions

## Examples

### Scan current directory with OpenRouter

```bash
cd ~/projects/myapp
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=openrouter \
  -e OPENROUTER_API_KEY=sk-or-v1-your-key \
  -e OPENROUTER_MODEL=anthropic/claude-3-haiku \
  security-scanner scan \
  --input /scan \
  --output /scan/reports \
  --name "MyPythonApp"
```

Reports created in `./reports/` subdirectory.

### Scan with OpenAI GPT-4

```bash
cd ~/projects/webapp
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e OPENAI_MODEL=gpt-4 \
  security-scanner scan \
  --input /scan \
  --output /scan/reports \
  --name "MyWebApp"
```

### Scan specific directory

```bash
docker run --rm \
  -v /path/to/myapp:/scan \
  --env-file .env \
  security-scanner scan \
  --input /scan \
  --output /scan/reports \
  --name "MyApplication"
```

### Scan a single file

```bash
python -m src.main scan \
  --input /path/to/file.py \
  --output ./reports \
  --name "SingleFile"
```

## Development

### Project Structure

See [CLAUDE.md](CLAUDE.md) for detailed architecture and development guidance.

### Adding a New Provider

1. Create a new provider class in `src/scanner/providers/`
2. Inherit from `BaseLLMProvider`
3. Implement required methods: `analyze_code()`, `get_headers()`, `get_endpoint()`
4. Implement `_parse_findings()` with error recovery logic
5. Update `src/scanner/analyzer.py` to support the new provider

## Troubleshooting

### "Configuration Error: API key not found"
Ensure environment variables are set correctly. Use `python -m src.main providers` to see required variables.

### "No files found to analyze"
Check that your input path contains files with supported extensions. The scanner only analyzes:
- Python, JavaScript/TypeScript, Java, Go, Ruby, PHP, C/C++, C# files
- Files under 1MB in size
- Files not in excluded directories (`.git`, `node_modules`, `__pycache__`, etc.)

### JSON Parsing Warnings
If you see warnings like "Failed to parse findings" or "Unterminated string":
- These are automatically handled with retry logic and error recovery
- The scanner will continue processing and return partial results
- Consider using a model with larger context windows if errors persist

### Permission Errors
Use the recommended Docker command format with single volume mount:
```bash
docker run --rm -v $(pwd):/scan ...
```
This avoids permission issues by writing to `/scan/reports` subdirectory.

## ThreatVault Ecosystem

ThreatCode-Review is part of the ThreatVault.io security platform, which provides comprehensive security tooling for development teams. Visit [ThreatVault.io](https://threatvault.io) to learn more about the complete security ecosystem.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.

---

**ThreatCode-Review** - Secure Code Analysis, Powered by AI | Part of [ThreatVault.io](https://threatvault.io)
