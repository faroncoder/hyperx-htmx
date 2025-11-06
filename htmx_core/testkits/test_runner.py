"""
TestKit Runner - Main entry point for running all TestKits
========================================================

Orchestrates execution of multiple TestKits and generates comprehensive reports.
"""

import unittest
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Handle imports for both direct execution and module import
try:
    from .test_discovery_kit import HTMXCoreDiscoveryKit
    from .test_analysis_kit import HTMXCoreAnalysisKit
    from .test_orphaned_files_kit import OrphanedFilesDetectionKit
    from .test_system_health_kit import SystemHealthKit
    from .test_reporter import TestKitReporter
except ImportError:
    # Direct execution - use absolute imports
    from test_discovery_kit import HTMXCoreDiscoveryKit
    from test_analysis_kit import HTMXCoreAnalysisKit
    from test_orphaned_files_kit import OrphanedFilesDetectionKit
    from test_system_health_kit import SystemHealthKit
    from test_reporter import TestKitReporter

class TestKitRunner:
    """Main runner for all TestKits"""
    
    def __init__(self, reports_path: Path = None):
        self.reports_path = reports_path or PROJECT_ROOT / 'testkits' / 'reports'
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.reporter = TestKitReporter(self.reports_path)
        
        # Available TestKits
        self.available_kits = {
            'health': SystemHealthKit,
            'discovery': HTMXCoreDiscoveryKit,
            'analysis': HTMXCoreAnalysisKit,
            'orphaned': OrphanedFilesDetectionKit
        }
        
        self.results = {}
    
    def run_kit(self, kit_name: str, verbosity: int = 2) -> Dict:
        """Run a specific TestKit"""
        if kit_name not in self.available_kits:
            raise ValueError(f"Unknown TestKit: {kit_name}. Available: {list(self.available_kits.keys())}")
        
        print(f"\n{'='*60}")
        print(f"🚀 RUNNING TESTKIT: {kit_name.upper()}")
        print(f"{'='*60}")
        
        # Create test suite
        kit_class = self.available_kits[kit_name]
        suite = unittest.TestLoader().loadTestsFromTestCase(kit_class)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
        result = runner.run(suite)
        
        # Store results
        self.results[kit_name] = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success': result.wasSuccessful(),
            'timestamp': datetime.now().isoformat()
        }
        
        return self.results[kit_name]
    
    def run_all(self, verbosity: int = 2) -> Dict:
        """Run all available TestKits"""
        print(f"\n{'='*70}")
        print("🧪 S5PORTAL TESTKITS - COMPREHENSIVE TESTING SUITE")
        print(f"{'='*70}")
        print(f"Starting full TestKit execution at {datetime.now()}")
        print(f"Available TestKits: {', '.join(self.available_kits.keys())}")
        
        start_time = datetime.now()
        
        # Run each TestKit
        for kit_name in self.available_kits.keys():
            try:
                self.run_kit(kit_name, verbosity)
            except Exception as e:
                print(f"❌ Failed to run {kit_name}: {e}")
                self.results[kit_name] = {
                    'tests_run': 0,
                    'failures': 0,
                    'errors': 1,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Generate summary
        self._generate_execution_summary(duration)
        
        # Generate comprehensive report
        try:
            summary_report = self.reporter.generate_summary_report()
            print(f"\n📊 Comprehensive report generated: {summary_report.get('generated_at', 'unknown')}")
        except Exception as e:
            print(f"⚠️ Report generation failed: {e}")
        
        return self.results
    
    def run_specific(self, kit_names: List[str], verbosity: int = 2) -> Dict:
        """Run specific TestKits"""
        print(f"\n{'='*70}")
        print(f"🧪 RUNNING SPECIFIC TESTKITS: {', '.join(kit_names)}")
        print(f"{'='*70}")
        
        start_time = datetime.now()
        
        for kit_name in kit_names:
            if kit_name in self.available_kits:
                try:
                    self.run_kit(kit_name, verbosity)
                except Exception as e:
                    print(f"❌ Failed to run {kit_name}: {e}")
            else:
                print(f"⚠️ Unknown TestKit: {kit_name}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        self._generate_execution_summary(duration)
        
        return self.results
    
    def _generate_execution_summary(self, duration):
        """Generate execution summary"""
        print(f"\n{'='*70}")
        print("📋 TESTKIT EXECUTION SUMMARY")
        print(f"{'='*70}")
        
        total_tests = sum(result.get('tests_run', 0) for result in self.results.values())
        total_failures = sum(result.get('failures', 0) for result in self.results.values())
        total_errors = sum(result.get('errors', 0) for result in self.results.values())
        successful_kits = sum(1 for result in self.results.values() if result.get('success', False))
        
        print(f"Duration: {duration}")
        print(f"TestKits Run: {len(self.results)}")
        print(f"Successful TestKits: {successful_kits}/{len(self.results)}")
        print(f"Total Tests: {total_tests}")
        print(f"Failures: {total_failures}")
        print(f"Errors: {total_errors}")
        
        if total_tests > 0:
            success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100
            print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print("\nIndividual TestKit Results:")
        for kit_name, result in self.results.items():
            status = "✅" if result.get('success', False) else "❌"
            tests = result.get('tests_run', 0)
            failures = result.get('failures', 0)
            errors = result.get('errors', 0)
            
            print(f"  {status} {kit_name}: {tests} tests, {failures} failures, {errors} errors")
        
        print(f"{'='*70}")
    
    def list_available_kits(self):
        """List all available TestKits"""
        print("\n🧪 Available TestKits:")
        print("="*40)
        
        kit_descriptions = {
            'health': 'System Health - Overall system and framework validation',
            'discovery': 'HTMX Core Discovery - Component discovery and functionality testing',
            'analysis': 'HTMX Core Analysis - Key component integration testing', 
            'orphaned': 'Orphaned Files Detection - File usage analysis and cleanup detection'
        }
        
        for kit_name, kit_class in self.available_kits.items():
            description = kit_descriptions.get(kit_name, 'No description available')
            print(f"  📦 {kit_name}: {description}")
        
        print("="*40)
    
    def get_recent_reports(self, limit: int = 5) -> List[Path]:
        """Get list of recent report files"""
        report_files = []
        
        for ext in ['.json', '.md']:
            report_files.extend(self.reports_path.glob(f"*{ext}"))
        
        # Sort by modification time, newest first
        report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return report_files[:limit]


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='S5Portal TestKit Runner')
    parser.add_argument('--kits', nargs='*', help='Specific TestKits to run')
    parser.add_argument('--list', action='store_true', help='List available TestKits')
    parser.add_argument('--verbosity', '-v', type=int, default=2, help='Test verbosity level (0-2)')
    parser.add_argument('--reports', help='Custom reports directory')
    
    args = parser.parse_args()
    
    # Set up runner
    reports_path = Path(args.reports) if args.reports else None
    runner = TestKitRunner(reports_path)
    
    # Handle commands
    if args.list:
        runner.list_available_kits()
        return
    
    if args.kits:
        runner.run_specific(args.kits, args.verbosity)
    else:
        runner.run_all(args.verbosity)
    
    # Show recent reports
    print("\n📄 Recent Reports:")
    for report in runner.get_recent_reports():
        print(f"  - {report.name}")


if __name__ == '__main__':
    main()