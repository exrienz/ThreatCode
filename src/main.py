"""Main CLI entry point for ThreatCode security scanner."""
import sys
import click
from pathlib import Path

from src.utils.config import LLMConfig, ScanConfig
from src.scanner.analyzer import CodeAnalyzer
from src.utils.formatters import ReportFormatter


@click.group()
@click.version_option(version="1.0.0", prog_name="ThreatCode")
def cli():
    """ThreatCode - AI-Powered Security Code Scanner.

    Analyze source code for security vulnerabilities using LLM providers.

    Created by exrienz - Part of the ThreatVault.io Ecosystem
    """
    pass


@cli.command()
@click.option(
    '--input', '-i',
    required=True,
    type=click.Path(exists=True),
    help='Input directory or file to scan'
)
@click.option(
    '--output', '-o',
    required=True,
    type=click.Path(),
    help='Output directory for reports'
)
@click.option(
    '--name', '-n',
    default='Application',
    help='Application name for the report'
)
@click.option(
    '--max-file-size',
    default=1048576,
    type=int,
    help='Maximum file size in bytes (default: 1MB)'
)
@click.option(
    '--max-workers',
    default=10,
    type=int,
    help='Maximum number of concurrent workers (default: 10)'
)
def scan(input, output, name, max_file_size, max_workers):
    """Scan source code for security vulnerabilities.

    Examples:

        # Scan with OpenRouter
        export LLM_PROVIDER=openrouter
        export OPENROUTER_API_KEY=sk-...
        export OPENROUTER_MODEL=anthropic/claude-3-haiku
        python -m src.main scan -i /path/to/code -o ./reports -n "MyApp"

        # Scan with OpenAI
        export LLM_PROVIDER=openai
        export OPENAI_API_KEY=sk-...
        export OPENAI_MODEL=gpt-4
        python -m src.main scan -i /path/to/code -o ./reports
    """
    click.echo("=" * 60)
    click.echo("ThreatCode Security Scanner")
    click.echo("=" * 60)

    try:
        # Load LLM configuration from environment
        click.echo("\nLoading configuration...")
        llm_config = LLMConfig.from_env()

        # Create scan configuration
        scan_config = ScanConfig(
            input_path=input,
            output_path=output,
            application_name=name,
            max_file_size=max_file_size,
            max_workers=max_workers
        )

        # Run analysis
        click.echo(f"\nProvider: {llm_config.provider}")
        click.echo(f"Model: {llm_config.model}")
        click.echo(f"Input: {scan_config.input_path}")
        click.echo(f"Output: {scan_config.output_path}")

        analyzer = CodeAnalyzer(scan_config, llm_config)
        report_data = analyzer.run()

        # Generate reports
        click.echo("\nGenerating reports...")
        formatter = ReportFormatter(scan_config.output_path)
        reports = formatter.generate_all_reports(report_data)

        # Summary
        click.echo("\n" + "=" * 60)
        click.echo("SCAN SUMMARY")
        click.echo("=" * 60)
        click.echo(f"Total Findings: {len(report_data.findings)}")
        click.echo(f"  Critical: {report_data.severity_stats.get('Critical', 0)}")
        click.echo(f"  High: {report_data.severity_stats.get('High', 0)}")
        click.echo(f"  Medium: {report_data.severity_stats.get('Medium', 0)}")
        click.echo(f"  Low: {report_data.severity_stats.get('Low', 0)}")
        click.echo(f"  Informational: {report_data.severity_stats.get('Informational', 0)}")

        click.echo("\nReports generated:")
        for format_type, path in reports.items():
            click.echo(f"  {format_type.upper()}: {path}")

        click.echo("\n" + "=" * 60)
        click.echo("Scan completed successfully!")
        click.echo("=" * 60)

        sys.exit(0)

    except ValueError as e:
        click.echo(f"\nConfiguration Error: {e}", err=True)
        click.echo("\nPlease ensure the following environment variables are set:", err=True)
        click.echo("  - LLM_PROVIDER (openrouter, openai, or custom)", err=True)
        click.echo("  - OPENROUTER_API_KEY (for OpenRouter)", err=True)
        click.echo("  - OPENROUTER_MODEL (for OpenRouter)", err=True)
        click.echo("  - OPENAI_API_KEY (for OpenAI)", err=True)
        click.echo("  - OPENAI_MODEL (for OpenAI)", err=True)
        click.echo("  - CUSTOM_API_KEY (for custom provider)", err=True)
        click.echo("  - CUSTOM_MODEL (for custom provider)", err=True)
        click.echo("  - CUSTOM_PROVIDER_URL (for custom provider)", err=True)
        sys.exit(1)

    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("ThreatCode v1.0.0")
    click.echo("AI-Powered Security Code Scanner")


@cli.command()
def providers():
    """List supported LLM providers."""
    click.echo("\nSupported LLM Providers:")
    click.echo("\n1. OpenRouter")
    click.echo("   Base URL: https://openrouter.ai/api/v1")
    click.echo("   Environment variables:")
    click.echo("     - LLM_PROVIDER=openrouter")
    click.echo("     - OPENROUTER_API_KEY=<your-key>")
    click.echo("     - OPENROUTER_MODEL=<model-name>")

    click.echo("\n2. OpenAI")
    click.echo("   Base URL: https://api.openai.com/v1")
    click.echo("   Environment variables:")
    click.echo("     - LLM_PROVIDER=openai")
    click.echo("     - OPENAI_API_KEY=<your-key>")
    click.echo("     - OPENAI_MODEL=<model-name>")

    click.echo("\n3. Custom Provider")
    click.echo("   Custom base URL")
    click.echo("   Environment variables:")
    click.echo("     - LLM_PROVIDER=custom")
    click.echo("     - CUSTOM_API_KEY=<your-key>")
    click.echo("     - CUSTOM_MODEL=<model-name>")
    click.echo("     - CUSTOM_PROVIDER_URL=<base-url>")
    click.echo()


if __name__ == '__main__':
    cli()
