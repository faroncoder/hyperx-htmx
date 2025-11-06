
from django.views import View
from django.http import HttpResponse
from django.shortcuts import render
from typing import Dict, List, Any, Optional

# Import HTMX core functionality
try:
    from htmx_core.mixins.htmx_mixin import HTMXLoginRequiredMixin, HTMXMessageMixin
    from htmx_core.utils.htmx_helpers import get_dynamic_context, _get_htmx_render_mode
    from htmx_core.utils.htmx_defaults import get_htmx_template_context
except ImportError as e:
    print(f"[X-TABS] Warning: HTMX Core import failed: {e}")
    # Provide fallbacks
    class HTMXLoginRequiredMixin:
        pass
    class HTMXMessageMixin:
        pass
    def get_dynamic_context(*args, **kwargs):
        return {}
    def _get_htmx_render_mode(*args, **kwargs):
        return 'full'
    def get_htmx_template_context(*args, **kwargs):
        return {}

from htmx_core.utils.htmx_x_tab_registry import TabRegistry, XTabDefinition


class XTabMixin:
    """
    Mixin for views that support X-Tab tabbed interfaces.
    
    Provides X-Tab header detection, tab management, and automatic 
    context loading based on registered tab definitions.
    
    Usage:
        class MyView(XTabMixin, HTMXLoginRequiredMixin, View):
            app_name = 'my_app'
            default_tab = 'overview'
            
            def _get_overview_context(self, request):
                return {'data': 'overview specific data'}
    """
    
    # Configuration attributes
    app_name: str = None  # Must be set by implementing view
    default_tab: str = 'overview'
    base_template: str = 'base/x_tab_base.html'
    
    def get_current_tab(self) -> str:
        """Get current tab from X-Tab header or use default"""
        return self.request.headers.get('X-Tab', self.default_tab)
    
    def get_available_tabs(self) -> List[XTabDefinition]:
        """Get tabs available for current user and app"""
        if not self.app_name:
            raise ValueError("app_name must be set when using XTabMixin")
            
        all_tabs = TabRegistry.get_tabs_for_app(self.app_name)
        return TabRegistry.filter_tabs_for_user(all_tabs, self.request.user)
    
    def get_tab_definition(self, tab_id: str) -> Optional[XTabDefinition]:
        """Get specific tab definition by ID"""
        available_tabs = self.get_available_tabs()
        for tab in available_tabs:
            if tab.tab_id == tab_id:
                return tab
        return None
    
    def get_tab_context(self, tab_definition: XTabDefinition) -> Dict[str, Any]:
        """
        Get context for a specific tab by calling its context method.
        
        Args:
            tab_definition: The tab to get context for
            
        Returns:
            dict: Context data for the tab
        """
        context_method_name = tab_definition.context_method
        
        if hasattr(self, context_method_name):
            context_method = getattr(self, context_method_name)
            if callable(context_method):
                try:
                    return context_method(self.request) or {}
                except Exception as e:
                    print(f"[X-TABS] Error calling {context_method_name}: {e}")
                    return {}
        
        print(f"[X-TABS] Context method '{context_method_name}' not found")
        return {}
    
    def get_x_tab_context(self) -> Dict[str, Any]:
        """
        Build complete X-Tab context including tab data and current state.
        
        Returns:
            dict: Complete context for X-Tab rendering
        """
        current_tab = self.get_current_tab()
        available_tabs = self.get_available_tabs()
        current_tab_def = self.get_tab_definition(current_tab)
        
        # Base X-Tab context
        context = {
            'current_tab': current_tab,
            'available_tabs': available_tabs,
            'current_tab_definition': current_tab_def,
            'x_tab_config': {
                'app_name': self.app_name,
                'default_tab': self.default_tab,
                'base_template': self.base_template
            }
        }
        
        # Add current tab specific context
        if current_tab_def:
            tab_context = self.get_tab_context(current_tab_def)
            context.update(tab_context)
            
            # Add tab-specific template info
            context['tab_template'] = current_tab_def.template
            context['tab_config'] = current_tab_def.to_dict()
        
        return context
    
    def render_x_tab_response(self, extra_context: Optional[Dict] = None) -> HttpResponse:
        """
        Render X-Tab response with proper template selection.
        
        Args:
            extra_context: Additional context to include
            
        Returns:
            HttpResponse: Rendered X-Tab response
        """
        context = self.get_x_tab_context()
        
        if extra_context:
            context.update(extra_context)
        
        # Add HTMX core context if available
        try:
            from htmx_core.utils.htmx_defaults import htmx_xtab_defaults
            
            # Add X-Tab specific HTMX defaults
            xtab_defaults = htmx_xtab_defaults(self.request, "#x-tab-content")
            context.update(xtab_defaults)
            
            # Add general HTMX template context
            htmx_context = get_htmx_template_context(self.request, {})
            context.update(htmx_context)
        except Exception as e:
            print(f"[X-TABS] Warning: Could not load HTMX defaults: {e}")
        
        # Determine template based on X-Tab header and HTMX state
        current_tab_def = context.get('current_tab_definition')
        
        if self.request.headers.get('HX-Request') and current_tab_def:
            # HTMX request - render just the tab content
            template = current_tab_def.template
        else:
            # Full page request - render base template with tab content
            template = self.base_template
            
        return render(self.request, template, context)


class XTabView(XTabMixin, HTMXLoginRequiredMixin, HTMXMessageMixin, View):
    """
    Complete X-Tab view class that combines X-Tab functionality 
    with HTMX core mixins for authentication and messaging.
    
    This is a ready-to-use view class for X-Tab interfaces.
    
    Usage:
        class DashboardView(XTabView):
            app_name = 'dashboard'
            default_tab = 'overview'
            
            def get(self, request):
                return self.render_x_tab_response()
                
            def _get_overview_context(self, request):
                return {'dashboard_data': get_dashboard_data()}
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Enhanced dispatch with X-Tab logging"""
        current_tab = self.get_current_tab()
        is_htmx = request.headers.get('HX-Request', False)
        
        print(f"[X-TABS] {self.__class__.__name__} - Tab: {current_tab}, HTMX: {is_htmx}")
        
        return super().dispatch(request, *args, **kwargs)


class XTabAPIView(XTabMixin):
    """
    API-focused X-Tab view for JSON responses.
    
    Useful for HTMX endpoints that need tab-aware JSON responses.
    """
    
    def get_tab_data(self) -> Dict[str, Any]:
        """Get tab data as JSON-serializable dictionary"""
        context = self.get_x_tab_context()
        
        # Convert tab definitions to dictionaries
        if 'available_tabs' in context:
            context['available_tabs'] = [
                tab.to_dict() for tab in context['available_tabs']
            ]
        
        if 'current_tab_definition' in context and context['current_tab_definition']:
            context['current_tab_definition'] = context['current_tab_definition'].to_dict()
        
        return context