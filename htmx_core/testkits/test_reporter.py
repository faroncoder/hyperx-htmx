"""
TestKit Reporter - Advanced reporting and visualization
====================================================

Provides comprehensive reporting capabilities for TestKit results.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Optional visualization imports
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

class TestKitReporter:
    """Advanced reporting for TestKit results"""
    
    def __init__(self, reports_path: Path = None):
        self.reports_path = reports_path or Path('testkits/reports')
        self.reports_path.mkdir(parents=True, exist_ok=True)
    
    def generate_summary_report(self, report_files: List[Path] = None) -> Dict:
        """Generate a summary report from multiple test runs"""
        if not report_files:
            report_files = list(self.reports_path.glob("*.json"))
        
        summary = {
            'total_kits': 0,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'success_rate': 0.0,
            'kit_results': [],
            'generated_at': datetime.now().isoformat()
        }
        
        for report_file in report_files:
            try:
                with open(report_file, 'r') as f:
                    data = json.load(f)
                
                kit_summary = self._analyze_kit_report(data)
                summary['kit_results'].append(kit_summary)
                summary['total_tests'] += kit_summary['total_tests']
                summary['passed_tests'] += kit_summary['passed_tests']
                summary['failed_tests'] += kit_summary['failed_tests']
                summary['total_kits'] += 1
                
            except Exception as e:
                print(f"Error processing {report_file}: {e}")
        
        if summary['total_tests'] > 0:
            summary['success_rate'] = (summary['passed_tests'] / summary['total_tests']) * 100
        
        # Save summary report
        summary_path = self.reports_path / f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate markdown summary
        self._generate_markdown_summary(summary, summary_path.with_suffix('.md'))
        
        return summary
    
    def _analyze_kit_report(self, data: Dict) -> Dict:
        """Analyze individual kit report"""
        tests = data.get('tests', [])
        passed = sum(1 for test in tests if test.get('success', False))
        failed = len(tests) - passed
        
        return {
            'kit_name': data.get('kit_name', 'Unknown'),
            'start_time': data.get('start_time'),
            'duration': data.get('duration'),
            'total_tests': len(tests),
            'passed_tests': passed,
            'failed_tests': failed,
            'success_rate': (passed / len(tests) * 100) if tests else 0,
            'summary': data.get('summary', {})
        }
    
    def _generate_markdown_summary(self, summary: Dict, filepath: Path):
        """Generate markdown summary report"""
        with open(filepath, 'w') as f:
            f.write("# TestKit Summary Report\n\n")
            f.write(f"**Generated:** {summary['generated_at']}\n")
            f.write(f"**Total TestKits:** {summary['total_kits']}\n")
            f.write(f"**Total Tests:** {summary['total_tests']}\n")
            f.write(f"**Success Rate:** {summary['success_rate']:.1f}%\n\n")
            
            f.write("## TestKit Results\n\n")
            for kit in summary['kit_results']:
                status = "✅" if kit['success_rate'] > 80 else "⚠️" if kit['success_rate'] > 60 else "❌"
                f.write(f"{status} **{kit['kit_name']}**\n")
                f.write(f"   - Tests: {kit['passed_tests']}/{kit['total_tests']}\n")
                f.write(f"   - Success Rate: {kit['success_rate']:.1f}%\n")
                f.write(f"   - Duration: {kit['duration']}\n\n")
    
    def generate_charts(self, summary: Dict):
        """Generate visualization charts"""
        if not CHARTS_AVAILABLE:
            print("Charts not available - install matplotlib and seaborn for visualization")
            return None
            
        try:
            # Set up the plotting style
            plt.style.use('default')
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('TestKit Analysis Dashboard', fontsize=16)
            
            # Chart 1: Overall Success Rate
            axes[0, 0].pie([summary['passed_tests'], summary['failed_tests']], 
                          labels=['Passed', 'Failed'], 
                          autopct='%1.1f%%',
                          colors=['#4CAF50', '#F44336'])
            axes[0, 0].set_title('Overall Test Results')
            
            # Chart 2: Success Rate by Kit
            kit_names = [kit['kit_name'] for kit in summary['kit_results']]
            success_rates = [kit['success_rate'] for kit in summary['kit_results']]
            
            bars = axes[0, 1].bar(kit_names, success_rates)
            axes[0, 1].set_title('Success Rate by TestKit')
            axes[0, 1].set_ylabel('Success Rate (%)')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Color bars based on success rate
            for bar, rate in zip(bars, success_rates):
                if rate > 80:
                    bar.set_color('#4CAF50')
                elif rate > 60:
                    bar.set_color('#FF9800')
                else:
                    bar.set_color('#F44336')
            
            # Chart 3: Test Count Distribution
            test_counts = [kit['total_tests'] for kit in summary['kit_results']]
            axes[1, 0].bar(kit_names, test_counts, color='#2196F3')
            axes[1, 0].set_title('Test Count by Kit')
            axes[1, 0].set_ylabel('Number of Tests')
            axes[1, 0].tick_params(axis='x', rotation=45)
            
            # Chart 4: Timeline (if we have duration data)
            durations = []
            for kit in summary['kit_results']:
                duration_str = kit.get('duration', '0:00:00')
                # Simple duration parsing for visualization
                try:
                    if ':' in duration_str:
                        parts = duration_str.split(':')
                        seconds = float(parts[-1])
                        if len(parts) > 1:
                            seconds += int(parts[-2]) * 60
                        if len(parts) > 2:
                            seconds += int(parts[-3]) * 3600
                        durations.append(seconds)
                    else:
                        durations.append(0)
                except:
                    durations.append(0)
            
            axes[1, 1].bar(kit_names, durations, color='#9C27B0')
            axes[1, 1].set_title('Execution Time by Kit')
            axes[1, 1].set_ylabel('Duration (seconds)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save chart
            chart_path = self.reports_path / f"testkit_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"Error generating charts: {e}")
            return None