from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin
from django.shortcuts import render
from htmx_core.utils.htmx_helpers import add_htmx_trigger
from django.contrib.messages.views import SuccessMessageMixin
from htmx_core.utils.htmx_defaults import smart_redirect
# TemplateView import removed - unused


class HTMXMessageMixin(SuccessMessageMixin):
    """
    Mixin to add HTMX-friendly messaging to views
    """
    
    def add_htmx_message(self, request, message, level='info'):
        """
        Add a message that works well with HTMX
        """
        from django.contrib import messages
        
        # Add Django message
        getattr(messages, level)(request, message)
        
        # Also add to response for immediate display if HTMX
        if hasattr(self, 'response') and request.headers.get('HX-Request') == 'true':
            add_htmx_trigger(self.response, 'showMessage', {
                'message': message,
                'level': level
            })
    
    def success_message_htmx(self, request, message):
        """Add success message for HTMX"""
        self.add_htmx_message(request, message, 'success')
    
    def error_message_htmx(self, request, message):
        """Add error message for HTMX"""
        self.add_htmx_message(request, message, 'error')
    
    def warning_message_htmx(self, request, message):
        """Add warning message for HTMX"""
        self.add_htmx_message(request, message, 'warning')





class HTMXRedirectMixin(TemplateResponseMixin):
    """
    Mixin for class-based views to handle HTMX redirects automatically
    """
    
    def redirect_htmx_compatible(self, url, force_clear=False):
        """Redirect in HTMX-compatible way"""
        return smart_redirect(self.request, url, force_clear)
    
    def success_redirect(self, message, url, force_clear=True):
        """Redirect with success message"""
        from django.contrib import messages
        messages.success(self.request, message)
        return self.redirect_htmx_compatible(url, force_clear)
    
    def error_redirect(self, message, url, force_clear=False):
        """Redirect with error message"""
        from django.contrib import messages  
        messages.error(self.request, message)
        return self.redirect_htmx_compatible(url, force_clear)




class HTMXLoginRequiredMixin(LoginRequiredMixin):
    """
    If the request is HTMX, render the login form inline without redirect,
    so the URL bar never changes. Otherwise, fall back to normal redirect.
    """
    def handle_no_permission(self):
        # Check if this is an HTMX request
        if self.request.headers.get("HX-Request") == "true":
            # Instead of redirecting, return the login form HTML
            from htmx_core.forms.auth_forms import LoginForm
            from django.urls import reverse
            
            form = LoginForm(request=self.request)
            
            context = {
                'title': 'Login Required',
                'form': form,
                'page_title': 'Please Sign In',
                'message': 'Please sign in to continue',
                'login_submit_url': reverse('core:login_submit'),
            }
            
            
            # update this line to match your login template 
            return render(self.request, 'core/auth/login_form_crispy.html', context, status=401)
        
           
           
        
        # For non-HTMX requests, use normal redirect
        return super().handle_no_permission()

