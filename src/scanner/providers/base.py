"""Abstract base class for LLM providers."""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List
from src.utils.config import Finding


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers."""

    def __init__(self, api_key: str, model: str, timeout: int = 30, rate_limit_delay: float = 0.5):
        """Initialize the provider.

        Args:
            api_key: API key for authentication
            model: Model identifier to use
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between API requests in seconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay

    @abstractmethod
    async def analyze_code(self, code_chunk: str, context: dict) -> List[Finding]:
        """Analyze code and return security findings.

        Args:
            code_chunk: Code content to analyze
            context: Additional context (file paths, metadata, etc.)

        Returns:
            List of security findings
        """
        pass

    @abstractmethod
    def get_headers(self) -> dict:
        """Get HTTP headers for API requests.

        Returns:
            Dictionary of HTTP headers
        """
        pass

    @abstractmethod
    def get_endpoint(self) -> str:
        """Get API endpoint URL.

        Returns:
            Full URL for the API endpoint
        """
        pass

    @abstractmethod
    async def validate_finding(self, finding: Finding, original_code: str) -> Dict:
        """Validate a security finding to eliminate false positives.

        Args:
            finding: Finding to validate
            original_code: Original code that was analyzed

        Returns:
            Dictionary with validation results:
            {
                "verdict": "Confirmed|Likely False Positive|Needs Review",
                "confidence": "High|Medium|Low",
                "rationale": "Explanation of the verdict"
            }
        """
        pass

    def get_security_prompt(self, code_chunk: str, context: dict) -> str:
        """Generate security analysis prompt.

        Args:
            code_chunk: Code content to analyze
            context: Additional context

        Returns:
            Formatted prompt for LLM
        """
        file_info = context.get('file_paths', ['unknown'])

        prompt = f"""Act as a seasoned security researcher with expertise in application security and vulnerability assessment. Conduct a comprehensive source code review of the provided codebase to identify security vulnerabilities, weaknesses, and coding best practices violations.

Files being analyzed: {', '.join(file_info)}

Code to analyze:
```
{code_chunk}
```

For your analysis, you must:

1. Perform a thorough examination of the entire codebase, looking for:
   - OWASP Top 10 vulnerabilities (injection, broken authentication, sensitive data exposure, etc.)
   - Common security misconfigurations
   - Insecure coding practices
   - Potential business logic flaws
   - Dependencies with known vulnerabilities
   - Information disclosure issues
   - Insecure error handling
   - Insufficient input validation and output encoding
   - Insecure direct object references
   - Security misconfigurations
   - Any other security-relevant issues

2. For each identified vulnerability, you must document:
   - Finding Name: Clear, concise title for the vulnerability
   - Severity: Critical, High, Medium, Low, or Informational (based on CVSS scoring guidelines)
     * Critical: Easily exploitable, high impact, allows complete system compromise
     * High: Exploitable with moderate effort, significant impact
     * Medium: Requires specific conditions, moderate impact
     * Low: Difficult to exploit or minimal impact
     * Informational: Best practices, no direct security impact
   - Description: Detailed explanation of the vulnerability and its potential impact
   - Evidence: Specific file path, line number(s), and the relevant code snippet
   - Suggested Remediation: Step-by-step instructions to fix the vulnerability

3. Prioritize findings based on potential business impact and exploitability.

**IMPORTANT**: Return your findings in JSON format ONLY. Do not include any additional text, explanations, or markdown formatting outside the JSON structure.

Required JSON format:
{{
    "findings": [
        {{
            "title": "Clear, concise vulnerability title",
            "severity": "Critical|High|Medium|Low|Informational",
            "description": "Detailed explanation of the vulnerability and its potential impact",
            "evidence": [
                {{
                    "file_path": "path/to/file.ext",
                    "line_number": 42,
                    "code": "actual vulnerable code from the file",
                    "description": "Optional explanation of this specific evidence"
                }}
            ],
            "remediation": "Step-by-step instructions to fix the vulnerability with code examples if applicable",
            "cvss_score": "Optional: CVSS score (e.g., '9.8' or 'CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H')",
            "impact": "Optional: Description of business/security impact if exploited",
            "attack_scenario": "Optional: Detailed scenario describing how an attacker could exploit this vulnerability",
            "references": ["Optional: Array of URLs or references to CWE, OWASP, CVE, etc."]
        }}
    ]
}}

Note: The optional fields (cvss_score, impact, attack_scenario, references) should be included when applicable to provide comprehensive security analysis.

Return ONLY the JSON response. No additional text, no markdown code blocks, just pure JSON."""

        return prompt

    def get_validation_prompt(self, finding: Finding, original_code: str) -> str:
        """Generate validation prompt for checker LLM.

        Args:
            finding: Finding to validate
            original_code: Original code that was analyzed

        Returns:
            Formatted prompt for validation
        """
        evidence_text = "\n".join([
            f"- File: {ev.file_path}, Line: {ev.line_number}\n  Code: {ev.code}"
            for ev in finding.evidence
        ])

        prompt = f"""Act as a senior security auditor performing a second-level review of a security finding. Your task is to validate whether this finding is a TRUE POSITIVE or a FALSE POSITIVE.

**Finding to Validate:**
Title: {finding.title}
Severity: {finding.severity}
Description: {finding.description}

Evidence:
{evidence_text}

Remediation Suggested: {finding.remediation}

**Original Code Context:**
```
{original_code}
```

**Your Task:**
Carefully review the finding and the code context. Determine whether this is:
1. **Confirmed**: A legitimate security vulnerability that should be addressed
2. **Likely False Positive**: The finding appears to be incorrect or the code is actually safe
3. **Needs Review**: Uncertain - requires human expert review

Consider the following in your analysis:
- Is the vulnerability actually exploitable in this context?
- Are there mitigating controls or security measures in place?
- Is the code snippet taken out of context?
- Does the finding accurately describe the security risk?
- Is the severity assessment appropriate?

**IMPORTANT**: Return your validation in JSON format ONLY. Do not include any additional text, explanations, or markdown formatting outside the JSON structure.

Required JSON format:
{{
    "verdict": "Confirmed|Likely False Positive|Needs Review",
    "confidence": "High|Medium|Low",
    "rationale": "Detailed explanation of why you reached this verdict, including specific code references and reasoning"
}}

Return ONLY the JSON response. No additional text, no markdown code blocks, just pure JSON."""

        return prompt

    async def apply_rate_limit(self) -> None:
        """Apply rate limiting delay between API requests."""
        if self.rate_limit_delay > 0:
            await asyncio.sleep(self.rate_limit_delay)
