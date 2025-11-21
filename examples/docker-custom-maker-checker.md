# Docker Examples: Custom Provider Maker-Checker

Complete examples for running ThreatCode with custom providers for both maker and checker LLMs.

---

## Example 1: Both Using Together.ai (Different Models)

**Use Case:** Fast model for scanning, powerful model for validation

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=custom \
  -e CUSTOM_API_KEY="YOUR_TOGETHER_API_KEY" \
  -e CUSTOM_MODEL="meta-llama/Llama-3-70b-chat-hf" \
  -e CUSTOM_PROVIDER_URL="https://api.together.xyz/v1" \
  -e ALLOW_ALL_CUSTOM_URLS=true \
  -e ENABLE_CHECKER=true \
  -e CHECKER_PROVIDER=custom \
  -e CHECKER_CUSTOM_API_KEY="YOUR_TOGETHER_API_KEY" \
  -e CHECKER_CUSTOM_MODEL="meta-llama/Llama-3.1-405b-instruct-turbo" \
  -e CHECKER_CUSTOM_PROVIDER_URL="https://api.together.xyz/v1" \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

---

## Example 2: Groq (Maker) + Anthropic (Checker)

**Use Case:** Ultra-fast Groq for scanning, Claude for high-quality validation

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=custom \
  -e CUSTOM_API_KEY="YOUR_GROQ_API_KEY" \
  -e CUSTOM_MODEL="llama-3.1-70b-versatile" \
  -e CUSTOM_PROVIDER_URL="https://api.groq.com/openai/v1" \
  -e ALLOW_ALL_CUSTOM_URLS=true \
  -e ENABLE_CHECKER=true \
  -e CHECKER_PROVIDER=custom \
  -e CHECKER_CUSTOM_API_KEY="YOUR_ANTHROPIC_API_KEY" \
  -e CHECKER_CUSTOM_MODEL="claude-3-opus-20240229" \
  -e CHECKER_CUSTOM_PROVIDER_URL="https://api.anthropic.com/v1" \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

---

## Example 3: Ollama Local (Maker) + Cloud API (Checker)

**Use Case:** Free local scanning, paid cloud validation

```bash
# Make sure Ollama is running locally first!
# ollama pull codellama:13b

docker run --rm \
  -v $(pwd):/scan \
  --network host \
  -e LLM_PROVIDER=custom \
  -e CUSTOM_API_KEY="ollama" \
  -e CUSTOM_MODEL="codellama:13b" \
  -e CUSTOM_PROVIDER_URL="http://localhost:11434/v1" \
  -e ALLOW_ALL_CUSTOM_URLS=true \
  -e ENABLE_CHECKER=true \
  -e CHECKER_PROVIDER=openrouter \
  -e CHECKER_OPENROUTER_API_KEY="YOUR_OPENROUTER_KEY" \
  -e CHECKER_OPENROUTER_MODEL="anthropic/claude-3-opus" \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

**Note:** Use `--network host` to allow Docker to access localhost services.

---

## Example 4: DeepInfra (Both Maker and Checker)

**Use Case:** Cost-effective provider for both roles

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e LLM_PROVIDER=custom \
  -e CUSTOM_API_KEY="YOUR_DEEPINFRA_KEY" \
  -e CUSTOM_MODEL="meta-llama/Meta-Llama-3-70B-Instruct" \
  -e CUSTOM_PROVIDER_URL="https://api.deepinfra.com/v1/openai" \
  -e ALLOW_ALL_CUSTOM_URLS=true \
  -e ENABLE_CHECKER=true \
  -e CHECKER_PROVIDER=custom \
  -e CHECKER_CUSTOM_API_KEY="YOUR_DEEPINFRA_KEY" \
  -e CHECKER_CUSTOM_MODEL="meta-llama/Meta-Llama-3.1-405B-Instruct" \
  -e CHECKER_CUSTOM_PROVIDER_URL="https://api.deepinfra.com/v1/openai" \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "MyApp"
```

---

## Example 5: Using .env File (Recommended)

Create a file named `.env` in your project:

```env
# Maker (Scanner)
LLM_PROVIDER=custom
CUSTOM_API_KEY=your_maker_api_key
CUSTOM_MODEL=llama-3-70b-instruct
CUSTOM_PROVIDER_URL=https://api.together.xyz/v1
ALLOW_ALL_CUSTOM_URLS=true

# Checker (Validator)
ENABLE_CHECKER=true
CHECKER_PROVIDER=custom
CHECKER_CUSTOM_API_KEY=your_checker_api_key
CHECKER_CUSTOM_MODEL=claude-3-opus-20240229
CHECKER_CUSTOM_PROVIDER_URL=https://api.anthropic.com/v1

# Optional: Rate limiting
RATE_LIMIT_DELAY=0.5
```

