#!/usr/bin/env python3
"""
Main test execution script for Live Graph System
Provides multiple testing modes and comprehensive reporting
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import json
import time

def install_test_dependencies():
    """Install test dependencies"""
    print("📦 Installing test dependencies...")
    
    requirements_file = Path("tests/requirements-test.txt")
    if requirements_file.exists():
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True)
            print("✅ Test dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install test dependencies: {e}")
            return False
    else:
        print("⚠️  Test requirements file not found, installing basic dependencies...")
        basic_deps = ["pytest", "pytest-cov", "coverage", "requests", "beautifulsoup4", "flask"]
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + basic_deps, check=True, capture_output=True)
            print("✅ Basic test dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install basic dependencies: {e}")
            return False

def run_quick_tests():
    """Run quick unit tests only"""
    print("🏃‍♂️ Running Quick Tests (Unit Tests Only)")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    return subprocess.run(cmd).returncode == 0

def run_comprehensive_tests():
    """Run comprehensive test suite"""
    print("🔬 Running Comprehensive Test Suite")
    
    cmd = [
        sys.executable, "tests/test_runner.py"
    ]
    
    return subprocess.run(cmd).returncode == 0

def run_coverage_only():
    """Run coverage analysis only"""
    print("📊 Running Coverage Analysis")
    
    cmd = [
        sys.executable, "tests/test_runner.py", "--coverage-only"
    ]
    
    return subprocess.run(cmd).returncode == 0

def run_performance_tests():
    """Run performance tests"""
    print("⚡ Running Performance Tests")
    
    cmd = [
        sys.executable, "tests/test_runner.py", "--performance"
    ]
    
    return subprocess.run(cmd).returncode == 0

def run_e2e_tests():
    """Run end-to-end tests"""
    print("🌐 Running End-to-End Tests")
    
    cmd = [
        sys.executable, "tests/test_runner.py", "--e2e"
    ]
    
    return subprocess.run(cmd).returncode == 0

def run_all_tests():
    """Run all tests including performance and e2e"""
    print("🚀 Running All Tests (Including Performance and E2E)")
    
    cmd = [
        sys.executable, "tests/test_runner.py", "--performance", "--e2e"
    ]
    
    return subprocess.run(cmd).returncode == 0

def run_pytest_mode():
    """Run tests using pytest directly"""
    print("🧪 Running Tests with Pytest")
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=backend",
        "--cov-report=html:tests/coverage_html",
        "--cov-report=term-missing",
        "--html=tests/pytest_report.html",
        "--self-contained-html"
    ]
    
    return subprocess.run(cmd).returncode == 0

def validate_test_environment():
    """Validate that the test environment is properly set up"""
    print("🔍 Validating Test Environment...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print(f"✅ Python version: {sys.version}")
    
    # Check project structure
    required_dirs = [
        "backend/core",
        "backend/interfaces", 
        "backend/config",
        "frontend",
        "tests"
    ]
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
    print("✅ Project structure validated")
    
    # Check for main application files
    required_files = [
        "backend/core/web_scraper.py",
        "backend/core/scraper_integration.py",
        "backend/interfaces/scraper_web_interface.py",
        "frontend/index.html"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            return False
    print("✅ Core application files found")
    
    return True

def generate_test_summary():
    """Generate a test summary from results"""
    results_file = Path("tests/test_results.json")
    
    if not results_file.exists():
        print("⚠️  No test results found")
        return
        
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
            
        print("\n" + "="*60)
        print("📋 TEST SUMMARY")
        print("="*60)
        
        print(f"Timestamp: {results.get('timestamp', 'Unknown')}")
        print(f"Total Tests: {results.get('total_tests', 0)}")
        print(f"Passed: {results.get('passed', 0)} ✅")
        print(f"Failed: {results.get('failed', 0)} ❌")
        print(f"Errors: {results.get('errors', 0)} 💥")
        print(f"Skipped: {results.get('skipped', 0)} ⏭️")
        
        if results.get('total_tests', 0) > 0:
            success_rate = (results.get('passed', 0) / results.get('total_tests', 1)) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
        coverage = results.get('coverage', {})
        if 'total_coverage' in coverage:
            print(f"Code Coverage: {coverage['total_coverage']:.1f}%")
            
        # Show recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS ({len(recommendations)}):")
            for rec in recommendations[:5]:  # Show top 5
                print(f"   {rec['priority']} - {rec['category']}: {rec['issue']}")
                
        print("\n📄 Reports Generated:")
        if Path("tests/test_report.html").exists():
            print("   - HTML Report: tests/test_report.html")
        if Path("tests/coverage_html/index.html").exists():
            print("   - Coverage Report: tests/coverage_html/index.html")
            
    except Exception as e:
        print(f"❌ Error reading test results: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Live Graph System Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Modes:
  quick       - Run unit tests only (fastest)
  comprehensive - Run all tests except performance and e2e
  coverage    - Run coverage analysis only
  performance - Run performance tests
  e2e         - Run end-to-end tests
  all         - Run everything including performance and e2e
  pytest      - Use pytest directly with coverage
  
Examples:
  python run_tests.py quick
  python run_tests.py comprehensive
  python run_tests.py all
  python run_tests.py --install-deps comprehensive
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["quick", "comprehensive", "coverage", "performance", "e2e", "all", "pytest"],
        help="Test mode to run"
    )
    
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running tests"
    )
    
    parser.add_argument(
        "--validate-env",
        action="store_true",
        help="Validate test environment before running tests"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show test summary after completion"
    )
    
    args = parser.parse_args()
    
    print("🧪 Live Graph System Test Runner")
    print("="*50)
    
    # Validate environment if requested
    if args.validate_env:
        if not validate_test_environment():
            print("❌ Environment validation failed")
            sys.exit(1)
            
    # Install dependencies if requested
    if args.install_deps:
        if not install_test_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
            
    # Run tests based on mode
    start_time = time.time()
    
    test_functions = {
        "quick": run_quick_tests,
        "comprehensive": run_comprehensive_tests,
        "coverage": run_coverage_only,
        "performance": run_performance_tests,
        "e2e": run_e2e_tests,
        "all": run_all_tests,
        "pytest": run_pytest_mode
    }
    
    success = test_functions[args.mode]()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n⏱️  Total execution time: {duration:.2f} seconds")
    
    # Show summary if requested
    if args.summary:
        generate_test_summary()
        
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the reports for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
