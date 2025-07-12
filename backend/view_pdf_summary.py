#!/usr/bin/env python3
"""
Quick script to show what's in the latest PDF report
"""

import os
import json
from pathlib import Path


def show_latest_report_summary():
    """Show summary of the latest test report"""
    test_reports_dir = Path("test_reports")

    if not test_reports_dir.exists():
        print("❌ No test reports directory found.")
        return

    # Find the latest JSON data file
    json_files = list(test_reports_dir.glob("test_data_*.json"))
    if not json_files:
        print("❌ No test data files found.")
        return

    latest_json = max(json_files, key=os.path.getctime)
    print(f"📄 Latest Report: {latest_json.name}")
    print("=" * 60)

    try:
        with open(latest_json, "r") as f:
            data = json.load(f)

        summary = data.get("summary", {})
        print(f"📊 TEST SUMMARY:")
        print(f"   Total Tests: {summary.get('total', 0)}")
        print(f"   ✅ Passed: {summary.get('passed', 0)}")
        print(f"   ❌ Failed: {summary.get('failed', 0)}")
        print(f"   ⏭️ Skipped: {summary.get('skipped', 0)}")
        print(
            f"   🎯 Success Rate: {(summary.get('passed', 0) / max(summary.get('total', 1), 1)) * 100:.1f}%"
        )
        print()

        # Show failed tests
        failed_tests = [
            test for test in data.get("tests", []) if test.get("outcome") == "failed"
        ]
        if failed_tests:
            print(f"❌ FAILED TESTS ({len(failed_tests)}):")
            print("-" * 40)
            for test in failed_tests[:10]:  # Show first 10 failed tests
                test_name = test["nodeid"].split("::")[-1]
                file_name = test["nodeid"].split("::")[0]
                print(f"   📁 {file_name}")
                print(f"   🔧 {test_name}")

                # Try to get error message
                if "call" in test and "longrepr" in test["call"]:
                    longrepr = test["call"]["longrepr"]
                    if isinstance(longrepr, str):
                        lines = longrepr.split("\n")
                        for line in lines:
                            if "Error:" in line or "Exception:" in line:
                                print(f"   ⚠️  {line.strip()}")
                                break
                print()

            if len(failed_tests) > 10:
                print(f"   ... and {len(failed_tests) - 10} more failed tests")
                print()

        # Show some passed tests for context
        passed_tests = [
            test for test in data.get("tests", []) if test.get("outcome") == "passed"
        ]
        if passed_tests:
            print(f"✅ SAMPLE PASSED TESTS ({len(passed_tests)} total):")
            print("-" * 40)
            for test in passed_tests[:5]:  # Show first 5 passed tests
                test_name = test["nodeid"].split("::")[-1]
                file_name = test["nodeid"].split("::")[0]
                duration = test.get("call", {}).get("duration", 0)
                print(f"   📁 {file_name}")
                print(f"   ✅ {test_name} ({duration:.3f}s)")
                print()

        print("=" * 60)
        print(f"📋 Full detailed report available in:")
        pdf_file = latest_json.name.replace("test_data_", "test_report_").replace(
            ".json", ".pdf"
        )
        print(f"   📄 {test_reports_dir / pdf_file}")
        print()
        print("📊 The PDF report includes:")
        print("   • Detailed test descriptions and purposes")
        print("   • Exact failure points and error messages")
        print("   • Stack traces for debugging")
        print("   • Visual charts and graphs")
        print("   • Environment information")

    except Exception as e:
        print(f"❌ Error reading report: {e}")


if __name__ == "__main__":
    show_latest_report_summary()
