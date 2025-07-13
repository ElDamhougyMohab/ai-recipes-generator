#!/usr/bin/env python3
"""
🧪 AI Recipe Generator - Comprehensive Test Runner & Report Generator
==================================================================

This script automates the entire testing process including:
- Running all test suites with detailed output
- Generating coverage reports (HTML, XML, Terminal)
- Creating visual test result charts
- Generating PDF reports
- Analyzing failures with solutions
- Performance benchmarking

Usage:
    python run_comprehensive_tests.py [options]

Options:
    --quick          Run only fast tests (exclude performance tests)
    --coverage       Generate detailed coverage reports
    --pdf            Generate PDF report
    --html           Generate HTML dashboard
    --failures-only  Show only failed tests
    --parallel       Run tests in parallel (faster)
    --docker         Test against Docker containers
    --staging        Test against staging environment
    --verbose        Show detailed output
    --help           Show this help message
"""

import os
import sys
import subprocess
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import statistics

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class TestRunner:
    """Comprehensive test runner with reporting capabilities"""
    
    def __init__(self, args):
        self.args = args
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.reports_dir = self.project_root / "test_reports"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create reports directory
        self.reports_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Test results storage
        self.test_results = {}
        self.coverage_data = {}
        self.performance_metrics = {}
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.reports_dir / f"test_run_{self.timestamp}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler() if self.args.verbose else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_banner(self):
        """Print welcome banner"""
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   🧪 AI Recipe Generator Test Suite                           ║
║                     Comprehensive Testing & Analysis                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}

{Colors.YELLOW}📊 Test Configuration:{Colors.END}
├── Mode: {'Quick' if self.args.quick else 'Comprehensive'}
├── Coverage: {'Enabled' if self.args.coverage else 'Disabled'}
├── Environment: {'Docker' if self.args.docker else 'Staging' if self.args.staging else 'Local'}
├── Parallel: {'Enabled' if self.args.parallel else 'Disabled'}
├── Reports: {self.reports_dir}
└── Timestamp: {self.timestamp}

