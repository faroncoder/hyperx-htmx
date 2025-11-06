"""
X-Tab System Generator and Mixin
===============================

Automated tab discovery and standardization system for HTMX-based tabbed interfaces.
Uses os.walk() to discover tab definitions and automatically stack them together.

FEATURES:
- X-Tab header-based tab switching
- Automatic tab discovery from filesystem
- Dynamic context loading per tab
- HTMX-compatible partial rendering
- Permission-based tab filtering
"""

import os
import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from django.conf import settings
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class XTabDefinition:
    """
    Standard tab definition structure
    """
    def __init__(self, tab_id: str, name: str, template: str, context_method: str = None, 
                 permission_level: int = 0, icon: str = "fas fa-tab", order: int = 100):
        self.tab_id = tab_id
        self.name = name  
        self.template = template
        self.context_method = context_method or f"_get_{tab_id}_context"
        self.permission_level = permission_level
        self.icon = icon
        self.order = order
    
    def to_dict(self):
        return {
            'tab_id': self.tab_id,
            'name': self.name,
            'template': self.template,
            'context_method': self.context_method,
            'permission_level': self.permission_level,
            'icon': self.icon,
            'order': self.order
        }


class XTabGenerator:
    """
    Automated tab discovery and registration system
    Uses os.walk() to find tab definition files and stack them together
    """
    
    def __init__(self, search_paths: List[str] = None):
        self.search_paths = search_paths or [
            os.path.join(settings.BASE_DIR, 'htmx_core', 'tabs'),
            os.path.join(settings.BASE_DIR, 'acct', 'tabs'), 
            os.path.join(settings.BASE_DIR, 'frontend', 'tabs'),
        ]
        self.discovered_tabs: Dict[str, XTabDefinition] = {}
        self.tab_collections: Dict[str, List[XTabDefinition]] = {}
    
    def discover_tabs(self) -> Dict[str, XTabDefinition]:
        """
        Walk through filesystem to discover tab definitions
        
        Searches for files matching patterns:
        - *_tab_def.py (tab definition files)
        - *_tabs.py (tab collection files)
        - tabs/*.py (tab directory files)
        """
        logger.info("🔍 Starting X-Tab discovery process...")
        
        for search_path in self.search_paths:
            if not os.path.exists(search_path):
                logger.debug(f"Search path doesn't exist: {search_path}")
                continue
                
            logger.info(f"🔍 Searching for tabs in: {search_path}")
            
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if self._is_tab_definition_file(file):
                        file_path = os.path.join(root, file)
                        self._process_tab_file(file_path)
        
        logger.info(f"✅ Discovered {len(self.discovered_tabs)} tabs across {len(self.tab_collections)} collections")
        return self.discovered_tabs
    
    def _is_tab_definition_file(self, filename: str) -> bool:
        """Check if file contains tab definitions"""
        tab_patterns = [
            '_tab_def.py',
            '_tabs.py', 
            'tab_config.py',
            'tabs.py'
        ]
        return any(pattern in filename for pattern in tab_patterns) and filename.endswith('.py')
    
    def _process_tab_file(self, file_path: str):
        """Process a discovered tab definition file"""
        try:
            # Load module dynamically
            spec = importlib.util.spec_from_file_location("tab_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for tab definitions
            if hasattr(module, 'TAB_DEFINITIONS'):
                self._register_tabs_from_definitions(module.TAB_DEFINITIONS, file_path)
            
            if hasattr(module, 'TABS'):
                self._register_tabs_from_dict(module.TABS, file_path)
                
            if hasattr(module, 'register_tabs'):
                tabs = module.register_tabs()
                self._register_tabs_from_callable(tabs, file_path)
                
        except Exception as e:
            logger.warning(f"Failed to process tab file {file_path}: {e}")
    
    def _register_tabs_from_definitions(self, definitions: List[Dict], source_file: str):
        """Register tabs from TAB_DEFINITIONS list"""
        for tab_def in definitions:
            tab = XTabDefinition(**tab_def)
            self.discovered_tabs[tab.tab_id] = tab
            logger.debug(f"Registered tab '{tab.tab_id}' from {source_file}")
    
    def _register_tabs_from_dict(self, tabs_dict: Dict, source_file: str):
        """Register tabs from TABS dictionary"""
        for tab_id, config in tabs_dict.items():
            if isinstance(config, dict):
                config['tab_id'] = tab_id
                tab = XTabDefinition(**config)
                self.discovered_tabs[tab_id] = tab
                logger.debug(f"Registered tab '{tab_id}' from {source_file}")
    
    def _register_tabs_from_callable(self, tabs: Any, source_file: str):
        """Register tabs from callable function"""
        if isinstance(tabs, list):
            self._register_tabs_from_definitions(tabs, source_file)
        elif isinstance(tabs, dict):
            self._register_tabs_from_dict(tabs, source_file)
    
    def get_tabs_for_collection(self, collection_name: str, 
                               user_permission_level: int = 0) -> List[XTabDefinition]:
        """
        Get tabs filtered by collection name and user permissions
        """
        all_tabs = self.discover_tabs()
        filtered_tabs = []
        
        for tab in all_tabs.values():
            # Permission check
            if tab.permission_level > user_permission_level:
                continue
                
            # Collection filter (if specified)
            if collection_name and collection_name not in getattr(tab, 'collections', [collection_name]):
                continue
                
            filtered_tabs.append(tab)
        
        # Sort by order
        return sorted(filtered_tabs, key=lambda t: t.order)
    
    def generate_tab_registry(self) -> Dict[str, Any]:
        """
        Generate complete tab registry for use in views
        """
        tabs = self.discover_tabs()
        
        registry = {
            'tabs': {tab_id: tab.to_dict() for tab_id, tab in tabs.items()},
            'allowed_tabs': set(tabs.keys()),
            'partials': {tab_id: tab.template for tab_id, tab in tabs.items()},
            'context_methods': {tab_id: tab.context_method for tab_id, tab in tabs.items()},
            'permissions': {tab_id: tab.permission_level for tab_id, tab in tabs.items()},
        }
        
        return registry


class XTabMixin:
    """
    Reusable mixin for X-Tab header-based tabbed interfaces
    
    USAGE:
    class MyDashboardView(XTabMixin, TemplateView):
        x_tab_collection = "dashboard"  # Optional: filter tabs by collection
        x_tab_default = "overview"      # Default tab
        x_tab_permission_required = 0   # Minimum permission level
    """
    
    x_tab_collection: Optional[str] = None
    x_tab_default: str = "overview"
    x_tab_permission_required: int = 0
    x_tab_generator: XTabGenerator = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.x_tab_generator is None:
            self.x_tab_generator = XTabGenerator()
    
    def get_x_tab(self) -> str:
        """Get current tab from X-Tab header or default"""
        tab = self.request.headers.get('X-Tab', self.x_tab_default)
        allowed_tabs = self.get_allowed_tabs()
        return tab if tab in allowed_tabs else self.x_tab_default
    
    def get_allowed_tabs(self) -> set:
        """Get tabs allowed for current user"""
        user_permission = self.get_user_permission_level()
        tabs = self.x_tab_generator.get_tabs_for_collection(
            self.x_tab_collection, 
            user_permission
        )
        return {tab.tab_id for tab in tabs}
    
    def get_user_permission_level(self) -> int:
        """Get current user's permission level"""
        if not self.request.user.is_authenticated:
            return 0
        return getattr(
            getattr(self.request.user, 'rbac_role', None), 
            'permission_level', 
            0
        )
    
    def get_tab_registry(self) -> Dict[str, Any]:
        """Get complete tab registry for current user"""
        return self.x_tab_generator.generate_tab_registry()
    
    def get_context_data(self, **kwargs):
        """Enhanced context with X-Tab support"""
        context = super().get_context_data(**kwargs)
        
        current_tab = self.get_x_tab()
        registry = self.get_tab_registry()
        
        # Base X-Tab context
        context.update({
            'current_tab': current_tab,
            'x_tab_registry': registry,
            'allowed_tabs': self.get_allowed_tabs(),
            'user_permission_level': self.get_user_permission_level(),
        })
        
        # Load tab-specific context
        context_method = registry['context_methods'].get(current_tab)
        if context_method and hasattr(self, context_method):
            tab_context = getattr(self, context_method)()
            if isinstance(tab_context, dict):
                context.update(tab_context)
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        """Render X-Tab aware response"""
        current_tab = self.get_x_tab()
        registry = self.get_tab_registry()
        
        # For HTMX requests, render the specific tab partial
        if self.request.headers.get('HX-Request') == 'true':
            partial_template = registry['partials'].get(current_tab)
            if partial_template:
                return render(self.request, partial_template, context)
        
        # For non-HTMX requests, render full page
        return super().render_to_response(context, **response_kwargs)


class XTabFormView(XTabMixin, TemplateView):
    """
    Specialized X-Tab view for forms with tabbed sections.
    
    Features:
    - Form validation with tab-specific error handling
    - Progress tracking across tabs
    - Auto-save functionality per tab
    - Form state persistence
    
    Example:
        class UserProfileFormView(XTabFormView):
            form_class = UserProfileForm
            x_tab_collection = 'user_profile_tabs'
            success_url = '/profile/saved/'
            
            def _get_personal_context(self, request):
                return {'form': self.get_form()}
    """
    
    form_class = None
    success_url = None
    form_prefix = 'xtab_form'
    auto_save_enabled = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._form_instances = {}  # Cache forms per tab
        self._validation_errors = {}  # Track errors per tab
    
    def get_form_class(self, tab_id=None):
        """Get form class for specific tab or default"""
        if tab_id and hasattr(self, f'get_{tab_id}_form_class'):
            return getattr(self, f'get_{tab_id}_form_class')()
        return self.form_class
    
    def get_form(self, tab_id=None, form_class=None):
        """Get form instance for specific tab"""
        tab_id = tab_id or self.get_x_tab()
        
        # Return cached form if exists
        if tab_id in self._form_instances:
            return self._form_instances[tab_id]
        
        # Create new form instance
        form_class = form_class or self.get_form_class(tab_id)
        if form_class:
            form_kwargs = self.get_form_kwargs(tab_id)
            form = form_class(**form_kwargs)
            self._form_instances[tab_id] = form
            return form
        
        return None
    
    def get_form_kwargs(self, tab_id):
        """Get form kwargs for specific tab"""
        kwargs = {
            'prefix': f'{self.form_prefix}_{tab_id}',
        }
        
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        
        # Add instance if available
        if hasattr(self, 'get_object'):
            kwargs['instance'] = self.get_object()
        
        return kwargs
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests with tab-aware form processing"""
        current_tab = self.get_x_tab()
        form = self.get_form(current_tab)
        
        if form and form.is_valid():
            return self.form_valid(form, current_tab)
        else:
            return self.form_invalid(form, current_tab)
    
    def form_valid(self, form, tab_id):
        """Handle valid form submission"""
        # Save form data
        if hasattr(form, 'save'):
            form.save()
        
        # Auto-save functionality
        if self.auto_save_enabled:
            self._save_tab_progress(tab_id, form.cleaned_data)
        
        # Check if this is the final tab
        if self._is_final_tab(tab_id):
            return self._handle_final_submission()
        
        # Move to next tab or show success message
        next_tab = self._get_next_tab(tab_id)
        if next_tab and self.request.htmx:
            response = self._render_tab_response(next_tab)
            response['HX-Trigger'] = f'{{"tabProgress": "{tab_id}", "nextTab": "{next_tab}"}}'
            return response
        
        return self.render_to_response(self.get_context_data(form=form))
    
    def form_invalid(self, form, tab_id):
        """Handle invalid form submission"""
        self._validation_errors[tab_id] = form.errors
        
        if self.request.htmx:
            # Return just the form section with errors
            context = self.get_context_data(form=form)
            response = self._render_tab_response(tab_id, context)
            response['HX-Trigger'] = f'{{"formErrors": "{tab_id}"}}'
            return response
        
        return self.render_to_response(self.get_context_data(form=form))
    
    def get_context_data(self, **kwargs):
        """Enhanced context with form and progress tracking"""
        context = super().get_context_data(**kwargs)
        
        current_tab = self.get_x_tab()
        
        # Add form context
        if 'form' not in kwargs:
            form = self.get_form(current_tab)
            if form:
                context['form'] = form
        
        # Add progress tracking
        context.update({
            'form_progress': self._get_form_progress(),
            'validation_errors': self._validation_errors,
            'current_tab_errors': self._validation_errors.get(current_tab, {}),
            'is_final_tab': self._is_final_tab(current_tab),
            'next_tab': self._get_next_tab(current_tab),
            'previous_tab': self._get_previous_tab(current_tab),
            'auto_save_enabled': self.auto_save_enabled,
        })
        
        return context
    
    def _save_tab_progress(self, tab_id, data):
        """Save progress for specific tab (override for custom storage)"""
        # Default: store in session
        if 'xtab_progress' not in self.request.session:
            self.request.session['xtab_progress'] = {}
        
        self.request.session['xtab_progress'][tab_id] = data
        self.request.session.modified = True
    
    def _get_form_progress(self):
        """Get form completion progress"""
        registry = self.get_tab_registry()
        total_tabs = len(registry.get('tabs', []))
        
        if total_tabs == 0:
            return 100
        
        completed_tabs = len([
            tab for tab in registry['tabs'] 
            if self._is_tab_completed(tab['tab_id'])
        ])
        
        return int((completed_tabs / total_tabs) * 100)
    
    def _is_tab_completed(self, tab_id):
        """Check if specific tab is completed"""
        progress = self.request.session.get('xtab_progress', {})
        return tab_id in progress and tab_id not in self._validation_errors
    
    def _is_final_tab(self, tab_id):
        """Check if this is the final tab"""
        registry = self.get_tab_registry()
        tabs = sorted(registry.get('tabs', []), key=lambda x: x.get('order', 100))
        return tabs and tabs[-1]['tab_id'] == tab_id
    
    def _get_next_tab(self, current_tab):
        """Get next tab ID"""
        registry = self.get_tab_registry()
        tabs = sorted(registry.get('tabs', []), key=lambda x: x.get('order', 100))
        
        current_index = None
        for i, tab in enumerate(tabs):
            if tab['tab_id'] == current_tab:
                current_index = i
                break
        
        if current_index is not None and current_index < len(tabs) - 1:
            return tabs[current_index + 1]['tab_id']
        
        return None
    
    def _get_previous_tab(self, current_tab):
        """Get previous tab ID"""
        registry = self.get_tab_registry()
        tabs = sorted(registry.get('tabs', []), key=lambda x: x.get('order', 100))
        
        current_index = None
        for i, tab in enumerate(tabs):
            if tab['tab_id'] == current_tab:
                current_index = i
                break
        
        if current_index is not None and current_index > 0:
            return tabs[current_index - 1]['tab_id']
        
        return None
    
    def _handle_final_submission(self):
        """Handle final form submission across all tabs"""
        if self.success_url:
            if self.request.htmx:
                response = HttpResponse()
                response['HX-Redirect'] = self.success_url
                return response
            else:
                from django.shortcuts import redirect
                return redirect(self.success_url)
        
        return self.render_to_response(self.get_context_data())
    
    def _render_tab_response(self, tab_id, context=None):
        """Render response for specific tab"""
        if context is None:
            context = self.get_context_data()
        
        registry = self.get_tab_registry()
        template = registry['partials'].get(tab_id)
        
        if template:
            return render(self.request, template, context)
        
        return self.render_to_response(context)


class XTabAPIView(XTabMixin, TemplateView):
    """
    Specialized X-Tab view for API endpoints with tabbed responses.
    
    Features:
    - JSON responses for HTMX requests
    - HTML responses for direct access
    - Tab-specific data serialization
    - Pagination support per tab
    - Caching per tab endpoint
    
    Example:
        class DataAnalyticsAPIView(XTabAPIView):
            x_tab_collection = 'analytics_tabs'
            
            def _get_sales_context(self, request):
                return {'sales_data': self.get_sales_data()}
            
            def _get_users_context(self, request):
                return {'users_data': self.get_users_data()}
    """
    
    content_type_json = 'application/json'
    content_type_html = 'text/html'
    cache_timeout = 300  # 5 minutes default cache
    paginate_by = 20
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests with JSON/HTML response logic"""
        current_tab = self.get_x_tab()
        
        # Check if this is an API request (JSON expected)
        if self._is_api_request():
            return self._render_json_response(current_tab)
        
        # Regular HTMX or browser request
        return self._render_html_response(current_tab)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests for data updates"""
        current_tab = self.get_x_tab()
        
        # Process tab-specific data updates
        if hasattr(self, f'_handle_{current_tab}_post'):
            result = getattr(self, f'_handle_{current_tab}_post')(request)
            if self._is_api_request():
                return JsonResponse(result)
        
        # Fall back to standard processing
        return self.get(request, *args, **kwargs)
    
    def _is_api_request(self):
        """Determine if this is an API request"""
        # Check Accept header
        accept_header = self.request.headers.get('Accept', '')
        if 'application/json' in accept_header:
            return True
        
        # Check for API parameter
        if self.request.GET.get('format') == 'json':
            return True
        
        # Check for API endpoint pattern
        if '/api/' in self.request.path:
            return True
        
        return False
    
    def _render_json_response(self, tab_id):
        """Render JSON response for API requests"""
        try:
            # Get tab-specific data
            context = self.get_context_data()
            tab_data = self._extract_tab_data(context, tab_id)
            
            # Apply pagination if enabled
            if self.paginate_by:
                tab_data = self._paginate_data(tab_data)
            
            response_data = {
                'status': 'success',
                'tab': tab_id,
                'data': tab_data,
                'meta': self._get_api_meta(context, tab_id)
            }
            
            response = JsonResponse(response_data)
            
            # Add caching headers
            if self.cache_timeout:
                response['Cache-Control'] = f'max-age={self.cache_timeout}'
            
            return response
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'tab': tab_id
            }, status=500)
    
    def _render_html_response(self, tab_id):
        """Render HTML response for regular requests"""
        context = self.get_context_data()
        
        # For HTMX requests, render the specific tab partial
        if self.request.headers.get('HX-Request') == 'true':
            registry = self.get_tab_registry()
            partial_template = registry['partials'].get(tab_id)
            if partial_template:
                return render(self.request, partial_template, context)
        
        # For non-HTMX requests, render full page
        return super().render_to_response(context)
    
    def _extract_tab_data(self, context, tab_id):
        """Extract relevant data for specific tab"""
        # Override this method for custom data extraction
        tab_context_method = f'_get_{tab_id}_context'
        if hasattr(self, tab_context_method):
            tab_context = getattr(self, tab_context_method)(self.request)
            return tab_context
        
        return context
    
    def _paginate_data(self, data):
        """Apply pagination to data"""
        page = int(self.request.GET.get('page', 1))
        per_page = int(self.request.GET.get('per_page', self.paginate_by))
        
        if isinstance(data, dict) and 'items' in data:
            items = data['items']
            start = (page - 1) * per_page
            end = start + per_page
            
            data['items'] = items[start:end]
            data['pagination'] = {
                'page': page,
                'per_page': per_page,
                'total': len(items),
                'pages': (len(items) + per_page - 1) // per_page
            }
        
        return data
    
    def _get_api_meta(self, context, tab_id):
        """Get metadata for API response"""
        return {
            'timestamp': self.request.META.get('HTTP_X_TIMESTAMP'),
            'user_id': self.request.user.id if self.request.user.is_authenticated else None,
            'tab_id': tab_id,
            'request_id': getattr(self.request, 'id', None)
        }


class XTabModalView(XTabMixin, TemplateView):
    """
    Specialized X-Tab view for modal dialogs with tabbed content.
    
    Features:
    - Modal-specific rendering
    - Auto-sizing based on content
    - Modal state management
    - Close/cancel handling
    - Tab validation before closing
    
    Example:
        class UserEditModalView(XTabModalView):
            modal_title = "Edit User Profile"
            modal_size = "lg"  # sm, md, lg, xl
            x_tab_collection = 'user_edit_tabs'
            
            def _get_profile_context(self, request):
                return {'user': self.get_object()}
    """
    
    modal_title = "Tabbed Modal"
    modal_size = "md"  # sm, md, lg, xl
    modal_backdrop = "static"  # true, false, static
    modal_keyboard = True
    modal_focus = True
    modal_show_close = True
    modal_show_footer = True
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests for modal content"""
        current_tab = self.get_x_tab()
        
        # Always render as modal content for HTMX requests
        if request.headers.get('HX-Request') == 'true':
            return self._render_modal_response(current_tab)
        
        # For direct access, render full page with modal
        return self._render_full_modal_page(current_tab)
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests (form submissions, etc.)"""
        current_tab = self.get_x_tab()
        action = request.POST.get('action', 'submit')
        
        if action == 'close':
            return self._handle_modal_close()
        elif action == 'cancel':
            return self._handle_modal_cancel()
        elif action == 'submit':
            return self._handle_modal_submit(current_tab)
        
        # Default: re-render modal
        return self._render_modal_response(current_tab)
    
    def _render_modal_response(self, tab_id):
        """Render modal content for HTMX requests"""
        context = self.get_context_data()
        context.update(self._get_modal_context())
        
        # Check if we should render just the tab content or full modal
        if self.request.headers.get('X-Tab-Content-Only') == 'true':
            # Render just the tab content (for tab switching within modal)
            registry = self.get_tab_registry()
            tab_template = registry['partials'].get(tab_id)
            if tab_template:
                return render(self.request, tab_template, context)
        
        # Render full modal with tabs
        modal_template = self._get_modal_template()
        response = render(self.request, modal_template, context)
        
        # Add modal-specific headers
        response['HX-Push-Url'] = 'false'  # Don't update URL for modals
        
        return response
    
    def _render_full_modal_page(self, tab_id):
        """Render full page with modal for direct access"""
        context = self.get_context_data()
        context.update(self._get_modal_context())
        context['render_full_page'] = True
        
        # Use base template that includes modal wrapper
        return render(self.request, self.get_template_names()[0], context)
    
    def _get_modal_context(self):
        """Get modal-specific context"""
        return {
            'modal_title': self.modal_title,
            'modal_size': self.modal_size,
            'modal_backdrop': self.modal_backdrop,
            'modal_keyboard': self.modal_keyboard,
            'modal_focus': self.modal_focus,
            'modal_show_close': self.modal_show_close,
            'modal_show_footer': self.modal_show_footer,
            'modal_id': f'modal_{self.x_tab_collection or "default"}',
            'current_tab': self.get_x_tab(),
        }
    
    def _get_modal_template(self):
        """Get template for modal rendering"""
        # Override this method to customize modal template
        return 'htmx_core/partials/x_tab_modal.html'
    
    def _handle_modal_close(self):
        """Handle modal close action"""
        # Check if all tabs are valid before closing
        if self._validate_all_tabs():
            return self._close_modal_success()
        else:
            return self._close_modal_with_errors()
    
    def _handle_modal_cancel(self):
        """Handle modal cancel action"""
        # Always allow cancel (no validation)
        response = HttpResponse()
        response['HX-Trigger'] = '{"modalClosed": {"action": "cancel"}}'
        return response
    
    def _handle_modal_submit(self, tab_id):
        """Handle modal submit action"""
        # Process submission for current tab
        if hasattr(self, f'_process_{tab_id}_submit'):
            result = getattr(self, f'_process_{tab_id}_submit')(self.request)
            
            if result.get('success', False):
                return self._close_modal_success(result)
            else:
                return self._render_modal_with_errors(tab_id, result.get('errors', {}))
        
        # Default: validation successful, close modal
        return self._close_modal_success()
    
    def _validate_all_tabs(self):
        """Validate all tabs before closing modal"""
        registry = self.get_tab_registry()
        
        for tab in registry.get('tabs', []):
            tab_id = tab['tab_id']
            if hasattr(self, f'_validate_{tab_id}'):
                if not getattr(self, f'_validate_{tab_id}')(self.request):
                    return False
        
        return True
    
    def _close_modal_success(self, data=None):
        """Close modal with success"""
        response = HttpResponse()
        trigger_data = {"modalClosed": {"action": "submit", "success": True}}
        if data:
            trigger_data["modalClosed"]["data"] = data
        
        response['HX-Trigger'] = json.dumps(trigger_data)
        return response
    
    def _close_modal_with_errors(self):
        """Handle modal close with validation errors"""
        context = self.get_context_data()
        context.update(self._get_modal_context())
        context['has_validation_errors'] = True
        
        # Re-render modal with error indicators
        modal_template = self._get_modal_template()
        response = render(self.request, modal_template, context)
        response['HX-Trigger'] = '{"modalValidationError": true}'
        
        return response
    
    def _render_modal_with_errors(self, tab_id, errors):
        """Re-render modal with errors for specific tab"""
        context = self.get_context_data()
        context.update(self._get_modal_context())
        context['tab_errors'] = {tab_id: errors}
        
        modal_template = self._get_modal_template()
        return render(self.request, modal_template, context)


# Global tab generator instance
x_tab_generator = XTabGenerator()