#!/bin/bash

# ==============================================================================
# ThreatCode - Custom Provider Maker-Checker Example
# ==============================================================================
# This script demonstrates how to run ThreatCode with custom LLM providers
# for both the maker (scanner) and checker (validator) roles.
# ==============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}ThreatCode Custom Provider Scan${NC}"
echo -e "${BLUE}=======================================${NC}\n"

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

# Path to scan (default: current directory)
SCAN_PATH="${1:-$(pwd)}"
APP_NAME="${2:-MyApplication}"

echo -e "${GREEN}Scan Configuration:${NC}"
echo -e "  Path: ${SCAN_PATH}"
echo -e "  App Name: ${APP_NAME}\n"

# ------------------------------------------------------------------------------
# Example 1: Together.ai (Maker) + OpenAI (Checker)
# ------------------------------------------------------------------------------
echo -e "${YELLOW}Running with Together.ai + OpenAI...${NC}\n"

docker run --rm \
  -v "${SCAN_PATH}:/scan" \
  -e LLM_PROVIDER=custom \
  -e CUSTOM_API_KEY="${TOGETHER_API_KEY}" \
  -e CUSTOM_MODEL="meta-llama/Llama-3-70b-chat-hf" \
  -e CUSTOM_PROVIDER_URL="https://api.together.xyz/v1" \
  -e ALLOW_ALL_CUSTOM_URLS=true \
  -e ENABLE_CHECKER=true \
  -e CHECKER_PROVIDER=openai \
  -e CHECKER_OPENAI_API_KEY="${OPENAI_API_KEY}" \
  -e CHECKER_OPENAI_MODEL="gpt-4" \
  exrienz/threatcode:latest scan \
  --input /scan \
  --output /scan \
  --name "${APP_NAME}"

# ------------------------------------------------------------------------------
# Example 2: Ollama Local (Maker) + OpenRouter (Checker)
# ------------------------------------------------------------------------------
# Uncomment to use Ollama locally with cloud checker
#
# echo -e "${YELLOW}Running with Ollama + OpenRouter...${NC}\n"
#
# docker run --rm \
#   -v "${SCAN_PATH}:/scan" \
#   --network host \
#   -e LLM_PROVIDER=custom \
#   -e CUSTOM_API_KEY="ollama" \
#   -e CUSTOM_MODEL="codellama:13b" \
#   -e CUSTOM_PROVIDER_URL="http://localhost:11434/v1" \
#   -e ALLOW_ALL_CUSTOM_URLS=true \
#   -e ENABLE_CHECKER=true \
#   -e CHECKER_PROVIDER=openrouter \
#   -e CHECKER_OPENROUTER_API_KEY="${OPENROUTER_API_KEY}" \
#   -e CHECKER_OPENROUTER_MODEL="anthropic/claude-3-opus" \
#   exrienz/threatcode:latest scan \
#   --input /scan \
#   --output /scan \
#   --name "${APP_NAME}"

# ------------------------------------------------------------------------------
# Example 3: Both using custom providers (Groq + Together.ai)
# ------------------------------------------------------------------------------
# Uncomment to use two different custom providers
#
# echo -e "${YELLOW}Running with Groq + Together.ai...${NC}\n"
#
# docker run --rm \
#   -v "${SCAN_PATH}:/scan" \
#   -e LLM_PROVIDER=custom \
#   -e CUSTOM_API_KEY="${GROQ_API_KEY}" \
#   -e CUSTOM_MODEL="llama-3.1-70b-versatile" \
#   -e CUSTOM_PROVIDER_URL="https://api.groq.com/openai/v1" \
#   -e ALLOW_ALL_CUSTOM_URLS=true \
#   -e ENABLE_CHECKER=true \
#   -e CHECKER_PROVIDER=custom \
#   -e CHECKER_CUSTOM_API_KEY="${TOGETHER_API_KEY}" \
#   -e CHECKER_CUSTOM_MODEL="meta-llama/Llama-3.1-405b-instruct-turbo" \
#   -e CHECKER_CUSTOM_PROVIDER_URL="https://api.together.xyz/v1" \
#   exrienz/threatcode:latest scan \
#   --input /scan \
#   --output /scan \
#   --name "${APP_NAME}"

echo -e "\n${GREEN}=======================================${NC}"
echo -e "${GREEN}Scan Complete!${NC}"
echo -e "${GREEN}=======================================${NC}"
echo -e "Check the following files in ${SCAN_PATH}:"
echo -e "  - report.html (detailed web report)"
echo -e "  - report.csv (spreadsheet format)"
echo -e "  - report.json (machine readable)\n"