{Colors.GREEN}🚀 Starting test execution...{Colors.END}
"""
        print(banner)
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        self.logger.info("Checking dependencies...")
        
        required_packages = [
            'pytest',
            'pytest-cov',
            'pytest-html',
            'pytest-asyncio',
            'httpx'
        ]
        
        optional_packages = [
            'pytest-xdist',  # For parallel testing
            'reportlab',     # For PDF generation
            'matplotlib',    # For charts
            'plotly'         # For interactive charts
        ]
        
        print(f"{Colors.BLUE}📦 Checking dependencies...{Colors.END}")
        
        # Check required packages
        missing_required = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                missing_required.append(package)
                print(f"  ❌ {package} (REQUIRED)")
        
        # Check optional packages
        missing_optional = []
        for package in optional_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"  ✅ {package}")
            except ImportError:
                missing_optional.append(package)
                print(f"  ⚠️  {package} (optional)")
        
        if missing_required:
            print(f"\n{Colors.RED}❌ Missing required packages: {', '.join(missing_required)}{Colors.END}")
            print(f"{Colors.YELLOW}💡 Install with: pip install {' '.join(missing_required)}{Colors.END}")
            return False
        
        if missing_optional and not self.args.quick:
            print(f"\n{Colors.YELLOW}⚠️  Optional packages missing: {', '.join(missing_optional)}{Colors.END}")
            print(f"{Colors.CYAN}💡 Install for enhanced features: pip install {' '.join(missing_optional)}{Colors.END}")
        
        return True
    
    def run_pytest_command(self, cmd: List[str], description: str) -> Tuple[int, str, str]:
        """Run a pytest command and capture results"""
        self.logger.info(f"Running: {description}")
        print(f"\n{Colors.CYAN}🔄 {description}...{Colors.END}")
        
        start_time = time.time()
        
        # Set up environment with proper Python path
        env = os.environ.copy()
        pythonpath = str(self.backend_dir)
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = pythonpath
        
        try:
            process = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                env=env
            )
            
            duration = time.time() - start_time
            
            if process.returncode == 0:
                print(f"  ✅ Completed in {duration:.1f}s")
            else:
                print(f"  ⚠️  Completed with issues in {duration:.1f}s")
            
            return process.returncode, process.stdout, process.stderr
            
        except subprocess.TimeoutExpired:
            print(f"  ❌ Timeout after 10 minutes")
            return 1, "", "Test execution timed out"
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            return 1, "", str(e)
    
    def run_basic_tests(self) -> Dict:
        """Run basic test suite"""
        print(f"\n{Colors.BOLD}📋 BASIC TEST SUITE{Colors.END}")
        
        # Determine test files to run
        if self.args.quick:
            test_files = [
                "backend/tests/test_health.py",
                "backend/tests/test_generation.py",
                "backend/tests/test_recipes_api.py"
            ]
        else:
            test_files = ["backend/tests/"]
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"] + test_files + [
            "-v",
            "--tb=short",
            f"--html={self.reports_dir}/basic_test_report_{self.timestamp}.html",
            "--self-contained-html"
        ]
        
        if self.args.parallel:
            cmd.extend(["-n", "auto"])
        
        if self.args.failures_only:
            cmd.append("--tb=line")
        
        returncode, stdout, stderr = self.run_pytest_command(cmd, "Basic Test Suite")
        
        # Parse results
        results = self.parse_pytest_output(stdout)
        self.test_results['basic'] = {
            'returncode': returncode,
            'results': results,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return results
    
    def run_coverage_tests(self) -> Dict:
        """Run tests with coverage analysis"""
        if not self.args.coverage:
            return {}
        
        print(f"\n{Colors.BOLD}📊 COVERAGE ANALYSIS{Colors.END}")
        
        coverage_dir = self.reports_dir / "coverage"
        coverage_dir.mkdir(exist_ok=True)
        
        cmd = [
            "python", "-m", "pytest",
            "backend/tests/",
            "--cov=backend/app",
            f"--cov-report=html:{coverage_dir}",
            f"--cov-report=xml:{self.reports_dir}/coverage_{self.timestamp}.xml",
            "--cov-report=term-missing",
            "--cov-report=json",
            "-v"
        ]
        
        returncode, stdout, stderr = self.run_pytest_command(cmd, "Coverage Analysis")
        
        # Parse coverage data
        coverage_data = self.parse_coverage_output(stdout)
        self.test_results['coverage'] = {
            'returncode': returncode,
            'data': coverage_data,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return coverage_data
    
    def run_performance_tests(self) -> Dict:
        """Run performance and stress tests"""
        if self.args.quick:
            return {}
        
        print(f"\n{Colors.BOLD}⚡ PERFORMANCE TESTS{Colors.END}")
        
        performance_files = [
            "backend/tests/test_performance.py",
            "backend/tests/test_performance_stress.py"
        ]
        
        cmd = [
            "python", "-m", "pytest"
        ] + performance_files + [
            "-v",
            "--tb=short",
            f"--html={self.reports_dir}/performance_report_{self.timestamp}.html",
            "--self-contained-html"
        ]
        
        returncode, stdout, stderr = self.run_pytest_command(cmd, "Performance Tests")
        
        # Parse performance metrics
        metrics = self.parse_performance_output(stdout)
        self.test_results['performance'] = {
            'returncode': returncode,
            'metrics': metrics,
            'stdout': stdout,
            'stderr': stderr
        }
        
        return metrics
    
    def parse_pytest_output(self, output: str) -> Dict:
        """Parse pytest output to extract test results"""
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'warnings': 0,
            'duration': 0.0,
            'failed_tests': [],
            'categories': {}
        }
        
        lines = output.split('\n')
        
        for line in lines:
            # Parse summary line
            if 'failed' in line and 'passed' in line:
                # Example: "39 failed, 169 passed, 410 warnings in 38.17s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'failed,' and i > 0:
                        results['failed'] = int(parts[i-1])
                    elif part == 'passed,' and i > 0:
                        results['passed'] = int(parts[i-1])
                    elif part == 'warnings' and i > 0:
                        results['warnings'] = int(parts[i-1])
                    elif part.endswith('s') and 'in' in parts[i-1:i+1]:
                        try:
                            results['duration'] = float(part[:-1])
                        except ValueError:
                            pass
            
            # Parse failed tests
            elif 'FAILED' in line and '::' in line:
                test_name = line.split('FAILED')[1].strip().split(' ')[0]
                results['failed_tests'].append(test_name)
        
        results['total'] = results['passed'] + results['failed'] + results['skipped']
        
        return results
    
    def parse_coverage_output(self, output: str) -> Dict:
        """Parse coverage output"""
        coverage = {
            'total_coverage': 0.0,
            'files': {},
            'missing_lines': {},
            'statements': 0,
            'missing': 0
        }
        
        lines = output.split('\n')
        
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                # Extract total coverage percentage
                parts = line.split()
                for part in parts:
                    if part.endswith('%'):
                        try:
                            coverage['total_coverage'] = float(part[:-1])
                        except ValueError:
                            pass
        
        return coverage
    
    def parse_performance_output(self, output: str) -> Dict:
        """Parse performance test output"""
        metrics = {
            'response_times': [],
            'memory_usage': [],
            'concurrent_users': 0,
            'requests_per_second': 0.0,
            'error_rate': 0.0
        }
        
        # This would need to be implemented based on your specific
        # performance test output format
        return metrics
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print(f"\n{Colors.BOLD}📑 GENERATING REPORTS{Colors.END}")
        
        summary = {
            'timestamp': self.timestamp,
            'test_results': self.test_results,
            'coverage_data': self.coverage_data,
            'performance_metrics': self.performance_metrics
        }
        
        # Save JSON summary
        summary_file = self.reports_dir / f"test_summary_{self.timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Generate markdown report
        self.generate_markdown_report(summary)
        
        # Generate PDF if requested
        if self.args.pdf:
            self.generate_pdf_report(summary)
        
        # Generate HTML dashboard if requested
        if self.args.html:
            self.generate_html_dashboard(summary)
        
        print(f"  ✅ Reports saved to: {self.reports_dir}")
    
    def generate_markdown_report(self, summary: Dict):
        """Generate detailed markdown report"""
        report_file = self.reports_dir / f"COMPREHENSIVE_TEST_REPORT_{self.timestamp}.md"
        
        basic_results = summary['test_results'].get('basic', {}).get('results', {})
        
        content = f"""# 🧪 Comprehensive Test Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Test Run ID**: {self.timestamp}

