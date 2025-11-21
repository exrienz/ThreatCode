"""Configuration and data models using Pydantic."""
import os
from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""
    provider: Literal["openrouter", "openai", "custom"]
    api_key: str
    model: str
    base_url: Optional[HttpUrl] = None
    timeout: int = Field(default=30, ge=10, le=300)
    rate_limit_delay: float = Field(default=0.5, ge=0, le=10)  # Delay between requests in seconds

    # Allowlist for custom provider URLs (SSRF protection)
    ALLOWED_CUSTOM_DOMAINS: List[str] = Field(default_factory=lambda: [
        "api.openai.com",
        "openrouter.ai",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "localhost",
        "127.0.0.1"
    ])

    @field_validator('base_url')
    @classmethod
    def validate_custom_url(cls, v, info):
        """Ensure base_url is provided for custom provider and validate against allowlist."""
        if info.data.get('provider') == 'custom':
            if not v:
                raise ValueError("base_url is required for custom provider")

            # Check if URL is in allowlist or if ALLOW_ALL_CUSTOM_URLS is set
            allow_all = os.getenv("ALLOW_ALL_CUSTOM_URLS", "false").lower() == "true"

            if not allow_all:
                hostname = v.host if hasattr(v, 'host') else str(v).split('/')[2].split(':')[0]
                allowed_domains = info.data.get('ALLOWED_CUSTOM_DOMAINS', cls.model_fields['ALLOWED_CUSTOM_DOMAINS'].default_factory())

                if hostname not in allowed_domains:
                    raise ValueError(
                        f"Custom provider URL '{hostname}' is not in the allowlist. "
                        f"Allowed domains: {', '.join(allowed_domains)}. "
                        f"To override, set ALLOW_ALL_CUSTOM_URLS=true (not recommended)."
                    )
        return v

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Load configuration from environment variables."""
        provider = os.getenv("LLM_PROVIDER", "openrouter").lower()

        if provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-haiku")
            base_url = None
        elif provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4")
            base_url = None
        elif provider == "custom":
            api_key = os.getenv("CUSTOM_API_KEY")
            model = os.getenv("CUSTOM_MODEL", "default-model")
            custom_url = os.getenv("CUSTOM_PROVIDER_URL")
            if not custom_url:
                raise ValueError("CUSTOM_PROVIDER_URL is required for custom provider")
            base_url = custom_url
        else:
            raise ValueError(f"Invalid provider: {provider}")

        if not api_key:
            raise ValueError(f"API key not found for provider: {provider}")

        # Get optional rate limit delay from environment
        rate_limit_delay = float(os.getenv("RATE_LIMIT_DELAY", "0.5"))

        return cls(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=base_url,
            rate_limit_delay=rate_limit_delay
        )


class Evidence(BaseModel):
    """Evidence for a security finding."""
    file_path: str
    line_number: Optional[int] = None
    code: str  # The vulnerable code snippet
    description: Optional[str] = None  # Additional description for the evidence


class Finding(BaseModel):
    """Security finding from code analysis."""
    title: str
    severity: Literal["Critical", "High", "Medium", "Low", "Informational"]
    description: str
    evidence: List[Evidence] = Field(default_factory=list)
    remediation: str
    cvss_score: Optional[str] = None  # CVSS score like "9.8" or "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    impact: Optional[str] = None  # Can be string or will be converted from list
    attack_scenario: Optional[str] = None  # Description of how the attack could be performed
    references: Optional[List[str]] = Field(default_factory=list)  # URLs or reference materials


class ReportData(BaseModel):
    """Complete report data."""
    application_name: str
    audit_date: datetime = Field(default_factory=datetime.now)
    findings: List[Finding] = Field(default_factory=list)
    severity_stats: Dict[str, int] = Field(default_factory=dict)

    # Optional fields for enhanced reporting
    version: Optional[str] = None
    auditor: Optional[str] = "ThreatCode AI Scanner"
    methodology: Optional[str] = "Automated AI-powered source code security analysis using LLM"
    executive_summary: Optional[str] = None
    conclusion: Optional[str] = None

    def calculate_severity_stats(self) -> None:
        """Calculate severity statistics from findings."""
        self.severity_stats = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
        for finding in self.findings:
            severity_key = finding.severity.lower()
            # Map "Informational" to "info"
            if severity_key == "informational":
                severity_key = "info"
            if severity_key in self.severity_stats:
                self.severity_stats[severity_key] += 1

    def generate_executive_summary(self) -> None:
        """Generate executive summary based on findings."""
        total = len(self.findings)
        if total == 0:
            self.executive_summary = "<p>The automated security scan completed successfully with <strong>no vulnerabilities detected</strong> in the analyzed codebase.</p>"
        else:
            critical = self.severity_stats.get("critical", 0)
            high = self.severity_stats.get("high", 0)
            medium = self.severity_stats.get("medium", 0)
            low = self.severity_stats.get("low", 0)
            info = self.severity_stats.get("info", 0)

            self.executive_summary = f"""<p>The automated security analysis identified <strong>{total} security finding(s)</strong> in the {self.application_name} codebase:</p>
<ul>
<li><strong>Critical:</strong> {critical} issue(s) requiring immediate attention</li>
<li><strong>High:</strong> {high} issue(s) that should be addressed soon</li>
<li><strong>Medium:</strong> {medium} issue(s) requiring review</li>
<li><strong>Low:</strong> {low} minor issue(s)</li>
<li><strong>Informational:</strong> {info} best practice recommendation(s)</li>
</ul>
<p>This report provides detailed findings with remediation guidance for each identified vulnerability.</p>"""

    def generate_conclusion(self) -> None:
        """Generate conclusion based on findings."""
        total = len(self.findings)
        critical = self.severity_stats.get("critical", 0)
        high = self.severity_stats.get("high", 0)

        if total == 0:
            self.conclusion = "<p>The codebase demonstrates good security practices with no vulnerabilities identified during this automated scan. Continue following secure coding practices and perform regular security assessments.</p>"
        elif critical > 0 or high > 0:
            self.conclusion = f"""<p>The analysis identified <strong>{critical + high} critical/high severity</strong> issue(s) that require immediate attention. It is strongly recommended to:</p>
<ul>
<li>Prioritize remediation of Critical and High severity findings</li>
<li>Implement the suggested fixes as outlined in each finding</li>
<li>Conduct code review of the remediated sections</li>
<li>Re-scan the codebase after implementing fixes</li>
<li>Consider implementing automated security scanning in your CI/CD pipeline</li>
</ul>"""
        else:
            self.conclusion = """<p>The codebase shows generally good security practices with primarily medium/low severity findings. Recommendations:</p>
<ul>
<li>Address the identified Medium and Low severity issues during regular maintenance cycles</li>
<li>Review and implement the informational best practice recommendations</li>
<li>Continue regular security assessments</li>
<li>Consider security training for the development team</li>
</ul>"""


class ScanConfig(BaseModel):
    """Configuration for file scanning."""
    input_path: str
    output_path: str
    application_name: str
    max_file_size: int = Field(default=1048576, ge=1024)  # 1MB default
    chunk_size: int = Field(default=51200, ge=1024)  # 50KB default
    batch_size: int = Field(default=102400, ge=1024)  # 100KB default
    max_workers: int = Field(default=10, ge=1, le=20)
    supported_extensions: List[str] = Field(
        default_factory=lambda: [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go",
            ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".hpp"
        ]
    )
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            ".git", "__pycache__", "node_modules", ".venv",
            "venv", "*.min.js", "*.min.css", ".pyc"
        ]
    )
