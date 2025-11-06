"""
X-Tab Registry System
====================

Central registry for managing tabbed interfaces across the application.
Imports core functionality from htmx_core and extends it for X-Tab specific needs.
"""

import os
import importlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

# Import HTMX core utilities
try:
    from htmx_core.utils.htmx_helpers import get_dynamic_context, _get_htmx_render_mode
    from htmx_core.mixins.htmx_mixin import HTMXLoginRequiredMixin
    from htmx_core.utils.htmx_defaults import get_htmx_template_context
except ImportError as e:
    print(f"[X-TABS] Warning: HTMX Core import failed: {e}")
    # Provide fallbacks
    def get_dynamic_context(*args, **kwargs):
        return {}
    def _get_htmx_render_mode(*args, **kwargs):
        return 'full'
    class HTMXLoginRequiredMixin:
        pass
    def get_htmx_template_context(*args, **kwargs):
        return {}


@dataclass
class XTabDefinition:
    """Standard structure for X-Tab definitions"""
    tab_id: str
    name: str
    template: str
    context_method: str
    permission_level: int = 0
    icon: str = 'fas fa-tab'
    order: int = 50
    requires_superuser: bool = False
    dynamic_reload: bool = False
    refresh_interval: int = 0
    extra_attrs: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for template rendering"""
        return {
            'tab_id': self.tab_id,
            'name': self.name,
            'template': self.template,
            'context_method': self.context_method,
            'permission_level': self.permission_level,
            'icon': self.icon,
            'order': self.order,
            'requires_superuser': self.requires_superuser,
            'dynamic_reload': self.dynamic_reload,
            'refresh_interval': self.refresh_interval,
            **self.extra_attrs
        }


class TabRegistry:
    """
    Global registry for X-Tab definitions.
    
    Discovers and manages tab definitions across the entire Django project.
    Uses os.walk() to find tab definition files and registers them automatically.
    """
    
    _instance = None
    _tabs: Dict[str, List[XTabDefinition]] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls):
        """Initialize the tab registry by discovering all tab definitions"""
        if cls._initialized:
            return
            
        registry = cls()
        registry._discover_tabs()
        cls._initialized = True
        
    def _discover_tabs(self):
        """
        Use os.walk() to discover tab definition files across the project.
        
        Looks for files matching these patterns:
        - *_tab_def.py
        - *_tabs.py  
        - tab_config.py
        """
        from django.conf import settings
        
        project_root = Path(settings.BASE_DIR)
        tab_files = []
        
        # Discover tab definition files
        for root, dirs, files in os.walk(project_root):
            # Skip certain directories
            skip_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', 'staticfiles', 'media'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if self._is_tab_definition_file(file):
                    file_path = Path(root) / file
                    tab_files.append(file_path)
        
        print(f"[X-TABS] Discovered {len(tab_files)} tab definition files")
        
        # Load tab definitions from discovered files
        for tab_file in tab_files:
            self._load_tab_definitions(tab_file)
    
    def _is_tab_definition_file(self, filename: str) -> bool:
        """Check if a file contains tab definitions"""
        patterns = [
            '_tab_def.py',
            '_tabs.py', 
            'tab_config.py'
        ]
        return any(filename.endswith(pattern) for pattern in patterns)
    
    def _load_tab_definitions(self, tab_file: Path):
        """Load tab definitions from a Python file"""
        try:
            # Convert file path to module path
            relative_path = tab_file.relative_to(Path.cwd())
            module_path = str(relative_path.with_suffix('')).replace(os.sep, '.')
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Look for tab definitions
            tabs = []
            
            # Check for standard patterns
            if hasattr(module, 'TAB_DEFINITIONS'):
                tabs.extend(self._convert_to_tab_definitions(module.TAB_DEFINITIONS))
            
            if hasattr(module, 'ADMIN_TAB_DEFINITIONS'):
                tabs.extend(self._convert_to_tab_definitions(module.ADMIN_TAB_DEFINITIONS))
                
            if hasattr(module, 'register_tabs'):
                tabs.extend(self._convert_to_tab_definitions(module.register_tabs()))
                
            if hasattr(module, 'get_all_tabs'):
                tabs.extend(self._convert_to_tab_definitions(module.get_all_tabs()))
            
            # Register discovered tabs
            if tabs:
                app_name = self._get_app_name_from_path(tab_file)
                self._tabs[app_name] = self._tabs.get(app_name, []) + tabs
                print(f"[X-TABS] Loaded {len(tabs)} tabs from {tab_file}")
                
        except Exception as e:
            print(f"[X-TABS] Error loading {tab_file}: {e}")
    
    def _convert_to_tab_definitions(self, tab_data: List[dict]) -> List[XTabDefinition]:
        """Convert dictionary tab data to XTabDefinition objects"""
        tabs = []
        for tab_dict in tab_data:
            try:
                tabs.append(XTabDefinition(**tab_dict))
            except Exception as e:
                print(f"[X-TABS] Error creating tab definition: {e}")
        return tabs
    
    def _get_app_name_from_path(self, file_path: Path) -> str:
        """Extract Django app name from file path"""
        parts = file_path.parts
        
        # Look for common Django app indicators
        for i, part in enumerate(parts):
            if i < len(parts) - 1:  # Not the last part (filename)
                # Check if this looks like a Django app
                app_path = Path(*parts[:i+1])
                if (app_path / 'apps.py').exists() or (app_path / 'models.py').exists():
                    return part
        
        # Fallback - use parent directory name
        return file_path.parent.name
    
    @classmethod
    def get_tabs_for_app(cls, app_name: str) -> List[XTabDefinition]:
        """Get all tabs registered for a specific app"""
        if not cls._initialized:
            cls.initialize()
        return cls._tabs.get(app_name, [])
    
    @classmethod
    def get_all_tabs(cls) -> Dict[str, List[XTabDefinition]]:
        """Get all registered tabs grouped by app"""
        if not cls._initialized:
            cls.initialize()
        return cls._tabs.copy()
    
    @classmethod
    def filter_tabs_for_user(cls, tabs: List[XTabDefinition], user) -> List[XTabDefinition]:
        """Filter tabs based on user permissions"""
        filtered_tabs = []
        
        for tab in tabs:
            # Check superuser requirement
            if tab.requires_superuser and not user.is_superuser:
                continue
                
            # Check permission level
            user_level = getattr(user, 'permission_level', 0)
            if user_level < tab.permission_level:
                continue
                
            filtered_tabs.append(tab)
        
        # Sort by order
        return sorted(filtered_tabs, key=lambda x: x.order)
    
    @classmethod
    def register_tab(cls, app_name: str, tab_definition: XTabDefinition):
        """Manually register a single tab definition"""
        if not cls._initialized:
            cls.initialize()
        
        if app_name not in cls._tabs:
            cls._tabs[app_name] = []
        
        cls._tabs[app_name].append(tab_definition)
        print(f"[X-TABS] Manually registered tab '{tab_definition.tab_id}' for app '{app_name}'")
    
    @classmethod
    def generate_tab_manifest(cls, output_path: Optional[str] = None) -> dict:
        """
        Generate JSON manifest of all tabs for frontend consumption.
        Extracted and enhanced from htmx_tabber() functionality.
        
        Args:
            output_path: Optional path to write manifest file
            
        Returns:
            dict: Tab manifest data
        """
        from django.conf import settings
        from django.utils.text import slugify
        from pathlib import Path
        import json
        import os
        
        if not cls._initialized:
            cls.initialize()
        
        # Build comprehensive tab listing
        manifest_data = {
            'generated_at': str(Path(__file__).stat().st_mtime),
            'total_apps': len(cls._tabs),
            'total_tabs': sum(len(tabs) for tabs in cls._tabs.values()),
            'apps': {}
        }
        
        # Process each app's tabs
        for app_name, tabs in cls._tabs.items():
            app_tabs = []
            for tab in tabs:
                tab_data = {
                    'tab_id': tab.tab_id,
                    'name': tab.name,
                    'tab_slug': slugify(tab.name),
                    'template': tab.template,
                    'context_method': tab.context_method,
                    'permission_level': tab.permission_level,
                    'icon': tab.icon,
                    'order': tab.order,
                    'requires_superuser': tab.requires_superuser,
                    'dynamic_reload': tab.dynamic_reload,
                    'refresh_interval': tab.refresh_interval,
                    **tab.extra_attrs
                }
                app_tabs.append(tab_data)
            
            # Sort by order
            app_tabs.sort(key=lambda x: x['order'])
            manifest_data['apps'][app_name] = {
                'tab_count': len(app_tabs),
                'tabs': app_tabs
            }
        
        # Write to file if path provided (with atomic operation from htmx_tabber)
        if output_path:
            target_path = Path(output_path)
        else:
            target_dir = Path(settings.BASE_DIR) / "staticfiles" / "js"
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / "x_tab_manifest.json"
        
        try:
            # Atomic file write (extracted from htmx_tabber)
            tmp_file = target_path.with_suffix(".tmp")
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2)
            os.replace(tmp_file, target_path)  # atomic swap
            print(f"✅ X-Tab manifest updated at {target_path}")
        except Exception as e:
            print(f"⚠️ Could not write X-Tab manifest: {e}")
        
        return manifest_data


# Global registry instance
tab_registry = TabRegistry()


# ============================================================================
# CONVENIENCE FUNCTIONS FOR COMPATIBILITY
# ============================================================================

def get_x_tab_manifest() -> dict:
    """
    Convenience function to generate X-Tab manifest.
    Enhanced replacement for htmx_tabber() functionality.
    
    Returns:
        dict: Complete tab manifest with all apps and tabs
    """
    return TabRegistry.generate_tab_manifest()


def export_x_tab_manifest_json():
    """
    Export X-Tab manifest to JSON file and return JsonResponse.
    Direct replacement for htmx_tabber() function.
    
    Returns:
        JsonResponse: Tab manifest as JSON response
    """
    from django.http import JsonResponse
    
    manifest = TabRegistry.generate_tab_manifest()
    
    # Return simplified format for API compatibility
    simplified_listing = []
    for app_name, app_data in manifest['apps'].items():
        for tab in app_data['tabs']:
            simplified_listing.append({
                'app_name': app_name,
                'tab_id': tab['tab_id'],
                'tab_name': tab['name'],
                'tab_slug': tab['tab_slug'],
                'template': tab['template'],
                'order': tab['order']
            })
    
    return JsonResponse(simplified_listing, safe=False)