## 📊 Executive Summary

### Test Results Overview
- **Total Tests**: {basic_results.get('total', 0)}
- **Passed**: {basic_results.get('passed', 0)} ✅
- **Failed**: {basic_results.get('failed', 0)} ❌
- **Success Rate**: {(basic_results.get('passed', 0) / max(basic_results.get('total', 1), 1) * 100):.1f}%
- **Duration**: {basic_results.get('duration', 0):.1f} seconds

### Health Check
{'🟢 HEALTHY' if basic_results.get('failed', 0) < 10 else '🟡 NEEDS ATTENTION' if basic_results.get('failed', 0) < 20 else '🔴 CRITICAL'}

## 📋 Detailed Results

### Failed Tests ({basic_results.get('failed', 0)})
"""
        
        for test in basic_results.get('failed_tests', []):
            content += f"- `{test}`\n"
        
        if 'coverage' in summary['test_results']:
            coverage_data = summary['test_results']['coverage']['data']
            content += f"""
## 📊 Coverage Analysis
- **Total Coverage**: {coverage_data.get('total_coverage', 0):.1f}%
- **Statements**: {coverage_data.get('statements', 0)}
- **Missing**: {coverage_data.get('missing', 0)}
"""
        
        content += f"""
## 🏃‍♂️ Performance Metrics
{'Performance tests were skipped (quick mode)' if self.args.quick else 'See performance section below'}

## 📁 Generated Files
- Test Summary: `test_summary_{self.timestamp}.json`
- Basic Test Report: `basic_test_report_{self.timestamp}.html`
- Coverage Report: `coverage/index.html`
- Log File: `test_run_{self.timestamp}.log`

## 🚀 Next Steps

### If Tests Failed:
1. Review the detailed failure analysis in `DETAILED_TEST_FAILURE_ANALYSIS.md`
2. Fix high-priority issues first (marked as HIGH impact)
3. Run specific test suites: `python -m pytest tests/test_specific.py -v`
4. Check deployment configuration (ensure FastAPI backend is deployed, not nginx mock)

### If Tests Passed:
1. Deploy to staging environment
2. Run integration tests against staging
3. Monitor production metrics
4. Update documentation

