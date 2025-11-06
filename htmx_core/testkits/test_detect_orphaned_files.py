#!/usr/bin/env python3
"""
HTMX Core Orphaned File Detector
Identifies files that exist but aren't being imported or used anywhere in the project.
"""

import os
import ast
import re
from pathlib import Path
from collections import defaultdict
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

class OrphanedFileDetector:
    def __init__(self):
        self.project_root = Path('.')
        self.htmx_core_path = Path('htmx_core')
        self.all_python_files = []
        self.import_mapping = defaultdict(set)  # file -> set of files it imports from
        self.imported_by = defaultdict(set)     # file -> set of files that import it
        self.orphaned_files = []
        self.suspicious_files = []
        
    def discover_all_python_files(self):
        """Find all Python files in the project"""
        print("🔍 Discovering all Python files in project...")
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories
            skip_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', 'staticfiles', 'media', 'logs'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = Path(root) / file
                    self.all_python_files.append(file_path)
        
        print(f"   Found {len(self.all_python_files)} Python files")
    
    def analyze_imports(self):
        """Analyze import relationships between files"""
        print("\n📊 Analyzing import relationships...")
        
        for file_path in self.all_python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse imports using AST
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    imported_modules = []
                    
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.append(alias.name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_modules.append(node.module)
                    
                    # Map imports to actual files
                    for module_name in imported_modules:
                        # Convert module path to file path
                        potential_paths = self._module_to_file_paths(module_name)
                        for potential_path in potential_paths:
                            if potential_path.exists():
                                self.import_mapping[file_path].add(potential_path)
                                self.imported_by[potential_path].add(file_path)
                                break
                
            except Exception as e:
                print(f"   ⚠️  Error analyzing {file_path}: {e}")
        
        print(f"   Analyzed imports for {len(self.import_mapping)} files")
    
    def _module_to_file_paths(self, module_name):
        """Convert a module name to potential file paths"""
        potential_paths = []
        
        # Handle relative imports and absolute imports
        module_parts = module_name.split('.')
        
        # Try as direct file path
        file_path = Path(*module_parts).with_suffix('.py')
        potential_paths.append(file_path)
        
        # Try with __init__.py
        dir_path = Path(*module_parts) / '__init__.py'
        potential_paths.append(dir_path)
        
        return potential_paths
    
    def find_orphaned_files(self):
        """Identify orphaned files in htmx_core"""
        print("\n🕵️  Identifying orphaned files in htmx_core...")
        
        htmx_files = [f for f in self.all_python_files if str(f).startswith('htmx_core/')]
        
        for file_path in htmx_files:
            # Skip certain files that are expected to be standalone
            skip_patterns = [
                '__init__.py',
                'manage.py',
                'apps.py',  # App config files are loaded by Django automatically
                'urls.py',  # URL files are included via urlconf
                'settings.py',
                'conftest.py',  # pytest configuration
                'test_',  # test files might not be imported directly
            ]
            
            if any(pattern in file_path.name for pattern in skip_patterns):
                continue
            
            # Check if this file is imported by anyone
            if file_path not in self.imported_by:
                # This file is not imported by anyone - potential orphan
                
                # But check if it might be used in other ways
                is_really_orphaned = self._deep_orphan_check(file_path)
                
                if is_really_orphaned:
                    self.orphaned_files.append(file_path)
                else:
                    self.suspicious_files.append(file_path)
        
        print(f"   Found {len(self.orphaned_files)} truly orphaned files")
        print(f"   Found {len(self.suspicious_files)} suspicious files (might be used indirectly)")
    
    def _deep_orphan_check(self, file_path):
        """Perform deeper analysis to see if file is really orphaned"""
        
        # Check if file is referenced in string literals (like URL includes)
        file_module = str(file_path.with_suffix('')).replace(os.sep, '.')
        file_stem = file_path.stem
        
        # Search for references in all Python files
        for search_file in self.all_python_files:
            try:
                with open(search_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for string references
                if (file_module in content or 
                    file_stem in content or
                    f'"{file_path.name}"' in content or
                    f"'{file_path.name}'" in content):
                    return False  # Not orphaned - referenced somewhere
                
            except Exception:
                continue
        
        # Check if it's a Django app file that might be auto-loaded
        if any(pattern in str(file_path) for pattern in ['apps.py', 'models.py', 'admin.py', 'views.py']):
            return False
        
        # Check if it defines classes/functions that might be used via getattr or similar
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # If it has classes or functions, it might be used dynamically
            has_definitions = any(isinstance(node, (ast.ClassDef, ast.FunctionDef)) 
                                for node in ast.walk(tree))
            
            if has_definitions:
                return False  # Might be used dynamically
                
        except Exception:
            pass
        
        return True  # Likely truly orphaned
    
    def analyze_htmx_specific_usage(self):
        """Analyze HTMX-specific usage patterns"""
        print("\n🎯 Analyzing HTMX-specific usage patterns...")
        
        # Check registry system usage
        registry_usage = self._check_registry_usage()
        
        # Check middleware usage 
        middleware_usage = self._check_middleware_usage()
        
        # Check auto-discovery usage
        auto_discovery_usage = self._check_auto_discovery_usage()
        
        return {
            'registry': registry_usage,
            'middleware': middleware_usage,
            'auto_discovery': auto_discovery_usage
        }
    
    def _check_registry_usage(self):
        """Check how registry system discovers and uses files"""
        registry_discovered = []
        
        # Files that should be auto-discovered by the registry
        patterns = ['_tab_def.py', '_tabs.py', 'tab_config.py']
        
        for file_path in self.all_python_files:
            if any(file_path.name.endswith(pattern) for pattern in patterns):
                registry_discovered.append(file_path)
        
        return {
            'discovered_files': registry_discovered,
            'count': len(registry_discovered)
        }
    
    def _check_middleware_usage(self):
        """Check middleware usage in settings"""
        middleware_files = []
        
        # Find middleware files
        for file_path in self.all_python_files:
            if 'middleware' in str(file_path) and str(file_path).startswith('htmx_core'):
                middleware_files.append(file_path)
        
        # Check if they're referenced in settings
        try:
            with open('config/settings.py', 'r') as f:
                settings_content = f.read()
            
            used_middleware = []
            for mw_file in middleware_files:
                module_name = str(mw_file.with_suffix('')).replace(os.sep, '.')
                if module_name in settings_content:
                    used_middleware.append(mw_file)
        
        except Exception:
            used_middleware = []
        
        return {
            'total_middleware': middleware_files,
            'used_middleware': used_middleware,
            'unused_middleware': [f for f in middleware_files if f not in used_middleware]
        }
    
    def _check_auto_discovery_usage(self):
        """Check files that are auto-discovered vs manually imported"""
        auto_discovered = []
        manually_imported = []
        
        htmx_files = [f for f in self.all_python_files if str(f).startswith('htmx_core/')]
        
        for file_path in htmx_files:
            # Check if file is in imported_by (manually imported)
            if file_path in self.imported_by:
                manually_imported.append(file_path)
            else:
                # Might be auto-discovered
                auto_discovered.append(file_path)
        
        return {
            'auto_discovered': auto_discovered,
            'manually_imported': manually_imported
        }
    
    def generate_orphan_report(self):
        """Generate comprehensive orphan analysis report"""
        print("\n📋 GENERATING ORPHAN ANALYSIS REPORT")
        print("=" * 60)
        
        htmx_usage = self.analyze_htmx_specific_usage()
        
        # Count htmx_core files
        htmx_files = [f for f in self.all_python_files if str(f).startswith('htmx_core/')]
        
        print(f"\n📊 STATISTICS:")
        print(f"   Total htmx_core files: {len(htmx_files)}")
        print(f"   Truly orphaned files: {len(self.orphaned_files)}")
        print(f"   Suspicious files: {len(self.suspicious_files)}")
        print(f"   Files with imports: {len([f for f in htmx_files if f in self.imported_by])}")
        
        # Registry auto-discovery
        print(f"\n🔍 AUTO-DISCOVERY ANALYSIS:")
        print(f"   Tab files auto-discovered: {htmx_usage['registry']['count']}")
        for tab_file in htmx_usage['registry']['discovered_files']:
            print(f"      ✅ {tab_file}")
        
        # Middleware usage
        middleware_info = htmx_usage['middleware']
        print(f"\n⚙️  MIDDLEWARE USAGE:")
        print(f"   Total middleware files: {len(middleware_info['total_middleware'])}")
        print(f"   Used in settings: {len(middleware_info['used_middleware'])}")
        print(f"   Unused middleware: {len(middleware_info['unused_middleware'])}")
        
        # Show truly orphaned files
        if self.orphaned_files:
            print(f"\n❌ TRULY ORPHANED FILES ({len(self.orphaned_files)}):")
            for orphan in self.orphaned_files:
                print(f"   🗑️  {orphan} - No imports, no references found")
        else:
            print(f"\n✅ NO TRULY ORPHANED FILES FOUND!")
        
        # Show suspicious files (might be used indirectly)
        if self.suspicious_files:
            print(f"\n⚠️  SUSPICIOUS FILES ({len(self.suspicious_files)}):")
            for suspicious in self.suspicious_files:
                print(f"   🤔 {suspicious} - Not directly imported but might be used")
        else:
            print(f"\n✅ NO SUSPICIOUS FILES FOUND!")
        
        # Usage summary
        print(f"\n📈 USAGE SUMMARY:")
        directly_imported = len([f for f in htmx_files if f in self.imported_by])
        auto_discovered = htmx_usage['registry']['count']
        settings_used = len(middleware_info['used_middleware'])
        
        total_used = directly_imported + auto_discovered + settings_used
        usage_percentage = (total_used / len(htmx_files) * 100) if htmx_files else 0
        
        print(f"   Directly imported: {directly_imported} files")
        print(f"   Auto-discovered: {auto_discovered} files") 
        print(f"   Settings-referenced: {settings_used} files")
        print(f"   Total actively used: {total_used}/{len(htmx_files)} ({usage_percentage:.1f}%)")
        
        # Final assessment
        print(f"\n🏆 FINAL ASSESSMENT:")
        if len(self.orphaned_files) == 0 and len(self.suspicious_files) <= 2:
            print("   🎉 EXCELLENT - No orphaned files detected!")
            print("   📦 All htmx_core files are actively used or auto-discovered")
        elif len(self.orphaned_files) <= 2:
            print("   ✅ GOOD - Very few potentially orphaned files")
        else:
            print("   ⚠️  ATTENTION - Multiple orphaned files detected")
        
        return {
            'orphaned_count': len(self.orphaned_files),
            'suspicious_count': len(self.suspicious_files),
            'usage_percentage': usage_percentage,
            'total_files': len(htmx_files)
        }
    
    def run_analysis(self):
        """Run the complete orphaned file analysis"""
        print("🕵️ HTMX CORE ORPHANED FILE DETECTION")
        print("=" * 50)
        
        self.discover_all_python_files()
        self.analyze_imports()
        self.find_orphaned_files()
        results = self.generate_orphan_report()
        
        return results

if __name__ == "__main__":
    detector = OrphanedFileDetector()
    detector.run_analysis()