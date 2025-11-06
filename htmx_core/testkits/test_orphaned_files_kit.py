"""
Orphaned Files Detection TestKit
==============================

Comprehensive orphaned files detection and analysis.
Based on the original detect_orphaned_files.py implementation.
"""

import os
import sys
import ast
import importlib
import inspect
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set, Tuple

# Handle imports for both direct execution and module import
try:
    from .test_base_testkit import BaseTestKit
except ImportError:
    # Direct execution - use absolute import
    from test_base_testkit import BaseTestKit

class OrphanedFilesDetectionKit(BaseTestKit):
    """TestKit for detecting orphaned files and analyzing usage patterns"""
    
    def setUp(self):
        super().setUp()
        self.all_python_files = []
        self.import_graph = defaultdict(set)
        self.usage_patterns = {}
        self.orphaned_files = []
        self.suspicious_files = []
        
    def test_project_file_discovery(self):
        """Discover all Python files in the project"""
        print("🔍 Discovering all Python files in project...")
        
        try:
            # Discover files across entire project
            for root, dirs, files in os.walk(self.project_root):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'staticfiles']]
                
                for file in files:
                    if file.endswith('.py') and not file.startswith('.'):
                        filepath = Path(root) / file
                        self.all_python_files.append(filepath)
            
            total_files = len(self.all_python_files)
            htmx_files = len([f for f in self.all_python_files if 'htmx_core' in str(f)])
            
            success = total_files > 0
            message = f"Discovered {total_files} Python files ({htmx_files} in htmx_core)"
            
            self.add_test_result("Project File Discovery", success, message, {
                'total_files': total_files,
                'htmx_core_files': htmx_files,
                'other_files': total_files - htmx_files
            })
            
            print(f"   📁 Total: {total_files} files ({htmx_files} in htmx_core)")
            
        except Exception as e:
            self.add_test_result("Project File Discovery", False, f"File discovery failed: {str(e)}")
    
    def test_import_graph_analysis(self):
        """Analyze import relationships across all files"""
        print("🕸️ Building import relationship graph...")
        
        processed_files = 0
        import_count = 0
        
        for filepath in self.all_python_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content, filename=str(filepath))
                file_imports = set()
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_imports.add(alias.name)
                            import_count += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            file_imports.add(node.module)
                            import_count += 1
                            # Also add full import paths
                            for alias in node.names:
                                full_import = f"{node.module}.{alias.name}"
                                file_imports.add(full_import)
                
                self.import_graph[str(filepath)] = file_imports
                processed_files += 1
                
            except Exception as e:
                # Skip files with parsing errors
                continue
        
        success = processed_files > 0
        message = f"Processed {processed_files} files, found {import_count} imports"
        
        self.add_test_result("Import Graph Analysis", success, message, {
            'processed_files': processed_files,
            'total_imports': import_count,
            'avg_imports_per_file': import_count / processed_files if processed_files > 0 else 0
        })
        
        print(f"   🕸️ Processed: {processed_files} files, {import_count} imports")
    
    def test_usage_pattern_detection(self):
        """Detect usage patterns for htmx_core files"""
        print("🔍 Detecting usage patterns...")
        
        htmx_files = [f for f in self.all_python_files if 'htmx_core' in str(f)]
        
        for filepath in htmx_files:
            rel_path = filepath.relative_to(self.project_root)
            module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
            
            usage_info = {
                'filepath': str(filepath),
                'module_path': module_path,
                'imported_by': [],
                'usage_type': 'unknown',
                'reasons': []
            }
            
            # Check if imported by other files
            for file_path, imports in self.import_graph.items():
                for import_name in imports:
                    if module_path in import_name or any(part in import_name for part in module_path.split('.')):
                        usage_info['imported_by'].append(file_path)
            
            # Determine usage type based on patterns
            filename = filepath.name
            file_content = ""
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except:
                pass
            
            # Check for auto-discovery patterns
            if any(pattern in filename for pattern in ['_tab_def.py', '_tabs.py', 'tab_config.py']):
                usage_info['usage_type'] = 'auto_discovered'
                usage_info['reasons'].append('Tab auto-discovery pattern')
            
            # Check for Django app patterns
            if filename in ['__init__.py', 'apps.py', 'admin.py', 'models.py', 'views.py', 'urls.py']:
                usage_info['usage_type'] = 'django_standard'
                usage_info['reasons'].append('Django standard file')
            
            # Check for middleware registration
            if 'middleware' in module_path.lower():
                usage_info['usage_type'] = 'django_middleware'
                usage_info['reasons'].append('Django middleware')
            
            # Check for template tags
            if 'templatetags' in module_path:
                usage_info['usage_type'] = 'django_templatetags'
                usage_info['reasons'].append('Django template tags')
            
            # Check for test files
            if 'test' in filename.lower() or 'example' in filename.lower():
                usage_info['usage_type'] = 'development'
                usage_info['reasons'].append('Development/test file')
            
            # Check if file has substantial content
            if len(file_content.strip()) < 50:
                usage_info['usage_type'] = 'empty_placeholder'
                usage_info['reasons'].append('Empty or minimal content')
            
            # Check if imported by other files
            if len(usage_info['imported_by']) > 0:
                if usage_info['usage_type'] == 'unknown':
                    usage_info['usage_type'] = 'explicitly_imported'
                usage_info['reasons'].append(f"Imported by {len(usage_info['imported_by'])} files")
            
            self.usage_patterns[str(filepath)] = usage_info
        
        total_analyzed = len(self.usage_patterns)
        
        message = f"Analyzed usage patterns for {total_analyzed} htmx_core files"
        
        self.add_test_result("Usage Pattern Detection", total_analyzed > 0, message, {
            'analyzed_files': total_analyzed,
            'usage_types': {
                usage_type: len([f for f in self.usage_patterns.values() if f['usage_type'] == usage_type])
                for usage_type in set(f['usage_type'] for f in self.usage_patterns.values())
            }
        })
        
        print(f"   🔍 Analyzed: {total_analyzed} htmx_core files")
    
    def test_orphaned_files_identification(self):
        """Identify truly orphaned files"""
        print("🗑️ Identifying orphaned files...")
        
        for filepath, usage_info in self.usage_patterns.items():
            if usage_info['usage_type'] == 'empty_placeholder':
                self.orphaned_files.append(usage_info)
            elif (usage_info['usage_type'] == 'unknown' and 
                  len(usage_info['imported_by']) == 0 and
                  len(usage_info['reasons']) == 0):
                self.orphaned_files.append(usage_info)
            elif (usage_info['usage_type'] in ['auto_discovered', 'django_middleware', 'development'] and
                  len(usage_info['imported_by']) == 0):
                self.suspicious_files.append(usage_info)
        
        total_htmx_files = len(self.usage_patterns)
        orphaned_count = len(self.orphaned_files)
        suspicious_count = len(self.suspicious_files)
        
        orphaned_percentage = (orphaned_count / total_htmx_files * 100) if total_htmx_files > 0 else 0
        
        success = orphaned_percentage < 10  # Less than 10% orphaned is good
        message = f"Found {orphaned_count} orphaned files ({orphaned_percentage:.1f}%), {suspicious_count} suspicious"
        
        self.add_test_result("Orphaned Files Identification", success, message, {
            'total_files': total_htmx_files,
            'orphaned_files': orphaned_count,
            'suspicious_files': suspicious_count,
            'orphaned_percentage': orphaned_percentage,
            'orphaned_list': [f['filepath'] for f in self.orphaned_files],
            'suspicious_list': [f['filepath'] for f in self.suspicious_files]
        })
        
        print(f"   🗑️ Orphaned: {orphaned_count}, Suspicious: {suspicious_count}")
    
    def test_file_usage_validation(self):
        """Validate file usage classifications"""
        print("✅ Validating file usage classifications...")
        
        classification_counts = defaultdict(int)
        validated_files = 0
        
        for usage_info in self.usage_patterns.values():
            classification_counts[usage_info['usage_type']] += 1
            
            # Validate classifications
            if usage_info['usage_type'] in ['auto_discovered', 'django_standard', 'django_middleware', 
                                          'django_templatetags', 'explicitly_imported']:
                validated_files += 1
        
        total_files = len(self.usage_patterns)
        validation_rate = (validated_files / total_files * 100) if total_files > 0 else 0
        
        success = validation_rate > 80  # 80% or more should have clear purpose
        message = f"Validation rate: {validation_rate:.1f}% ({validated_files}/{total_files})"
        
        self.add_test_result("File Usage Validation", success, message, {
            'validation_rate': validation_rate,
            'validated_files': validated_files,
            'total_files': total_files,
            'classifications': dict(classification_counts)
        })
        
        print(f"   ✅ Validation: {validation_rate:.1f}% ({validated_files}/{total_files})")
    
    def test_cleanup_recommendations(self):
        """Generate cleanup recommendations"""
        print("🧹 Generating cleanup recommendations...")
        
        recommendations = []
        
        # Recommend removing truly orphaned files
        for orphaned_file in self.orphaned_files:
            recommendations.append({
                'action': 'remove',
                'file': orphaned_file['filepath'],
                'reason': 'Empty placeholder or no usage detected',
                'confidence': 'high'
            })
        
        # Review suspicious files
        for suspicious_file in self.suspicious_files:
            recommendations.append({
                'action': 'review',
                'file': suspicious_file['filepath'],
                'reason': f"Type: {suspicious_file['usage_type']}, but not imported",
                'confidence': 'medium'
            })
        
        # Calculate cleanup potential
        total_files = len(self.usage_patterns)
        removable_files = len([r for r in recommendations if r['action'] == 'remove'])
        reviewable_files = len([r for r in recommendations if r['action'] == 'review'])
        
        cleanup_percentage = (removable_files / total_files * 100) if total_files > 0 else 0
        
        success = cleanup_percentage < 5  # Less than 5% removable files indicates good maintenance
        message = f"Cleanup potential: {cleanup_percentage:.1f}% ({removable_files} removable, {reviewable_files} reviewable)"
        
        self.add_test_result("Cleanup Recommendations", success, message, {
            'total_recommendations': len(recommendations),
            'removable_files': removable_files,
            'reviewable_files': reviewable_files,
            'cleanup_percentage': cleanup_percentage,
            'recommendations': recommendations[:10]  # First 10 recommendations
        })
        
        print(f"   🧹 Cleanup: {cleanup_percentage:.1f}% removable ({removable_files} files)")
    
    def tearDown(self):
        """Generate final orphaned files analysis summary"""
        total_files = len(self.usage_patterns)
        orphaned_count = len(self.orphaned_files)
        suspicious_count = len(self.suspicious_files)
        
        # Calculate architecture quality score
        if total_files > 0:
            orphaned_percentage = (orphaned_count / total_files) * 100
            architecture_score = 100 - orphaned_percentage
        else:
            architecture_score = 0
            orphaned_percentage = 0
        
        # Determine architecture quality
        if architecture_score >= 95:
            architecture_quality = "Excellent"
        elif architecture_score >= 90:
            architecture_quality = "Very Good"
        elif architecture_score >= 85:
            architecture_quality = "Good"
        else:
            architecture_quality = "Needs Improvement"
        
        self.test_results['summary'] = {
            'Total HTMX Files': total_files,
            'Orphaned Files': orphaned_count,
            'Suspicious Files': suspicious_count,
            'Orphaned Percentage': f"{orphaned_percentage:.1f}%",
            'Architecture Score': f"{architecture_score:.1f}%",
            'Architecture Quality': architecture_quality,
            'Cleanup Needed': orphaned_count > 0
        }
        
        print("\n" + "="*60)
        print("🗑️ ORPHANED FILES ANALYSIS SUMMARY")
        print("="*60)
        for key, value in self.test_results['summary'].items():
            print(f"{key}: {value}")
        
        if self.orphaned_files:
            print("\nOrphaned Files:")
            for orphaned in self.orphaned_files:
                print(f"  - {orphaned['filepath']}")
        
        if self.suspicious_files:
            print(f"\nSuspicious Files ({len(self.suspicious_files)}):")
            for suspicious in self.suspicious_files[:5]:  # Show first 5
                print(f"  - {suspicious['filepath']} ({suspicious['usage_type']})")
        
        print("="*60)
        
        super().tearDown()

if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)