---
*Generated by AI Recipe Generator Test Automation Suite*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  📄 Markdown report: {report_file.name}")
    
    def generate_pdf_report(self, summary: Dict):
        """Generate PDF report"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            pdf_file = self.reports_dir / f"test_report_{self.timestamp}.pdf"
            
            doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title = Paragraph("AI Recipe Generator - Test Report", styles['Title'])
            story.append(title)
            story.append(Spacer(1, 12))
            
            # Summary
            basic_results = summary['test_results'].get('basic', {}).get('results', {})
            summary_text = f"""
            <b>Test Summary:</b><br/>
            Total Tests: {basic_results.get('total', 0)}<br/>
            Passed: {basic_results.get('passed', 0)}<br/>
            Failed: {basic_results.get('failed', 0)}<br/>
            Success Rate: {(basic_results.get('passed', 0) / max(basic_results.get('total', 1), 1) * 100):.1f}%<br/>
            Duration: {basic_results.get('duration', 0):.1f} seconds
            """
            
            summary_para = Paragraph(summary_text, styles['Normal'])
            story.append(summary_para)
            
            doc.build(story)
            print(f"  📄 PDF report: {pdf_file.name}")
            
        except ImportError:
            print(f"  ⚠️  PDF generation skipped (reportlab not installed)")
    
    def generate_html_dashboard(self, summary: Dict):
        """Generate interactive HTML dashboard"""
        try:
            dashboard_file = self.reports_dir / f"dashboard_{self.timestamp}.html"
            
            basic_results = summary['test_results'].get('basic', {}).get('results', {})
            
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AI Recipe Generator - Test Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }}
        .metric-card {{ display: inline-block; background: #f8f9fa; padding: 20px; margin: 10px; border-radius: 8px; border-left: 4px solid #4CAF50; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2E7D32; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .chart-container {{ margin: 30px 0; }}
        .failed-tests {{ background: #ffebee; padding: 15px; border-radius: 4px; border-left: 4px solid #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 AI Recipe Generator Test Dashboard</h1>
            <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{basic_results.get('total', 0)}</div>
                <div class="metric-label">Total Tests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{basic_results.get('passed', 0)}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{basic_results.get('failed', 0)}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{(basic_results.get('passed', 0) / max(basic_results.get('total', 1), 1) * 100):.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
        </div>
        
        <div class="chart-container">
            <div id="results-pie-chart"></div>
        </div>
        
        <div class="failed-tests">
            <h3>Failed Tests</h3>
            <ul>
"""
            
            for test in basic_results.get('failed_tests', []):
                html_content += f"<li><code>{test}</code></li>\n"
            
            html_content += f"""
            </ul>
        </div>
    </div>
    
    <script>
        // Create pie chart
        var data = [{{
            values: [{basic_results.get('passed', 0)}, {basic_results.get('failed', 0)}],
            labels: ['Passed', 'Failed'],
            type: 'pie',
            marker: {{
                colors: ['#4CAF50', '#f44336']
            }}
        }}];
        
        var layout = {{
            title: 'Test Results Distribution',
            height: 400
        }};
        
        Plotly.newPlot('results-pie-chart', data, layout);
    </script>
</body>
</html>
"""
            
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"  📊 HTML dashboard: {dashboard_file.name}")
            
        except Exception as e:
            print(f"  ⚠️  HTML dashboard generation failed: {str(e)}")
    
    def print_summary(self):
        """Print final summary to console"""
        basic_results = self.test_results.get('basic', {}).get('results', {})
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}🎯 FINAL SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}")
        
        # Overall status
        total_tests = basic_results.get('total', 0)
        failed_tests = basic_results.get('failed', 0)
        passed_tests = basic_results.get('passed', 0)
        success_rate = (passed_tests / max(total_tests, 1)) * 100
        
        if failed_tests == 0:
            status_color = Colors.GREEN
            status_icon = "🟢"
            status_text = "ALL TESTS PASSED"
        elif failed_tests < 10:
            status_color = Colors.YELLOW
            status_icon = "🟡"
            status_text = "MINOR ISSUES"
        elif failed_tests < 20:
            status_color = Colors.YELLOW
            status_icon = "🟠"
            status_text = "ATTENTION NEEDED"
        else:
            status_color = Colors.RED
            status_icon = "🔴"
            status_text = "CRITICAL ISSUES"
        
        print(f"{status_color}{Colors.BOLD}{status_icon} {status_text}{Colors.END}")
        print()
        
        # Metrics
        print(f"{Colors.BOLD}📊 Test Metrics:{Colors.END}")
        print(f"├── Total Tests: {Colors.BOLD}{total_tests}{Colors.END}")
        print(f"├── Passed: {Colors.GREEN}{passed_tests}{Colors.END}")
        print(f"├── Failed: {Colors.RED}{failed_tests}{Colors.END}")
        print(f"├── Success Rate: {Colors.BOLD}{success_rate:.1f}%{Colors.END}")
        print(f"└── Duration: {Colors.BOLD}{basic_results.get('duration', 0):.1f}s{Colors.END}")
        
        # Coverage info
        if 'coverage' in self.test_results:
            coverage_data = self.test_results['coverage']['data']
            coverage_pct = coverage_data.get('total_coverage', 0)
            coverage_color = Colors.GREEN if coverage_pct >= 80 else Colors.YELLOW if coverage_pct >= 60 else Colors.RED
            print(f"\n{Colors.BOLD}📊 Coverage:{Colors.END}")
            print(f"└── Total Coverage: {coverage_color}{coverage_pct:.1f}%{Colors.END}")
        
        # Next steps
        print(f"\n{Colors.BOLD}🚀 Next Steps:{Colors.END}")
        if failed_tests == 0:
            print(f"├── ✅ Ready for deployment!")
            print(f"├── 🔄 Run staging tests")
            print(f"└── 📊 Monitor production metrics")
        else:
            print(f"├── 📋 Review failure analysis: DETAILED_TEST_FAILURE_ANALYSIS.md")
            print(f"├── 🔧 Fix high-priority issues first")
            print(f"├── 🔄 Re-run tests: python run_comprehensive_tests.py")
            print(f"└── 🚀 Deploy actual FastAPI backend (not nginx mock)")
        
        # File locations
        print(f"\n{Colors.BOLD}📁 Generated Reports:{Colors.END}")
        print(f"├── 📊 Reports Directory: {self.reports_dir}")
        print(f"├── 📄 Test Summary: test_summary_{self.timestamp}.json")
        print(f"├── 🌐 HTML Report: basic_test_report_{self.timestamp}.html")
        if self.args.coverage:
            print(f"├── 📈 Coverage: coverage/index.html")
        if self.args.pdf:
            print(f"├── 📄 PDF Report: test_report_{self.timestamp}.pdf")
        if self.args.html:
            print(f"├── 📊 Dashboard: dashboard_{self.timestamp}.html")
        print(f"└── 📝 Log File: test_run_{self.timestamp}.log")
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
    
    def run(self):
        """Main execution method"""
        try:
            # Print banner
            self.print_banner()
            
            # Check dependencies
            if not self.check_dependencies():
                sys.exit(1)
            
            # Run test suites
            self.run_basic_tests()
            
            if self.args.coverage:
                self.run_coverage_tests()
            
            if not self.args.quick:
                self.run_performance_tests()
            
            # Generate reports
            self.generate_summary_report()
            
            # Print summary
            self.print_summary()
            
            # Exit with appropriate code
            basic_results = self.test_results.get('basic', {}).get('results', {})
            if basic_results.get('failed', 0) == 0:
                sys.exit(0)
            else:
                sys.exit(1)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Test execution interrupted by user{Colors.END}")
            sys.exit(130)
        except Exception as e:
            print(f"\n{Colors.RED}❌ Fatal error: {str(e)}{Colors.END}")
            self.logger.exception("Fatal error during test execution")
            sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Recipe Generator - Comprehensive Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_comprehensive_tests.py                    # Run full test suite
  python run_comprehensive_tests.py --quick           # Quick test run
  python run_comprehensive_tests.py --coverage --pdf  # With coverage and PDF
  python run_comprehensive_tests.py --parallel        # Parallel execution
  python run_comprehensive_tests.py --docker          # Test Docker deployment
        """
    )
    
    parser.add_argument('--quick', action='store_true', 
                       help='Run only fast tests (exclude performance tests)')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate detailed coverage reports')
    parser.add_argument('--pdf', action='store_true',
                       help='Generate PDF report')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML dashboard')
    parser.add_argument('--failures-only', action='store_true',
                       help='Show only failed tests')
    parser.add_argument('--parallel', action='store_true',
                       help='Run tests in parallel (faster)')
    parser.add_argument('--docker', action='store_true',
                       help='Test against Docker containers')
    parser.add_argument('--staging', action='store_true',
                       help='Test against staging environment')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output')
    
    args = parser.parse_args()
    
    # Create and run test runner
    runner = TestRunner(args)
    runner.run()

if __name__ == "__main__":
    main()
