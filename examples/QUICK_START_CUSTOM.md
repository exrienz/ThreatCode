# Quick Start: Custom Provider Maker-Checker

## One-Line Commands (Copy & Paste Ready)

### 🚀 Together.ai (Both Maker & Checker)
```bash
docker run --rm -v $(pwd):/scan -e LLM_PROVIDER=custom -e CUSTOM_API_KEY="YOUR_KEY" -e CUSTOM_MODEL="meta-llama/Llama-3-70b-chat-hf" -e CUSTOM_PROVIDER_URL="https://api.together.xyz/v1" -e ALLOW_ALL_CUSTOM_URLS=true -e ENABLE_CHECKER=true -e CHECKER_PROVIDER=custom -e CHECKER_CUSTOM_API_KEY="YOUR_KEY" -e CHECKER_CUSTOM_MODEL="meta-llama/Llama-3.1-405b-instruct-turbo" -e CHECKER_CUSTOM_PROVIDER_URL="https://api.together.xyz/v1" exrienz/threatcode:latest scan --input /scan --output /scan --name "MyApp"
```

### ⚡ Groq (Maker) + Anthropic (Checker)
```bash
docker run --rm -v $(pwd):/scan -e LLM_PROVIDER=custom -e CUSTOM_API_KEY="YOUR_GROQ_KEY" -e CUSTOM_MODEL="llama-3.1-70b-versatile" -e CUSTOM_PROVIDER_URL="https://api.groq.com/openai/v1" -e ALLOW_ALL_CUSTOM_URLS=true -e ENABLE_CHECKER=true -e CHECKER_PROVIDER=custom -e CHECKER_CUSTOM_API_KEY="YOUR_ANTHROPIC_KEY" -e CHECKER_CUSTOM_MODEL="claude-3-opus-20240229" -e CHECKER_CUSTOM_PROVIDER_URL="https://api.anthropic.com/v1" exrienz/threatcode:latest scan --input /scan --output /scan --name "MyApp"
```

### 🏠 Ollama Local (Maker) + OpenRouter (Checker)
```bash
docker run --rm -v $(pwd):/scan --network host -e LLM_PROVIDER=custom -e CUSTOM_API_KEY="ollama" -e CUSTOM_MODEL="codellama:13b" -e CUSTOM_PROVIDER_URL="http://localhost:11434/v1" -e ALLOW_ALL_CUSTOM_URLS=true -e ENABLE_CHECKER=true -e CHECKER_PROVIDER=openrouter -e CHECKER_OPENROUTER_API_KEY="YOUR_KEY" -e CHECKER_OPENROUTER_MODEL="anthropic/claude-3-opus" exrienz/threatcode:latest scan --input /scan --output /scan --name "MyApp"
```

### 💰 DeepInfra (Both - Cost Effective)
```bash
docker run --rm -v $(pwd):/scan -e LLM_PROVIDER=custom -e CUSTOM_API_KEY="YOUR_KEY" -e CUSTOM_MODEL="meta-llama/Meta-Llama-3-70B-Instruct" -e CUSTOM_PROVIDER_URL="https://api.deepinfra.com/v1/openai" -e ALLOW_ALL_CUSTOM_URLS=true -e ENABLE_CHECKER=true -e CHECKER_PROVIDER=custom -e CHECKER_CUSTOM_API_KEY="YOUR_KEY" -e CHECKER_CUSTOM_MODEL="meta-llama/Meta-Llama-3.1-405B-Instruct" -e CHECKER_CUSTOM_PROVIDER_URL="https://api.deepinfra.com/v1/openai" exrienz/threatcode:latest scan --input /scan --output /scan --name "MyApp"
```

---

## Using .env File (Cleaner!)

**Create `.env` file:**
```env
LLM_PROVIDER=custom
CUSTOM_API_KEY=your_key_here
CUSTOM_MODEL=your-maker-model
CUSTOM_PROVIDER_URL=https://your-provider.com/v1
ALLOW_ALL_CUSTOM_URLS=true

ENABLE_CHECKER=true
CHECKER_PROVIDER=custom
CHECKER_CUSTOM_API_KEY=your_checker_key
CHECKER_CUSTOM_MODEL=your-checker-model
CHECKER_CUSTOM_PROVIDER_URL=https://your-checker-provider.com/v1
```

**Run with .env:**
```bash
docker run --rm -v $(pwd):/scan --env-file .env exrienz/threatcode:latest scan --input /scan --output /scan --name "MyApp"
```

---

## What You'll Get

Three files will be created:
- **report.html** ← Open this in your browser!
- **report.csv** ← Import to Excel
- **report.json** ← For automation

Each finding shows:
- ✅ **Confirmed** - Real vulnerability, fix it!
- ❌ **Likely False Positive** - Safe to ignore
- ⚠️ **Needs Review** - Human judgment needed

---

## Replace These Placeholders

| Placeholder | Replace With |
|-------------|--------------|
| `YOUR_KEY` | Your API key from the provider |
| `YOUR_GROQ_KEY` | API key from groq.com |
| `YOUR_ANTHROPIC_KEY` | API key from anthropic.com |
| `$(pwd)` | Full path to your project (or leave as-is) |
| `"MyApp"` | Your application name |

---

## Troubleshooting

**Error: "not in allowlist"**
→ Add: `-e ALLOW_ALL_CUSTOM_URLS=true`

**Ollama not connecting**
→ Add: `--network host`

**High costs**
→ Use cheaper maker model + expensive checker model

---

For more examples, see [docker-custom-maker-checker.md](./docker-custom-maker-checker.md)
