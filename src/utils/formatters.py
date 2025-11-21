"""Report formatting and generation utilities."""
import csv
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from src.utils.config import ReportData


class ReportFormatter:
    """Generate reports in various formats."""

    def __init__(self, output_path: str):
        """Initialize the formatter.

        Args:
            output_path: Directory to write reports
        """
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Set up Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_html_report(self, report_data: ReportData, filename: str = "report.html") -> Path:
        """Generate HTML report.

        Args:
            report_data: Report data to format
            filename: Output filename

        Returns:
            Path to generated report
        """
        try:
            template = self.jinja_env.get_template("report.html")
            html_content = template.render(
                report_title="Security Audit Report",
                application_name=report_data.application_name,
                audit_date=report_data.audit_date.strftime("%Y-%m-%d %H:%M:%S"),
                version=report_data.version,
                auditor=report_data.auditor,
                methodology=report_data.methodology,
                executive_summary=report_data.executive_summary,
                severity_stats=report_data.severity_stats,
                findings=report_data.findings,
                conclusion=report_data.conclusion,
                footer_text="Security Audit Report - ThreatCode-Review",
                confidentiality_notice="This report is confidential and intended for internal use only."
            )

            output_file = self.output_path / filename
            output_file.write_text(html_content, encoding='utf-8')
            return output_file
        except Exception as e:
            # Fallback to plain text if template rendering fails
            print(f"Warning: HTML template failed ({e}), falling back to plain text report")
            return self.generate_text_report(report_data, filename.replace('.html', '.txt'))

    def generate_csv_report(self, report_data: ReportData, filename: str = "report.csv") -> Path:
        """Generate CSV report in vulnerability scanner format.

        Args:
            report_data: Report data to format
            filename: Output filename

        Returns:
            Path to generated report
        """
        output_file = self.output_path / filename

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'CVE',
                'Risk',
                'Host',
                'Port',
                'Name',
                'Description',
                'Solution',
                'Plugin Output',
                'VPR Score'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for finding in report_data.findings:
                # Collect all plugin output (evidence code snippets)
                plugin_output = []
                for evidence in finding.evidence:
                    if evidence.file_path:
                        plugin_output.append(f"File: {evidence.file_path}")
                        if evidence.line_number:
                            plugin_output.append(f"Line: {evidence.line_number}")
                    if evidence.code:
                        plugin_output.append(f"Code:\n{evidence.code}")
                    plugin_output.append("---")

                writer.writerow({
                    'CVE': '',  # No CVE for custom findings
                    'Risk': finding.severity,
                    'Host': report_data.application_name,
                    'Port': '0',  # Not applicable for source code analysis
                    'Name': finding.title,
                    'Description': finding.description,
                    'Solution': finding.remediation,
                    'Plugin Output': '\n'.join(plugin_output) if plugin_output else '',
                    'VPR Score': '0'  # Vulnerability Priority Rating not applicable
                })

        return output_file

    def generate_json_report(self, report_data: ReportData, filename: str = "report.json") -> Path:
        """Generate JSON report.

        Args:
            report_data: Report data to format
            filename: Output filename

        Returns:
            Path to generated report
        """
        output_file = self.output_path / filename
        json_content = report_data.model_dump_json(indent=2)
        output_file.write_text(json_content, encoding='utf-8')
        return output_file

    def generate_text_report(self, report_data: ReportData, filename: str = "report.txt") -> Path:
        """Generate plain text report (fallback when templates fail).

        Args:
            report_data: Report data to format
            filename: Output filename

        Returns:
            Path to generated report
        """
        output_file = self.output_path / filename

        lines = []
        lines.append("=" * 80)
        lines.append(f"SECURITY ANALYSIS REPORT - {report_data.application_name}")
        lines.append("=" * 80)
        lines.append(f"Scan Date: {report_data.audit_date.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary statistics
        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total Findings: {len(report_data.findings)}")
        lines.append(f"  Critical: {report_data.severity_stats.get('Critical', 0)}")
        lines.append(f"  High: {report_data.severity_stats.get('High', 0)}")
        lines.append(f"  Medium: {report_data.severity_stats.get('Medium', 0)}")
        lines.append(f"  Low: {report_data.severity_stats.get('Low', 0)}")
        lines.append(f"  Informational: {report_data.severity_stats.get('Informational', 0)}")
        lines.append("")

        # Detailed findings
        if report_data.findings:
            lines.append("DETAILED FINDINGS")
            lines.append("=" * 80)
            lines.append("")

            for i, finding in enumerate(report_data.findings, 1):
                lines.append(f"Finding #{i}: {finding.title}")
                lines.append(f"Severity: {finding.severity}")
                lines.append("-" * 80)
                lines.append(f"Description: {finding.description}")
                lines.append("")

                if finding.evidence:
                    lines.append("Evidence:")
                    for ev in finding.evidence:
                        lines.append(f"  File: {ev.file_path}")
                        lines.append(f"  Line: {ev.line_number}")
                        lines.append(f"  Code: {ev.code}")
                        lines.append("")

                lines.append(f"Remediation: {finding.remediation}")
                lines.append("")
                lines.append("=" * 80)
                lines.append("")
        else:
            lines.append("No security issues found.")
            lines.append("")

        lines.append("=" * 80)
        lines.append("Generated by ThreatCode-Review Security Scanner")
        lines.append("=" * 80)

        output_file.write_text('\n'.join(lines), encoding='utf-8')
        return output_file

    def generate_all_reports(self, report_data: ReportData) -> dict:
        """Generate reports in all formats.

        Args:
            report_data: Report data to format

        Returns:
            Dictionary mapping format to output path
        """
        reports = {}

        try:
            reports['html'] = self.generate_html_report(report_data)
            print(f"HTML report generated: {reports['html']}")
        except Exception as e:
            print(f"Error generating HTML report: {e}")

        try:
            reports['csv'] = self.generate_csv_report(report_data)
            print(f"CSV report generated: {reports['csv']}")
        except Exception as e:
            print(f"Error generating CSV report: {e}")

        try:
            reports['json'] = self.generate_json_report(report_data)
            print(f"JSON report generated: {reports['json']}")
        except Exception as e:
            print(f"Error generating JSON report: {e}")

        return reports
