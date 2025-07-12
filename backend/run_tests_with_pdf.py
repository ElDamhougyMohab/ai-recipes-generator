#!/usr/bin/env python3
"""
Simple test runner to generate PDF reports
"""

from generate_test_report import TestReportGenerator

def main():
    """Run tests and generate PDF report"""
    print("🧪 AI Recipe Generator API Test Report Generator")
    print("=" * 50)
    
    generator = TestReportGenerator()
    result = generator.generate_full_report()
    
    print("\n" + "=" * 50)
    print("📊 REPORT GENERATION COMPLETE!")
    print("=" * 50)
    print(f"📄 PDF Report: {result['pdf_report']}")
    print(f"📈 Charts Generated: {len(result['charts'])}")
    print(f"📋 JSON Data: {result['json_data']}")
    
    summary = result['summary']
    print(f"\n📊 TEST SUMMARY:")
    print(f"   Total Tests: {summary['total']}")
    print(f"   ✅ Passed: {summary['passed']}")
    print(f"   ❌ Failed: {summary['failed']}")
    print(f"   ⏭️ Skipped: {summary.get('skipped', 0)}")
    print(f"   🎯 Success Rate: {(summary['passed'] / max(summary['total'], 1)) * 100:.1f}%")
    
    if summary['total'] > 0:
        if summary['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"\n⚠️ {summary['failed']} tests failed. Check the PDF report for details.")
    
    print(f"\n📂 Report files saved in: test_reports/")

if __name__ == "__main__":
    main()
