"""Core analysis module that coordinates scanning."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List
from tqdm import tqdm

from src.scanner.file_collector import FileCollector
from src.scanner.providers.base import BaseLLMProvider
from src.scanner.providers.openrouter import OpenRouterProvider
from src.scanner.providers.openai import OpenAIProvider
from src.utils.config import Finding, LLMConfig, ReportData, ScanConfig


class CodeAnalyzer:
    """Coordinates code analysis using LLM providers."""

    def __init__(self, scan_config: ScanConfig, llm_config: LLMConfig):
        """Initialize the analyzer.

        Args:
            scan_config: Scan configuration
            llm_config: LLM provider configuration
        """
        self.scan_config = scan_config
        self.llm_config = llm_config
        self.provider = self._create_provider()
        self.file_collector = FileCollector(scan_config)

    def _create_provider(self) -> BaseLLMProvider:
        """Create appropriate LLM provider based on config.

        Returns:
            Initialized provider instance
        """
        if self.llm_config.provider == "openrouter":
            return OpenRouterProvider(
                api_key=self.llm_config.api_key,
                model=self.llm_config.model,
                timeout=self.llm_config.timeout,
                rate_limit_delay=self.llm_config.rate_limit_delay
            )
        elif self.llm_config.provider == "openai":
            return OpenAIProvider(
                api_key=self.llm_config.api_key,
                model=self.llm_config.model,
                timeout=self.llm_config.timeout,
                rate_limit_delay=self.llm_config.rate_limit_delay
            )
        elif self.llm_config.provider == "custom":
            # For custom provider, extend OpenRouterProvider with custom URL
            provider = OpenRouterProvider(
                api_key=self.llm_config.api_key,
                model=self.llm_config.model,
                timeout=self.llm_config.timeout,
                rate_limit_delay=self.llm_config.rate_limit_delay
            )
            # Override base URL
            provider.BASE_URL = str(self.llm_config.base_url).rstrip('/')
            return provider
        else:
            raise ValueError(f"Unknown provider: {self.llm_config.provider}")

    async def analyze(self) -> ReportData:
        """Run the complete analysis.

        Returns:
            Report data with findings
        """
        print(f"Starting scan of: {self.scan_config.input_path}")
        print(f"Using provider: {self.llm_config.provider} with model: {self.llm_config.model}")

        # Collect files
        print("\nCollecting files...")
        files = self.file_collector.collect_files()
        print(f"Found {len(files)} files to analyze")

        if not files:
            print("No files found to analyze")
            return ReportData(
                application_name=self.scan_config.application_name,
                findings=[]
            )

        # Create batches
        batches = self.file_collector.create_batches(files)
        print(f"Created {len(batches)} batches for processing")

        # Process batches
        all_findings = []
        print("\nAnalyzing code...")

        with tqdm(total=len(batches), desc="Processing batches") as pbar:
            # Process batches with limited concurrency
            semaphore = asyncio.Semaphore(self.scan_config.max_workers)

            async def process_batch_with_semaphore(batch):
                async with semaphore:
                    findings = await self._process_batch(batch)
                    pbar.update(1)
                    return findings

            tasks = [process_batch_with_semaphore(batch) for batch in batches]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    print(f"Warning: Batch processing error: {result}")
                elif result:
                    all_findings.extend(result)

        print(f"\nAnalysis complete. Found {len(all_findings)} security issues.")

        # Create report
        report = ReportData(
            application_name=self.scan_config.application_name,
            findings=all_findings
        )
        report.calculate_severity_stats()
        report.generate_executive_summary()
        report.generate_conclusion()

        return report

    async def _process_batch(self, batch: List[Path]) -> List[Finding]:
        """Process a batch of files.

        Args:
            batch: List of file paths

        Returns:
            List of findings from the batch
        """
        findings = []

        # Combine files in the batch
        combined_code = []
        file_paths = []

        for file_path in batch:
            chunks = self.file_collector.read_file_chunked(file_path)
            for chunk_content, start_line in chunks:
                # Add file marker
                relative_path = file_path.relative_to(Path(self.scan_config.input_path))
                combined_code.append(f"\n# File: {relative_path} (starting at line {start_line})\n")
                combined_code.append(chunk_content)
                file_paths.append(str(relative_path))

        if not combined_code:
            return findings

        code_chunk = ''.join(combined_code)
        context = {
            'file_paths': list(set(file_paths)),
            'batch_size': len(batch)
        }

        try:
            batch_findings = await self.provider.analyze_code(code_chunk, context)
            findings.extend(batch_findings)
        except Exception as e:
            print(f"Warning: Error analyzing batch: {e}")

        return findings

    def run(self) -> ReportData:
        """Synchronous wrapper for running the analysis.

        Returns:
            Report data with findings
        """
        return asyncio.run(self.analyze())