Then run with `--env-file`:

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

## Example 6: Separate Reports Directory

```bash
# Create reports directory
mkdir -p ./security-reports

docker run --rm \
  -v $(pwd):/scan:ro \
  -v $(pwd)/security-reports:/reports \
  -e LLM_PROVIDER=custom \
  -e CUSTOM_API_KEY="YOUR_API_KEY" \
  -e CUSTOM_MODEL="your-maker-model" \
  -e CUSTOM_PROVIDER_URL="https://api.provider.com/v1" \
  -e ALLOW_ALL_CUSTOM_URLS=true \
  -e ENABLE_CHECKER=true \
  -e CHECKER_PROVIDER=custom \
  -e CHECKER_CUSTOM_API_KEY="YOUR_API_KEY" \
  -e CHECKER_CUSTOM_MODEL="your-checker-model" \
  -e CHECKER_CUSTOM_PROVIDER_URL="https://api.provider.com/v1" \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /reports \
  --name "MyApp"

# Reports will be in ./security-reports/
```

---

## Popular Custom Provider URLs

| Provider | URL | Notes |
|----------|-----|-------|
| Together.ai | `https://api.together.xyz/v1` | Fast, affordable |
| Groq | `https://api.groq.com/openai/v1` | Extremely fast |
| DeepInfra | `https://api.deepinfra.com/v1/openai` | Cost-effective |
| Anthropic | `https://api.anthropic.com/v1` | High quality |
| Ollama | `http://localhost:11434/v1` | Local, free |
| Replicate | `https://api.replicate.com/v1` | Various models |
| Anyscale | `https://api.endpoints.anyscale.com/v1` | Ray-based |

---

## Common Models for Maker-Checker

### Good Maker Models (Fast, Cost-Effective)
- `meta-llama/Llama-3-70b-chat-hf` (Together.ai)
- `llama-3.1-70b-versatile` (Groq)
- `codellama:13b` (Ollama - local)
- `mistralai/Mixtral-8x7B-Instruct-v0.1` (Various)

### Good Checker Models (High Quality)
- `meta-llama/Llama-3.1-405b-instruct-turbo` (Together.ai)
- `claude-3-opus-20240229` (Anthropic)
- `gpt-4` (OpenAI via OpenRouter)
- `llama-3.1-405b-reasoning` (Groq)

---

## Troubleshooting

### Error: "Custom provider URL is not in the allowlist"

**Solution:** Add `ALLOW_ALL_CUSTOM_URLS=true` to your environment variables:

```bash
docker run --rm \
  -v $(pwd):/scan \
  -e ALLOW_ALL_CUSTOM_URLS=true \
  ... other variables ...
```

### Error: "Checker API key not found"

**Solution:** Make sure you're using the correct prefix for checker variables:
- OpenRouter: `CHECKER_OPENROUTER_API_KEY`
- OpenAI: `CHECKER_OPENAI_API_KEY`
- Custom: `CHECKER_CUSTOM_API_KEY`

### Ollama Connection Issues

**Solution:** Use `--network host` to allow Docker to access localhost:

```bash
docker run --rm \
  -v $(pwd):/scan \
  --network host \
  -e CUSTOM_PROVIDER_URL="http://localhost:11434/v1" \
  ...
```

---

## Cost Optimization Tips

1. **Use a cheaper/faster model for maker, expensive/better for checker**
   - Maker: Llama 3 70B (~$0.88/1M tokens)
   - Checker: Llama 3.1 405B (~$3.50/1M tokens)

2. **Use free local models for maker, paid cloud for checker**
   - Maker: Ollama (free, local)
   - Checker: Claude Opus (paid, cloud)

3. **Only enable checker for critical projects**
   - Regular scans: Disable checker
   - Pre-production: Enable checker

4. **Adjust rate limiting to avoid throttling charges**
   ```bash
   -e RATE_LIMIT_DELAY=1.0
   ```

---

## Security Notes

⚠️ **Important:**

1. Never commit `.env` files with API keys to version control
2. Add `.env` to your `.gitignore`
3. Only set `ALLOW_ALL_CUSTOM_URLS=true` for trusted providers
4. Rotate API keys regularly
5. Use read-only mounts when possible: `-v $(pwd):/scan:ro`

---

## Next Steps

After scanning, you'll find three report files:
- **`report.html`** - Open in browser for detailed view with validation status
- **`report.csv`** - Import to Excel/Google Sheets
- **`report.json`** - Process programmatically

Each finding will show:
- ✅ **Confirmed** (green) - Real vulnerability
- ❌ **Likely False Positive** (red) - Can ignore
- ⚠️ **Needs Review** (orange) - Requires human judgment
