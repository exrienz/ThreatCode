# ThreatCode

**Part of the [ThreatVault.io](https://threatvault.io) Ecosystem**

AI-powered security scanner that finds vulnerabilities in your source code using Large Language Models.

## 🚀 Quick Start (Easiest Way)

No installation needed! Just run the pre-built Docker image:

### 1. Pull the Image
```bash
docker pull exrienz/threatcode:latest
```

### 2. Run a Scan

Navigate to your project folder and run:

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=openrouter \
  -e OPENROUTER_API_KEY=YOUR_API_KEY \
  -e OPENROUTER_MODEL=anthropic/claude-3-haiku \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

**That's it!** Your security report will be generated in the same folder.

> **📁 Important:** Always use `--output /scan` to save reports in your project folder. No need to create a separate reports directory.

---

## 📋 What You'll Get

After scanning, you'll find three report files in your project folder:

- **`report.html`** - Beautiful, interactive web report
- **`report.csv`** - Spreadsheet-friendly format
- **`report.json`** - Machine-readable format

Each report includes:
- ✅ Security vulnerabilities ranked by severity (Critical, High, Medium, Low)
- ✅ Exact file locations and line numbers
- ✅ Detailed explanations of each issue
- ✅ Step-by-step remediation guidance
- ✅ CVSS scores and impact assessment

---

## 🔧 Configuration Options

### Using OpenRouter (Recommended)

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=openrouter \
  -e OPENROUTER_API_KEY=YOUR_API_KEY \
  -e OPENROUTER_MODEL=anthropic/claude-3-haiku \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

**Popular models:**
- `anthropic/claude-3-haiku` (fast, cost-effective)
- `anthropic/claude-3-sonnet` (balanced)
- `openai/gpt-4` (most thorough)
- `z-ai/glm-4.5-air:free` (free tier option)

### Using OpenAI

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=openai \
  -e OPENAI_API_KEY=YOUR_API_KEY \
  -e OPENAI_MODEL=gpt-4 \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

### Using a Custom LLM Provider

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=custom \
  -e CUSTOM_API_KEY=YOUR_API_KEY \
  -e CUSTOM_MODEL=your-model-name \
  -e CUSTOM_PROVIDER_URL=https://your-api.com/v1 \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

### Using Environment File

Create a `.env` file in your project:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku
```

Then run:

```bash
docker run --rm \
  -v $(pwd):/scan \
  --env-file .env \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

---

## 🎯 Supported Languages

ThreatCode analyzes these file types:

| Language | Extensions |
|----------|-----------|
| Python | `.py` |
| JavaScript/TypeScript | `.js`, `.jsx`, `.ts`, `.tsx` |
| Java | `.java` |
| Go | `.go` |
| Ruby | `.rb` |
| PHP | `.php` |
| C/C++ | `.c`, `.cpp`, `.h`, `.hpp` |
| C# | `.cs` |

**Automatically excludes:**
- `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`
- Minified files (`.min.js`, `.min.css`)
- Files larger than 1MB

---

## ⚙️ Advanced Options

### Scan Specific Directory

```bash
docker run --rm \
  -v /absolute/path/to/project:/scan \
  --env-file .env \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

### Adjust Concurrency

```bash
# Use --max-workers to control parallel processing (default: 10)
docker run --rm \
  -v $(pwd):/scan \
  --env-file .env \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp" \
  --max-workers 5
```

### Custom File Size Limit

```bash
# Use --max-file-size to set max file size in bytes (default: 1MB)
docker run --rm \
  -v $(pwd):/scan \
  --env-file .env \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp" \
  --max-file-size 2097152  # 2MB
```

---

## 🛠️ Build Your Own Image (Optional)

If you prefer to build from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/ThreatCode.git
cd ThreatCode

# Build the Docker image
docker build -t threatcode .

# Run with your custom build
docker run --rm \
  -v $(pwd):/scan \
  --env-file .env \
  threatcode scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

---

## 🔐 Security Features

ThreatCode follows security best practices:

- ✅ **No API keys in CLI** - All credentials via environment variables
- ✅ **SSRF protection** - Custom provider URLs validated against allowlist
- ✅ **Path traversal protection** - Safe file operations using pathlib
- ✅ **Rate limiting** - Configurable delays to respect API limits
- ✅ **Non-root execution** - Runs as unprivileged user in Docker
- ✅ **Request timeouts** - 30-second default timeout on all API calls

---

## 📊 Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `LLM_PROVIDER` | Provider choice | Yes | `openrouter`, `openai`, `custom` |
| `OPENROUTER_API_KEY` | OpenRouter API key | For OpenRouter | `sk-or-v1-...` |
| `OPENROUTER_MODEL` | OpenRouter model name | For OpenRouter | `anthropic/claude-3-haiku` |
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI | `sk-...` |
| `OPENAI_MODEL` | OpenAI model name | For OpenAI | `gpt-4` |
| `CUSTOM_API_KEY` | Custom provider API key | For custom | Your API key |
| `CUSTOM_MODEL` | Custom provider model | For custom | Model identifier |
| `CUSTOM_PROVIDER_URL` | Custom provider base URL | For custom | `https://api.example.com/v1` |
| `RATE_LIMIT_DELAY` | Delay between requests (seconds) | No | `0.5` (default) |
| `ALLOW_ALL_CUSTOM_URLS` | Bypass URL allowlist ⚠️ | No | `false` (default) |

---

## ❓ Troubleshooting

### "No files found to analyze"

**Solution:** Ensure your project contains supported file types and they're not in excluded directories:
```bash
# Check what files will be scanned
ls -la  # Look for .py, .js, .java, etc.
```

### "API key not found"

**Solution:** Double-check your environment variables:
```bash
# Test your environment variables
docker run --rm \
  -e LLM_PROVIDER=openrouter \
  -e OPENROUTER_API_KEY=test \
  exrienz/threatcode:latest providers
```

### Permission Errors

**Solution:** Always use `--output /scan` to write reports in the mounted directory:
```bash
# ✅ Correct
--output /scan

# ❌ Incorrect
--output /reports
```

### JSON Parsing Warnings

**What it means:** The LLM response was malformed, but ThreatCode automatically recovers and continues scanning.

**What to do:** Nothing! The scanner handles this automatically. If you see many warnings, consider using a more stable model.

---

## 🏗️ Architecture

```
src/
├── main.py              # CLI entry point
├── scanner/
│   ├── file_collector.py # Discovers and filters files
│   ├── providers/        # LLM provider implementations
│   │   ├── base.py       # Abstract provider interface
│   │   ├── openrouter.py # OpenRouter client
│   │   └── openai.py     # OpenAI client
│   └── analyzer.py       # Orchestrates scanning
├── templates/
│   └── report.html       # HTML report template
└── utils/
    ├── config.py         # Configuration & validation
    └── formatters.py     # Report generators
```

For detailed architecture information, see [CLAUDE.md](CLAUDE.md).

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please open an issue first to discuss major changes.

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Documentation:** [CLAUDE.md](CLAUDE.md)
- **ThreatVault Ecosystem:** [threatvault.io](https://threatvault.io)
- **Issues & Support:** [GitHub Issues](https://github.com/yourusername/ThreatCode/issues)

---

**ThreatCode** - Secure Code Analysis, Powered by AI

Created by **exrienz** | Part of [ThreatVault.io](https://threatvault.io)
