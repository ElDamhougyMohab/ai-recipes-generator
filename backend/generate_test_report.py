#!/usr/bin/env python3
"""
Test Report Generator for AI Recipe Generator APIs
Generates comprehensive PDF and HTML reports of test results
"""

import os
import sys
import json
import subprocess
import datetime
import re
from pathlib import Path
from typing import Dict, List, Any

import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class TestReportGenerator:
    """Generate comprehensive test reports in PDF and HTML formats"""

    def __init__(self, output_dir: str = "test_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize styles
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            "CustomTitle",
            parent=self.styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
        )
        self.heading_style = ParagraphStyle(
            "CustomHeading",
            parent=self.styles["Heading2"],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkgreen,
        )
        self.subheading_style = ParagraphStyle(
            "CustomSubHeading",
            parent=self.styles["Heading3"],
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkblue,
        )
        self.normal_style = ParagraphStyle(
            "CustomNormal", parent=self.styles["Normal"], fontSize=10, spaceAfter=6
        )

    def run_tests_with_json_output(self) -> Dict[str, Any]:
        """Run pytest and capture results in JSON format"""
        print("🧪 Running comprehensive test suite...")

        # Run tests with JSON output
        json_file = self.output_dir / f"test_results_{self.timestamp}.json"
        html_file = self.output_dir / f"test_results_{self.timestamp}.html"

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            f"--html={html_file}",
            "--self-contained-html",
            f"--json-report",
            f"--json-report-file={json_file}",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=os.getcwd()
            )
            print(f"✅ Tests completed. Exit code: {result.returncode}")

            # Try to load JSON results if pytest-json-report is available
            if json_file.exists():
                with open(json_file, "r") as f:
                    return json.load(f)
            else:
                # Fallback: parse pytest output manually
                return self._parse_pytest_output(
                    result.stdout, result.stderr, result.returncode
                )

        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return self._create_error_report(str(e))

    def _parse_pytest_output(
        self, stdout: str, stderr: str, exit_code: int
    ) -> Dict[str, Any]:
        """Parse pytest output when JSON report is not available"""
        lines = stdout.split("\n")

        # Extract test results
        tests = []
        summary_line = ""

        for line in lines:
            if "::" in line and (
                " PASSED" in line or " FAILED" in line or " SKIPPED" in line
            ):
                parts = line.split("::")
                if len(parts) >= 2:
                    test_file = parts[0].strip()
                    test_info = parts[1].strip()

                    if " PASSED" in test_info:
                        status = "passed"
                        test_name = test_info.replace(" PASSED", "")
                    elif " FAILED" in test_info:
                        status = "failed"
                        test_name = test_info.replace(" FAILED", "")
                    elif " SKIPPED" in test_info:
                        status = "skipped"
                        test_name = test_info.replace(" SKIPPED", "")
                    else:
                        continue

                    tests.append(
                        {
                            "nodeid": f"{test_file}::{test_name}",
                            "outcome": status,
                            "setup": {"outcome": status},
                            "call": {"outcome": status},
                            "teardown": {"outcome": status},
                        }
                    )

            if " failed" in line and " passed" in line:
                summary_line = line

        # Count results
        passed = len([t for t in tests if t["outcome"] == "passed"])
        failed = len([t for t in tests if t["outcome"] == "failed"])
        skipped = len([t for t in tests if t["outcome"] == "skipped"])
        total = len(tests)

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "duration": 0,
                "outcome": "failed" if failed > 0 else "passed",
            },
            "tests": tests,
            "environment": {
                "Python": sys.version,
                "Platform": sys.platform,
                "Packages": {},
            },
            "created": datetime.datetime.now().isoformat(),
        }

    def _create_error_report(self, error_msg: str) -> Dict[str, Any]:
        """Create error report when tests can't be run"""
        return {
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": 0,
                "outcome": "error",
                "error": error_msg,
            },
            "tests": [],
            "environment": {"Python": sys.version, "Platform": sys.platform},
            "created": datetime.datetime.now().isoformat(),
        }

    def create_charts(self, test_data: Dict[str, Any]) -> List[str]:
        """Create charts for the test report"""
        chart_files = []

        summary = test_data["summary"]

        # Set style
        plt.style.use("seaborn-v0_8")

        # 1. Pie chart of test results
        fig, ax = plt.subplots(figsize=(8, 6))
        sizes = [
            summary.get("passed", 0),
            summary.get("failed", 0),
            summary.get("skipped", 0),
        ]
        labels = ["Passed", "Failed", "Skipped"]
        colors_pie = ["#28a745", "#dc3545", "#ffc107"]

        # Filter out zero values
        non_zero_data = [
            (size, label, color)
            for size, label, color in zip(sizes, labels, colors_pie)
            if size > 0
        ]
        if non_zero_data:
            sizes_filtered, labels_filtered, colors_filtered = zip(*non_zero_data)
            wedges, texts, autotexts = ax.pie(
                sizes_filtered,
                labels=labels_filtered,
                colors=colors_filtered,
                autopct="%1.1f%%",
                startangle=90,
            )
            ax.set_title("Test Results Distribution", fontsize=16, fontweight="bold")
        else:
            ax.text(
                0.5,
                0.5,
                "No test data available",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
            ax.set_title("Test Results Distribution", fontsize=16, fontweight="bold")

        pie_chart_path = self.output_dir / f"test_results_pie_{self.timestamp}.png"
        plt.savefig(pie_chart_path, dpi=300, bbox_inches="tight")
        plt.close()
        chart_files.append(str(pie_chart_path))

        # 2. Bar chart by test file
        if test_data["tests"]:
            test_files = {}
            for test in test_data["tests"]:
                file_name = (
                    test["nodeid"]
                    .split("::")[0]
                    .replace("tests/", "")
                    .replace(".py", "")
                )
                if file_name not in test_files:
                    test_files[file_name] = {"passed": 0, "failed": 0, "skipped": 0}
                test_files[file_name][test["outcome"]] += 1

            if test_files:
                fig, ax = plt.subplots(figsize=(12, 6))
                files = list(test_files.keys())
                passed_counts = [test_files[f]["passed"] for f in files]
                failed_counts = [test_files[f]["failed"] for f in files]
                skipped_counts = [test_files[f]["skipped"] for f in files]

                x = range(len(files))
                width = 0.25

                ax.bar(
                    [i - width for i in x],
                    passed_counts,
                    width,
                    label="Passed",
                    color="#28a745",
                )
                ax.bar(x, failed_counts, width, label="Failed", color="#dc3545")
                ax.bar(
                    [i + width for i in x],
                    skipped_counts,
                    width,
                    label="Skipped",
                    color="#ffc107",
                )

                ax.set_xlabel("Test Files")
                ax.set_ylabel("Number of Tests")
                ax.set_title("Test Results by File")
                ax.set_xticks(x)
                ax.set_xticklabels(files, rotation=45, ha="right")
                ax.legend()

                bar_chart_path = (
                    self.output_dir / f"test_results_bar_{self.timestamp}.png"
                )
                plt.tight_layout()
                plt.savefig(bar_chart_path, dpi=300, bbox_inches="tight")
                plt.close()
                chart_files.append(str(bar_chart_path))

        return chart_files

    def generate_pdf_report(
        self, test_data: Dict[str, Any], chart_files: List[str]
    ) -> str:
        """Generate comprehensive PDF report"""
        pdf_file = self.output_dir / f"test_report_{self.timestamp}.pdf"
        doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
        story = []

        summary = test_data["summary"]

        # Title
        story.append(Paragraph("AI Recipe Generator API", self.title_style))
        story.append(Paragraph("Comprehensive Test Report", self.title_style))
        story.append(Spacer(1, 12))

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.heading_style))

        summary_data = [
            ["Metric", "Value"],
            ["Total Tests", str(summary["total"])],
            ["Passed", str(summary["passed"])],
            ["Failed", str(summary["failed"])],
            ["Skipped", str(summary.get("skipped", 0))],
            [
                "Success Rate",
                f"{(summary['passed'] / max(summary['total'], 1)) * 100:.1f}%",
            ],
            ["Test Duration", f"{summary.get('duration', 0):.2f}s"],
            ["Overall Result", summary.get("outcome", "unknown").upper()],
            ["Generated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # Add charts
        for chart_file in chart_files:
            if os.path.exists(chart_file):
                img = Image(chart_file, width=6 * inch, height=4 * inch)
                story.append(img)
                story.append(Spacer(1, 12))

        # Test Details
        story.append(Paragraph("📋 Detailed Test Results", self.heading_style))

        if test_data["tests"]:
            # Group tests by file
            test_by_file = {}
            for test in test_data["tests"]:
                file_name = test["nodeid"].split("::")[0]
                if file_name not in test_by_file:
                    test_by_file[file_name] = []
                test_by_file[file_name].append(test)

            for file_name, tests in test_by_file.items():
                story.append(Paragraph(f"📁 File: {file_name}", self.subheading_style))

                for test in tests:
                    test_name = test["nodeid"].split("::")[-1]
                    status = test["outcome"].upper()
                    duration = test.get("call", {}).get("duration", 0)

                    # Get test description
                    description = self._extract_test_documentation(file_name, test_name)

                    # Create test case header
                    if status == "PASSED":
                        status_icon = "✅"
                        status_color = colors.green
                    elif status == "FAILED":
                        status_icon = "❌"
                        status_color = colors.red
                    else:
                        status_icon = "⏭️"
                        status_color = colors.orange

                    # Test case summary
                    test_header = f"{status_icon} <b>{test_name}</b> ({duration:.3f}s)"
                    story.append(Paragraph(test_header, self.normal_style))

                    # Test description
                    if description != "Test description not available":
                        story.append(
                            Paragraph(
                                f"<b>Purpose:</b> {description}", self.normal_style
                            )
                        )

                    # Failure details for failed tests
                    if status == "FAILED":
                        failure_details = self._extract_failure_details(test)

                        story.append(
                            Paragraph(
                                f"<b>❌ Failure Stage:</b> {failure_details['stage'].title()}",
                                self.normal_style,
                            )
                        )
                        story.append(
                            Paragraph(
                                f"<b>Error Type:</b> {failure_details['error_type']}",
                                self.normal_style,
                            )
                        )
                        story.append(
                            Paragraph(
                                f"<b>Error Message:</b> {failure_details['error_message']}",
                                self.normal_style,
                            )
                        )

                        # Add stack trace if available (truncated for readability)
                        if failure_details["stack_trace"]:
                            trace_lines = failure_details["stack_trace"].split("\n")
                            # Show only the most relevant parts of the stack trace
                            relevant_lines = []
                            for line in trace_lines[
                                -10:
                            ]:  # Last 10 lines are usually most relevant
                                if line.strip() and not line.startswith("="):
                                    relevant_lines.append(line.strip())

                            if relevant_lines:
                                story.append(
                                    Paragraph(
                                        "<b>Stack Trace (excerpt):</b>",
                                        self.normal_style,
                                    )
                                )
                                trace_text = "<br/>".join(
                                    relevant_lines[:5]
                                )  # Limit to 5 lines
                                story.append(
                                    Paragraph(
                                        f"<font name='Courier' size='8'>{trace_text}</font>",
                                        self.normal_style,
                                    )
                                )

                    story.append(Spacer(1, 8))

                story.append(Spacer(1, 12))

        # Environment Information
        story.append(Paragraph("Environment Information", self.heading_style))
        env_data = [
            [
                "Python Version",
                test_data.get("environment", {}).get("Python", "Unknown"),
            ],
            ["Platform", test_data.get("environment", {}).get("Platform", "Unknown")],
            ["Test Framework", "pytest"],
            ["Report Generated", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ]

        env_table = Table(env_data, colWidths=[2 * inch, 4 * inch])
        env_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(env_table)

        # Build PDF
        doc.build(story)
        print(f"📊 PDF report generated: {pdf_file}")
        return str(pdf_file)

    def generate_full_report(self) -> Dict[str, str]:
        """Generate complete test report with PDF and charts"""
        print("🚀 Generating comprehensive test report...")

        # Run tests
        test_data = self.run_tests_with_json_output()

        # Create charts
        chart_files = self.create_charts(test_data)

        # Generate PDF
        pdf_file = self.generate_pdf_report(test_data, chart_files)

        # Save JSON data for reference
        json_file = self.output_dir / f"test_data_{self.timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(test_data, f, indent=2)

        result = {
            "pdf_report": pdf_file,
            "json_data": str(json_file),
            "charts": chart_files,
            "summary": test_data["summary"],
        }

        print("📈 Test report generation complete!")
        print(f"📄 PDF Report: {pdf_file}")
        print(f"📊 Charts: {len(chart_files)} generated")
        print(f"✅ Passed: {test_data['summary']['passed']}")
        print(f"❌ Failed: {test_data['summary']['failed']}")
        print(f"⏭️ Skipped: {test_data['summary'].get('skipped', 0)}")

        return result

    def _extract_test_documentation(self, test_file_path: str, test_name: str) -> str:
        """Extract docstring or comments from test method"""
        try:
            full_path = os.path.join(os.getcwd(), test_file_path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Look for the test method
                pattern = rf'def {re.escape(test_name)}\([^)]*\):\s*"""([^"]*?)"""'
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    return match.group(1).strip()

                # Look for single-line docstring
                pattern = rf'def {re.escape(test_name)}\([^)]*\):\s*"([^"]*)"'
                match = re.search(pattern, content)
                if match:
                    return match.group(1).strip()

                # Look for comment on the line before
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if f"def {test_name}(" in line and i > 0:
                        prev_line = lines[i - 1].strip()
                        if prev_line.startswith("#"):
                            return prev_line[1:].strip()

        except Exception:
            pass
        return "Test description not available"

    def _extract_failure_details(self, test: Dict[str, Any]) -> Dict[str, str]:
        """Extract detailed failure information from test result"""
        failure_info = {
            "stage": "unknown",
            "error_type": "unknown",
            "error_message": "No error details available",
            "stack_trace": "",
        }

        # Check different stages of test execution
        for stage in ["setup", "call", "teardown"]:
            if stage in test and test[stage].get("outcome") == "failed":
                failure_info["stage"] = stage
                if "longrepr" in test[stage]:
                    longrepr = test[stage]["longrepr"]
                    if isinstance(longrepr, str):
                        lines = longrepr.split("\n")
                        # Extract error type and message
                        for line in lines:
                            if "Error:" in line or "Exception:" in line:
                                failure_info["error_type"] = line.split(":")[0].strip()
                                failure_info["error_message"] = ":".join(
                                    line.split(":")[1:]
                                ).strip()
                                break
                        failure_info["stack_trace"] = longrepr
                    elif isinstance(longrepr, dict) and "reprcrash" in longrepr:
                        crash = longrepr["reprcrash"]
                        failure_info["error_message"] = crash.get(
                            "message", "Unknown error"
                        )
                        failure_info["error_type"] = crash.get("path", "").split(".")[
                            -1
                        ]
                break

        return failure_info


def main():
    """Main function to generate test reports"""
    generator = TestReportGenerator()
    result = generator.generate_full_report()
    return result


if __name__ == "__main__":
    main()
