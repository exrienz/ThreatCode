"""OpenRouter LLM provider implementation."""
import json
import re
import httpx
from typing import Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.scanner.providers.base import BaseLLMProvider
from src.utils.config import Finding, Evidence


class JSONParseError(Exception):
    """Custom exception for JSON parsing failures that should trigger retry."""
    pass


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API provider."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def get_headers(self) -> dict:
        """Get HTTP headers for OpenRouter API.

        Returns:
            Dictionary of HTTP headers
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/threatcode-review",
            "X-Title": "ThreatCode Security Scanner"
        }

    def get_endpoint(self) -> str:
        """Get OpenRouter API endpoint.

        Returns:
            Full URL for the chat completions endpoint
        """
        return f"{self.BASE_URL}/chat/completions"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, JSONParseError))
    )
    async def analyze_code(self, code_chunk: str, context: dict) -> List[Finding]:
        """Analyze code using OpenRouter API.

        Args:
            code_chunk: Code content to analyze
            context: Additional context

        Returns:
            List of security findings
        """
        prompt = self.get_security_prompt(code_chunk, context)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a security expert. Return findings in JSON format only. Do not include any explanatory text before or after the JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 16000
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.get_endpoint(),
                headers=self.get_headers(),
                json=payload
            )

            # Log detailed error information before raising
            if response.status_code != 200:
                error_detail = f"HTTP {response.status_code}: {response.text}"
                print(f"Error: OpenRouter API request failed - {error_detail}")

            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse the JSON response - may raise JSONParseError to trigger retry
            findings = self._parse_findings(content, raise_on_error=True)

            # Apply rate limiting delay
            await self.apply_rate_limit()

            return findings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, JSONParseError))
    )
    async def validate_finding(self, finding: Finding, original_code: str) -> Dict:
        """Validate a security finding using the checker LLM.

        Args:
            finding: Finding to validate
            original_code: Original code that was analyzed

        Returns:
            Dictionary with validation results
        """
        prompt = self.get_validation_prompt(finding, original_code)

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior security auditor. Return validation results in JSON format only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,  # Lower temperature for more consistent validation
            "max_tokens": 4000
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.get_endpoint(),
                headers=self.get_headers(),
                json=payload
            )

            if response.status_code != 200:
                error_detail = f"HTTP {response.status_code}: {response.text}"
                print(f"Error: Validation API request failed - {error_detail}")

            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse the validation response
            validation_result = self._parse_validation(content, raise_on_error=True)

            # Apply rate limiting delay
            await self.apply_rate_limit()

            return validation_result

    def _parse_validation(self, content: str, raise_on_error: bool = False) -> Dict:
        """Parse validation response from LLM.

        Args:
            content: JSON string from LLM
            raise_on_error: If True, raise JSONParseError on unrecoverable errors

        Returns:
            Dictionary with verdict, confidence, and rationale
        """
        try:
            # Clean up markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Try to extract JSON from mixed text
            if not content.startswith("{"):
                json_match = re.search(r'\{.*"verdict".*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                else:
                    error_msg = "Could not find validation JSON in response"
                    print(f"Warning: {error_msg}")
                    if raise_on_error:
                        raise JSONParseError(error_msg)
                    return {
                        "verdict": "Needs Review",
                        "confidence": "Low",
                        "rationale": "Failed to parse validation response"
                    }

            data = json.loads(content)

            # Validate required fields
            verdict = data.get("verdict", "Needs Review")
            confidence = data.get("confidence", "Low")
            rationale = data.get("rationale", "No rationale provided")

            return {
                "verdict": verdict,
                "confidence": confidence,
                "rationale": rationale
            }

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse validation JSON: {e}"
            print(f"Warning: {error_msg}")
            if raise_on_error:
                raise JSONParseError(error_msg)
            return {
                "verdict": "Needs Review",
                "confidence": "Low",
                "rationale": f"JSON parsing error: {str(e)}"
            }

    def _parse_findings(self, content: str, raise_on_error: bool = False) -> List[Finding]:
        """Parse LLM response into Finding objects with robust error recovery.

        Args:
            content: JSON string from LLM
            raise_on_error: If True, raise JSONParseError on unrecoverable errors (for retry)

        Returns:
            List of Finding objects
        """
        try:
            # Clean up markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            # Try to extract JSON from mixed text using regex
            if not content.startswith("{"):
                json_match = re.search(r'\{.*"findings".*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                else:
                    error_msg = "Could not find JSON structure in response"
                    print(f"Warning: {error_msg}")
                    if raise_on_error:
                        raise JSONParseError(error_msg)
                    return []

            # Attempt to parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                # Check if response was truncated
                if "Unterminated string" in str(e) or "Expecting" in str(e):
                    print(f"Warning: Response appears truncated. Attempting recovery...")
                    # Try to fix truncated JSON by adding closing braces
                    content = self._attempt_json_repair(content)
                    try:
                        data = json.loads(content)
                        print("Successfully recovered truncated JSON")
                    except json.JSONDecodeError as repair_error:
                        error_msg = f"Could not repair truncated JSON: {repair_error}"
                        print(f"Warning: {error_msg}")
                        if raise_on_error:
                            raise JSONParseError(error_msg)
                        return []
                else:
                    if raise_on_error:
                        raise JSONParseError(f"JSON decode error: {e}")
                    raise

            findings = []
            findings_data = data.get("findings", [])

            if not isinstance(findings_data, list):
                error_msg = f"'findings' is not a list: {type(findings_data)}"
                print(f"Warning: {error_msg}")
                if raise_on_error:
                    raise JSONParseError(error_msg)
                return []

            for idx, finding_data in enumerate(findings_data):
                try:
                    # Validate required fields
                    required_fields = ["title", "severity", "description", "remediation"]
                    missing_fields = [f for f in required_fields if f not in finding_data]

                    if missing_fields:
                        print(f"Warning: Finding {idx} missing required fields: {missing_fields}")
                        continue

                    evidence_list = []
                    for ev in finding_data.get("evidence", []):
                        try:
                            evidence_list.append(Evidence(**ev))
                        except Exception as ev_err:
                            print(f"Warning: Skipping invalid evidence in finding {idx}: {ev_err}")
                            continue

                    finding = Finding(
                        title=finding_data["title"],
                        severity=finding_data["severity"],
                        description=finding_data["description"],
                        evidence=evidence_list,
                        remediation=finding_data["remediation"],
                        cvss_score=finding_data.get("cvss_score"),
                        impact=finding_data.get("impact"),
                        attack_scenario=finding_data.get("attack_scenario"),
                        references=finding_data.get("references")
                    )
                    findings.append(finding)

                except Exception as finding_err:
                    print(f"Warning: Failed to parse finding {idx}: {finding_err}")
                    continue

            return findings

        except (json.JSONDecodeError, KeyError) as e:
            error_msg = f"Failed to parse findings: {e}"
            print(f"Warning: {error_msg}")
            if raise_on_error:
                raise JSONParseError(error_msg)
            return []

    def _attempt_json_repair(self, content: str) -> str:
        """Attempt to repair truncated JSON by adding missing closing braces.

        Args:
            content: Potentially truncated JSON string

        Returns:
            Repaired JSON string
        """
        # Count opening and closing braces/brackets
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_brackets = content.count('[')
        close_brackets = content.count(']')

        # Add missing closing characters
        repaired = content

        # Close any unterminated strings
        quote_count = content.count('"') - content.count('\\"')
        if quote_count % 2 != 0:
            repaired += '"'

        # Add missing closing brackets/braces
        repaired += ']' * (open_brackets - close_brackets)
        repaired += '}' * (open_braces - close_braces)

        return repaired
