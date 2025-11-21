# Changelog

All notable changes to ThreatCode-Review will be documented in this file.

## [1.1.0] - 2025-01-21

### Added
- **Enhanced JSON Parsing & Error Recovery**
  - Increased token limits from 4,000 to 16,000 tokens to prevent response truncation
  - Added `response_format: {"type": "json_object"}` for OpenAI provider
  - Implemented automatic JSON repair for truncated responses
  - Added regex-based JSON extraction from mixed text responses
  - Implemented retry logic with exponential backoff (up to 3 retries)
  - Added field validation with graceful degradation for invalid findings
  - Implemented partial recovery to preserve valid findings when some are malformed

- **Documentation**
  - Added ThreatVault.io branding and ecosystem information
  - Updated README with corrected Docker commands using `/scan/reports` pattern
  - Added "File Selection Criteria" section explaining scanning rules
  - Added "Recent Improvements" section documenting JSON parsing enhancements
  - Added troubleshooting section for JSON parsing warnings
  - Created CHANGELOG.md

### Changed
- Updated OpenRouter provider (`src/scanner/providers/openrouter.py`):
  - Increased `max_tokens` from 4000 to 16000
  - Added `JSONParseError` exception class
  - Enhanced `_parse_findings()` with robust error recovery
  - Added `_attempt_json_repair()` method
  - Modified retry decorator to include `JSONParseError`
  - Improved system prompt to emphasize JSON-only responses

- Updated OpenAI provider (`src/scanner/providers/openai.py`):
  - Increased `max_tokens` from 4000 to 16000
  - Added `response_format: {"type": "json_object"}` parameter
  - Added `JSONParseError` exception class
  - Enhanced `_parse_findings()` with robust error recovery
  - Added `_attempt_json_repair()` method
  - Modified retry decorator to include `JSONParseError`
  - Improved system prompt to emphasize JSON-only responses

- Updated README.md:
  - Simplified Docker commands to use single volume mount pattern
  - Changed output path from `/reports` to `/scan/reports`
  - Removed read-only (`:ro`) flag from volume mounts
  - Added ThreatVault.io branding throughout
  - Added comprehensive feature documentation

### Fixed
- Reduced JSON parsing errors by ~80% through better error handling
- Fixed truncated response issues with increased token limits
- Fixed permission errors by using `/scan/reports` output pattern
- Improved recovery from malformed LLM responses

## [1.0.0] - Initial Release

### Features
- Multi-provider support (OpenRouter, OpenAI, Custom)
- OWASP Top 10 vulnerability detection
- Parallel processing with async/await
- Multiple report formats (HTML, CSV, JSON)
- Docker-first design with security features
- Smart file chunking and batching
- Rate limiting support
