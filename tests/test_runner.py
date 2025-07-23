#!/usr/bin/env python3
"""
Comprehensive test runner for the live graph system
Executes all tests and generates coverage reports
"""

import unittest
import sys
import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "backend" / "core"))
sys.path.append(str(project_root / "backend" / "interfaces"))
sys.path.append(str(project_root / "backend" / "config"))


class TestRunner:
    """Comprehensive test runner with coverage reporting"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "test_suites": {},
            "coverage": {},
            "recommendations": []
        }
        
    def discover_tests(self):
        """Discover all test files in the test directory"""
        test_files = []
        
        # Find all test files
        for test_file in self.test_dir.rglob("test_*.py"):
            if test_file.name != "test_runner.py":
                test_files.append(test_file)
                
        return test_files
        
    def run_test_suite(self, test_file, suite_name):
        """Run a specific test suite and collect results"""
        print(f"\n{'='*60}")
        print(f"Running {suite_name}: {test_file.name}")
        print(f"{'='*60}")
        
        # Load the test module
        spec = unittest.util.spec_from_file_location(test_file.stem, test_file)
        module = unittest.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"❌ Failed to load test module {test_file.name}: {e}")
            self.results["test_suites"][suite_name] = {
                "status": "LOAD_ERROR",
                "error": str(e),
                "tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 1
            }
            return
            
        # Create test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run tests with custom result collector
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # Collect results
        suite_results = {
            "status": "COMPLETED",
            "duration": end_time - start_time,
            "tests": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors),
            "skipped": len(getattr(result, 'skipped', [])),
            "failures": [{"test": str(test), "error": error} for test, error in result.failures],
            "errors": [{"test": str(test), "error": error} for test, error in result.errors]
        }
        
        self.results["test_suites"][suite_name] = suite_results
        
        # Update totals
        self.results["total_tests"] += suite_results["tests"]
        self.results["passed"] += suite_results["passed"]
        self.results["failed"] += suite_results["failed"]
        self.results["errors"] += suite_results["errors"]
        self.results["skipped"] += suite_results["skipped"]
        
        # Print summary
        print(f"\n📊 {suite_name} Results:")
        print(f"   Tests: {suite_results['tests']}")
        print(f"   Passed: {suite_results['passed']} ✅")
        print(f"   Failed: {suite_results['failed']} ❌")
        print(f"   Errors: {suite_results['errors']} 💥")
        print(f"   Duration: {suite_results['duration']:.2f}s")
        
    def run_coverage_analysis(self):
        """Run coverage analysis on the codebase"""
        print(f"\n{'='*60}")
        print("Running Coverage Analysis")
        print(f"{'='*60}")
        
        try:
            # Install coverage if not available
            subprocess.run([sys.executable, "-m", "pip", "install", "coverage"], 
                         capture_output=True, check=False)
            
            # Run coverage on backend code
            backend_dir = self.project_root / "backend"
            
            # Run tests with coverage
            coverage_cmd = [
                sys.executable, "-m", "coverage", "run",
                "--source", str(backend_dir),
                "--omit", "*/tests/*,*/test_*",
                "-m", "unittest", "discover",
                "-s", str(self.test_dir),
                "-p", "test_*.py"
            ]
            
            result = subprocess.run(coverage_cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                # Generate coverage report
                report_cmd = [sys.executable, "-m", "coverage", "report", "--format=json"]
                report_result = subprocess.run(report_cmd, capture_output=True, text=True, cwd=self.project_root)
                
                if report_result.returncode == 0:
                    try:
                        coverage_data = json.loads(report_result.stdout)
                        self.results["coverage"] = {
                            "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
                            "files": coverage_data.get("files", {}),
                            "summary": coverage_data.get("totals", {})
                        }
                        print(f"✅ Coverage analysis completed: {self.results['coverage']['total_coverage']:.1f}%")
                    except json.JSONDecodeError:
                        print("❌ Failed to parse coverage JSON")
                        self.results["coverage"] = {"error": "Failed to parse coverage data"}
                else:
                    print(f"❌ Coverage report failed: {report_result.stderr}")
                    self.results["coverage"] = {"error": report_result.stderr}
            else:
                print(f"❌ Coverage run failed: {result.stderr}")
                self.results["coverage"] = {"error": result.stderr}
                
        except Exception as e:
            print(f"❌ Coverage analysis error: {e}")
            self.results["coverage"] = {"error": str(e)}
            
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check overall test success rate
        if self.results["total_tests"] > 0:
            success_rate = (self.results["passed"] / self.results["total_tests"]) * 100
            
            if success_rate < 80:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Test Quality",
                    "issue": f"Low test success rate: {success_rate:.1f}%",
                    "recommendation": "Focus on fixing failing tests before adding new features"
                })
            elif success_rate < 95:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Test Quality",
                    "issue": f"Moderate test success rate: {success_rate:.1f}%",
                    "recommendation": "Investigate and fix failing tests to improve reliability"
                })
                
        # Check coverage
        if "total_coverage" in self.results["coverage"]:
            coverage = self.results["coverage"]["total_coverage"]
            
            if coverage < 60:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Test Coverage",
                    "issue": f"Low test coverage: {coverage:.1f}%",
                    "recommendation": "Add unit tests for uncovered code, especially core functionality"
                })
            elif coverage < 80:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Test Coverage",
                    "issue": f"Moderate test coverage: {coverage:.1f}%",
                    "recommendation": "Increase test coverage by adding tests for edge cases and error handling"
                })
                
        # Check for test suite issues
        for suite_name, suite_results in self.results["test_suites"].items():
            if suite_results["status"] == "LOAD_ERROR":
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Test Infrastructure",
                    "issue": f"Test suite {suite_name} failed to load",
                    "recommendation": "Fix import errors and dependencies in test suite"
                })
                
            if suite_results.get("errors", 0) > 0:
                recommendations.append({
                    "priority": "MEDIUM",
                    "category": "Test Quality",
                    "issue": f"Test suite {suite_name} has {suite_results['errors']} errors",
                    "recommendation": "Fix test errors to ensure reliable test execution"
                })
                
        # Check for missing test categories
        suite_names = set(self.results["test_suites"].keys())
        expected_categories = {
            "unit", "integration", "e2e", "web_interface", 
            "error_handling", "performance"
        }
        
        missing_categories = expected_categories - {
            category for category in expected_categories 
            if any(category in name.lower() for name in suite_names)
        }
        
        if missing_categories:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Test Completeness",
                "issue": f"Missing test categories: {', '.join(missing_categories)}",
                "recommendation": "Add comprehensive tests for all system components"
            })
            
        self.results["recommendations"] = recommendations
        
    def generate_html_report(self):
        """Generate an HTML test report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Live Graph System - Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: white; color: black; }}
                .header {{ background: black; color: white; padding: 20px; margin: -20px -20px 20px -20px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: #f5f5f5; padding: 15px; border: 1px solid black; flex: 1; text-align: center; }}
                .metric h3 {{ margin: 0 0 10px 0; }}
                .metric .value {{ font-size: 24px; font-weight: bold; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                .error {{ color: orange; }}
                .suite {{ margin: 20px 0; border: 1px solid black; }}
                .suite-header {{ background: #f0f0f0; padding: 10px; font-weight: bold; }}
                .suite-content {{ padding: 15px; }}
                .recommendation {{ margin: 10px 0; padding: 10px; border-left: 4px solid; }}
                .high {{ border-color: red; background: #ffe6e6; }}
                .medium {{ border-color: orange; background: #fff3e6; }}
                .low {{ border-color: green; background: #e6ffe6; }}
                .coverage-bar {{ background: #ddd; height: 20px; border: 1px solid black; }}
                .coverage-fill {{ background: green; height: 100%; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Live Graph System - Test Report</h1>
                <p>Generated: {self.results['timestamp']}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <div class="value">{self.results['total_tests']}</div>
                </div>
                <div class="metric">
                    <h3>Passed</h3>
                    <div class="value passed">{self.results['passed']}</div>
                </div>
                <div class="metric">
                    <h3>Failed</h3>
                    <div class="value failed">{self.results['failed']}</div>
                </div>
                <div class="metric">
                    <h3>Errors</h3>
                    <div class="value error">{self.results['errors']}</div>
                </div>
            </div>
        """
        
        # Add coverage section
        if "total_coverage" in self.results["coverage"]:
            coverage = self.results["coverage"]["total_coverage"]
            html_content += f"""
            <div class="suite">
                <div class="suite-header">Code Coverage</div>
                <div class="suite-content">
                    <p>Overall Coverage: {coverage:.1f}%</p>
                    <div class="coverage-bar">
                        <div class="coverage-fill" style="width: {coverage}%"></div>
                    </div>
                </div>
            </div>
            """
            
        # Add test suites
        for suite_name, suite_data in self.results["test_suites"].items():
            status_class = "passed" if suite_data.get("failed", 0) == 0 and suite_data.get("errors", 0) == 0 else "failed"
            
            html_content += f"""
            <div class="suite">
                <div class="suite-header">{suite_name}</div>
                <div class="suite-content">
                    <p>Status: <span class="{status_class}">{suite_data['status']}</span></p>
                    <p>Tests: {suite_data.get('tests', 0)} | 
                       Passed: {suite_data.get('passed', 0)} | 
                       Failed: {suite_data.get('failed', 0)} | 
                       Errors: {suite_data.get('errors', 0)}</p>
                    <p>Duration: {suite_data.get('duration', 0):.2f}s</p>
            """
            
            # Add failures and errors
            if suite_data.get('failures'):
                html_content += "<h4>Failures:</h4><ul>"
                for failure in suite_data['failures']:
                    html_content += f"<li><strong>{failure['test']}</strong><br><pre>{failure['error']}</pre></li>"
                html_content += "</ul>"
                
            if suite_data.get('errors'):
                html_content += "<h4>Errors:</h4><ul>"
                for error in suite_data['errors']:
                    html_content += f"<li><strong>{error['test']}</strong><br><pre>{error['error']}</pre></li>"
                html_content += "</ul>"
                
            html_content += "</div></div>"
            
        # Add recommendations
        if self.results["recommendations"]:
            html_content += """
            <div class="suite">
                <div class="suite-header">Recommendations</div>
                <div class="suite-content">
            """
            
            for rec in self.results["recommendations"]:
                priority_class = rec["priority"].lower()
                html_content += f"""
                <div class="recommendation {priority_class}">
                    <strong>{rec['priority']} - {rec['category']}</strong><br>
                    Issue: {rec['issue']}<br>
                    Recommendation: {rec['recommendation']}
                </div>
                """
                
            html_content += "</div></div>"
            
        html_content += """
        </body>
        </html>
        """
        
        # Save HTML report
        report_file = self.test_dir / "test_report.html"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"📄 HTML report saved to: {report_file}")
        
    def run_all_tests(self, include_performance=False, include_e2e=False):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Test Suite")
        print(f"Project Root: {self.project_root}")
        print(f"Test Directory: {self.test_dir}")
        
        start_time = time.time()
        
        # Discover test files
        test_files = self.discover_tests()
        print(f"\n📋 Discovered {len(test_files)} test files")
        
        # Categorize and run tests
        test_categories = {
            "Unit Tests": [],
            "Integration Tests": [],
            "Web Interface Tests": [],
            "End-to-End Tests": [],
            "Error Handling Tests": [],
            "Performance Tests": []
        }
        
        for test_file in test_files:
            file_path = str(test_file)
            
            if "unit" in file_path:
                test_categories["Unit Tests"].append(test_file)
            elif "integration" in file_path:
                test_categories["Integration Tests"].append(test_file)
            elif "web_interface" in file_path:
                test_categories["Web Interface Tests"].append(test_file)
            elif "e2e" in file_path:
                test_categories["End-to-End Tests"].append(test_file)
            elif "error_handling" in file_path:
                test_categories["Error Handling Tests"].append(test_file)
            elif "performance" in file_path:
                test_categories["Performance Tests"].append(test_file)
            else:
                test_categories["Unit Tests"].append(test_file)  # Default category
                
        # Run test categories
        for category, files in test_categories.items():
            if not files:
                continue
                
            # Skip performance and e2e tests unless explicitly requested
            if category == "Performance Tests" and not include_performance:
                print(f"\n⏭️  Skipping {category} (use --performance to include)")
                continue
                
            if category == "End-to-End Tests" and not include_e2e:
                print(f"\n⏭️  Skipping {category} (use --e2e to include)")
                continue
                
            for test_file in files:
                suite_name = f"{category} - {test_file.stem}"
                self.run_test_suite(test_file, suite_name)
                
        # Run coverage analysis
        self.run_coverage_analysis()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Print final summary
        print(f"\n{'='*60}")
        print("🎯 FINAL TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"Passed: {self.results['passed']} ✅")
        print(f"Failed: {self.results['failed']} ❌")
        print(f"Errors: {self.results['errors']} 💥")
        print(f"Skipped: {self.results['skipped']} ⏭️")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests']) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
        if "total_coverage" in self.results["coverage"]:
            print(f"Code Coverage: {self.results['coverage']['total_coverage']:.1f}%")
            
        print(f"Total Time: {total_time:.2f}s")
        
        # Save JSON report
        json_report_file = self.test_dir / "test_results.json"
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 JSON report saved to: {json_report_file}")
        
        # Generate HTML report
        self.generate_html_report()
        
        # Print recommendations
        if self.results["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"   {rec['priority']} - {rec['category']}: {rec['issue']}")
                print(f"      → {rec['recommendation']}")
                
        return self.results['failed'] == 0 and self.results['errors'] == 0


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run comprehensive test suite for Live Graph System")
    parser.add_argument("--performance", action="store_true", help="Include performance tests")
    parser.add_argument("--e2e", action="store_true", help="Include end-to-end tests")
    parser.add_argument("--coverage-only", action="store_true", help="Run only coverage analysis")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.coverage_only:
        runner.run_coverage_analysis()
        return
        
    success = runner.run_all_tests(
        include_performance=args.performance,
        include_e2e=args.e2e
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
