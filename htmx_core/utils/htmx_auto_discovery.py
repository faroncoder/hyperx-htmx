"""
HTMX Core Auto-Discovery System
==============================

Automatically discovers and registers HTMX components without manual registration.
"""

import os
import sys
import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Any, Type
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)

class HTMXAutoDiscovery:
    """Auto-discovery system for HTMX Core components"""
    
    def __init__(self, htmx_core_path: Path = None):
        # Default to htmx_core directory (parent of utils)
        self.htmx_core_path = htmx_core_path or Path(__file__).parent.parent
        self.discovered_components = {
            'middleware': {},
            'mixins': {},
            'helpers': {},
            'defaults': {},
            'decorators': {},
            'dispatchers': {},
            'static': {},
            'views': {},
            'forms': {},
        }
    
    def discover_all_components(self) -> Dict[str, Any]:
        """Discover all HTMX components automatically"""
        logger.info("🔍 Starting auto-discovery of HTMX components...")
        
        # Discover components by category
        self._discover_middleware()
        self._discover_mixins()
        self._discover_helpers()
        self._discover_defaults()
        self._discover_decorators()
        self._discover_dispatchers()
        self._discover_views()
        self._discover_forms()
        
        total_discovered = sum(len(components) for components in self.discovered_components.values())
        logger.info(f"✅ Auto-discovered {total_discovered} HTMX components across {len(self.discovered_components)} categories")
        
        return self.discovered_components
    
    def _discover_middleware(self):
        """Auto-discover middleware classes"""
        middleware_dir = self.htmx_core_path / 'middleware'
        if not middleware_dir.exists():
            return
        
        # Include all htmx_* middleware files
        for py_file in middleware_dir.glob('htmx_*.py'):
            if py_file.name.startswith('__'):
                continue
            
            module_path = f"htmx_core.middleware.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if ((name.endswith('Middleware') or name.startswith('HTMX')) and 
                        obj.__module__ == module_path and
                        hasattr(obj, '__init__')):
                        
                        self.discovered_components['middleware'][name] = obj
                        logger.debug(f"   🔗 Discovered middleware: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def _discover_mixins(self):
        """Auto-discover mixin classes"""
        mixins_dir = self.htmx_core_path / 'mixins'
        if not mixins_dir.exists():
            return
        
        # Include all htmx_* mixin files
        for py_file in mixins_dir.glob('htmx_*.py'):
            if py_file.name.startswith('__'):
                continue
            
            module_path = f"htmx_core.mixins.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if ((name.endswith('Mixin') or name.startswith('HTMX')) and 
                        obj.__module__ == module_path):
                        
                        self.discovered_components['mixins'][name] = obj
                        logger.debug(f"   🧩 Discovered mixin: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def _discover_helpers(self):
        """Auto-discover helper functions"""
        utils_dir = self.htmx_core_path / 'utils'
        if not utils_dir.exists():
            return
        
        # Auto-discover all htmx_* files in utils
        for py_file in utils_dir.glob('htmx_*.py'):
            if py_file.name.startswith('__'):
                continue
                
            module_path = f"htmx_core.utils.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if (obj.__module__ == module_path and 
                        not name.startswith('_') and
                        (name.startswith('hx_') or name.startswith('htmx_') or name.startswith('is_htmx'))):
                        
                        self.discovered_components['helpers'][name] = obj
                        logger.debug(f"   🛠️ Discovered helper: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def _discover_defaults(self):
        """Auto-discover default context functions"""
        utils_dir = self.htmx_core_path / 'utils'
        if not utils_dir.exists():
            return
        
        # Look for all htmx_*defaults*.py files
        for defaults_file in utils_dir.glob('htmx_*defaults*.py'):
            module_path = f"htmx_core.utils.{defaults_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if (obj.__module__ == module_path and 
                        not name.startswith('_') and
                        (name.endswith('_defaults') or name == 'htmx_tabber' or name.startswith('htmx_'))):
                        
                        self.discovered_components['defaults'][name] = obj
                        logger.debug(f"   ⚙️ Discovered default: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def _discover_decorators(self):
        """Auto-discover decorator functions"""
        utils_dir = self.htmx_core_path / 'utils'
        if not utils_dir.exists():
            return
        
        # Focus on htmx_* files for decorators
        for py_file in utils_dir.glob('htmx_*.py'):
            if py_file.name.startswith('__'):
                continue
            
            module_path = f"htmx_core.utils.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isfunction):
                    if (obj.__module__ == module_path and 
                        not name.startswith('_') and
                        ('required' in name.lower() or 'login' in name.lower() or 
                         name.startswith('htmx_') and ('decorator' in name.lower() or 'wrapper' in name.lower()))):
                        
                        self.discovered_components['decorators'][name] = obj
                        logger.debug(f"   🎯 Discovered decorator: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def _discover_dispatchers(self):
        """Auto-discover dispatcher classes"""
        dispatchers_dir = self.htmx_core_path / 'dispatchers'
        if not dispatchers_dir.exists():
            return
        
        # Include both htmx_* files and any dispatcher files
        for py_file in dispatchers_dir.glob('*.py'):
            if py_file.name.startswith('__'):
                continue
            
            module_path = f"htmx_core.dispatchers.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if ((name.endswith('Dispatcher') or name.startswith('HTMX') or name.startswith('Hyper')) and 
                        obj.__module__ == module_path):
                        
                        self.discovered_components['dispatchers'][name] = obj
                        logger.debug(f"   📡 Discovered dispatcher: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def _discover_views(self):
        """Auto-discover view functions and classes"""
        views_dir = self.htmx_core_path / 'views'
        if not views_dir.exists():
            return
        
        # Focus on htmx_* view files
        for py_file in views_dir.glob('htmx_*.py'):
            if py_file.name.startswith('__'):
                continue
            
            module_path = f"htmx_core.views.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module):
                    if (inspect.isfunction(obj) or inspect.isclass(obj)) and \
                       obj.__module__ == module_path and \
                       not name.startswith('_'):
                        
                        self.discovered_components['views'][name] = obj
                        logger.debug(f"   🌐 Discovered view: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def _discover_forms(self):
        """Auto-discover form classes"""
        forms_dir = self.htmx_core_path / 'forms'
        if not forms_dir.exists():
            return
        
        # Include all htmx_* form files
        for py_file in forms_dir.glob('htmx_*.py'):
            if py_file.name.startswith('__'):
                continue
            
            module_path = f"htmx_core.forms.{py_file.stem}"
            try:
                module = importlib.import_module(module_path)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if ((name.endswith('Form') or name.startswith('HTMX')) and 
                        obj.__module__ == module_path):
                        
                        self.discovered_components['forms'][name] = obj
                        logger.debug(f"   📝 Discovered form: {name}")
                        
            except Exception as e:
                logger.debug(f"   ⚠️ Skipped {module_path}: {e}")
    
    def get_registry_dict(self) -> Dict[str, Any]:
        """Convert discovered components to registry format"""
        return {
            "middleware": self.discovered_components['middleware'],
            "mixins": self.discovered_components['mixins'],
            "helpers": self.discovered_components['helpers'],
            "defaults": self.discovered_components['defaults'],
            "decorators": self.discovered_components['decorators'],
            "dispatchers": self.discovered_components['dispatchers'],
            "views": self.discovered_components['views'],
            "forms": self.discovered_components['forms'],
        }


def auto_discover_htmx_components() -> Dict[str, Any]:
    """Main entry point for auto-discovery"""
    discovery = HTMXAutoDiscovery()
    return discovery.discover_all_components()


def get_auto_registry() -> Dict[str, Any]:
    """Get auto-discovered components in registry format"""
    discovery = HTMXAutoDiscovery()
    discovery.discover_all_components()
    return discovery.get_registry_dict()