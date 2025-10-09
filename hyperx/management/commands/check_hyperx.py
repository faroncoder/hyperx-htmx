"""
Django Management Command to Check HyperX Configuration
======================================================

Usage:
    python manage.py check_hyperx
    python manage.py check_hyperx --settings-file /path/to/settings.py
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from ...opt.hyperx.core_install_hyperx import *
from ...core.core import *

class Command(BaseCommand):
    help = 'Check HyperX configuration and installation status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--settings-file',
            type=str,
            help='Path to the settings.py file to check (default: current Django settings)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed configuration information',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 HyperX Configuration Check')
        )
        self.stdout.write('=' * 40)

        # Check installation status
        installation_status = self._check_installation()
        
        # Check configuration
        config_status = self._check_configuration(options['verbose'])
        
        # Check middleware order
        middleware_status = self._check_middleware_order()
        
        # Summary
        self._show_summary(installation_status, config_status, middleware_status)

    def _check_installation(self):
        """Check if HyperX apps are installed."""
        self.stdout.write("\n📦 Installation Status:")
        
        status = {}
        
        # Check INSTALLED_APPS
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        
        django_htmx_installed = 'django_htmx' in installed_apps
        hyperx_installed = 'hyperx' in installed_apps
        
        if django_htmx_installed:
            self.stdout.write("   ✅ django_htmx is installed")
        else:
            self.stdout.write("   ❌ django_htmx is NOT installed")
            
        if hyperx_installed:
            self.stdout.write("   ✅ hyperx is installed")
        else:
            self.stdout.write("   ❌ hyperx is NOT installed")
        
        status['apps_installed'] = django_htmx_installed and hyperx_installed
        status['django_htmx'] = django_htmx_installed
        status['hyperx'] = hyperx_installed
        
        return status

    def _check_configuration(self, verbose=False):
        """Check HyperX configuration settings."""
        self.stdout.write("\n⚙️ Configuration Status:")
        
        status = {}
        
        # Check HYPERX_MIDDLEWARE config
        hyperx_middleware_config = getattr(settings, 'HYPERX_MIDDLEWARE', None)
        if hyperx_middleware_config:
            self.stdout.write("   ✅ HYPERX_MIDDLEWARE is configured")
            if verbose:
                for key, value in hyperx_middleware_config.items():
                    self.stdout.write(f"      {key}: {value}")
        else:
            self.stdout.write("   ❌ HYPERX_MIDDLEWARE is NOT configured")
            
        # Check HYPERX_SECURITY config
        hyperx_security_config = getattr(settings, 'HYPERX_SECURITY', None)
        if hyperx_security_config:
            self.stdout.write("   ✅ HYPERX_SECURITY is configured")
            if verbose:
                for key, value in hyperx_security_config.items():
                    self.stdout.write(f"      {key}: {value}")
        else:
            self.stdout.write("   ⚠️ HYPERX_SECURITY is not configured (optional)")
        
        status['middleware_config'] = hyperx_middleware_config is not None
        status['security_config'] = hyperx_security_config is not None
        
        return status

    def _check_middleware_order(self):
        """Check if HyperX middleware is in the correct order."""
        self.stdout.write("\n🔧 Middleware Order:")
        
        middleware = getattr(settings, 'MIDDLEWARE', [])
        
        status = {}
        required_middleware = [
            'django_htmx.middleware.HtmxMiddleware',
            'hyperx.middleware.HyperXMiddleware',
        ]
        optional_middleware = [
            'hyperx.middleware.HyperXSecurityMiddleware',
        ]
        
        # Check if required middleware is present
        for mw in required_middleware:
            if mw in middleware:
                pos = middleware.index(mw)
                self.stdout.write(f"   ✅ {mw} (position {pos})")
                status[mw] = True
            else:
                self.stdout.write(f"   ❌ {mw} is NOT installed")
                status[mw] = False
        
        # Check optional middleware
        for mw in optional_middleware:
            if mw in middleware:
                pos = middleware.index(mw)
                self.stdout.write(f"   ✅ {mw} (position {pos})")
                status[mw] = True
            else:
                self.stdout.write(f"   ⚠️ {mw} is not installed (optional)")
                status[mw] = False
        
        # Check order
        csrf_pos = -1
        auth_pos = -1
        
        for i, mw in enumerate(middleware):
            if 'csrf' in mw.lower():
                csrf_pos = i
            elif 'auth' in mw.lower() and 'AuthenticationMiddleware' in mw:
                auth_pos = i
        
        htmx_pos = middleware.index('django_htmx.middleware.HtmxMiddleware') if 'django_htmx.middleware.HtmxMiddleware' in middleware else -1
        hyperx_pos = middleware.index('hyperx.middleware.HyperXMiddleware') if 'hyperx.middleware.HyperXMiddleware' in middleware else -1
        
        if htmx_pos > csrf_pos and htmx_pos < auth_pos and hyperx_pos > htmx_pos:
            self.stdout.write("   ✅ Middleware order is correct")
            status['order_correct'] = True
        else:
            self.stdout.write("   ⚠️ Middleware order may need adjustment")
            self.stdout.write("      Recommended order: CSRF → HTMX → HyperX → Auth")
            status['order_correct'] = False
            
        return status

    def _show_summary(self, installation_status, config_status, middleware_status):
        """Show overall summary."""
        self.stdout.write("\n" + "="*40)
        self.stdout.write("📊 Summary:")
        
        all_good = True
        
        if not installation_status['apps_installed']:
            self.stdout.write("   ❌ Installation incomplete")
            all_good = False
        
        if not config_status['middleware_config']:
            self.stdout.write("   ❌ Configuration incomplete")
            all_good = False
            
        required_mw = [
            'django_htmx.middleware.HtmxMiddleware',
            'hyperx.middleware.HyperXMiddleware'
        ]
        
        if not all(middleware_status.get(mw, False) for mw in required_mw):
            self.stdout.write("   ❌ Middleware setup incomplete")
            all_good = False
        
        if all_good:
            self.stdout.write(
                self.style.SUCCESS("   🎉 HyperX is properly configured!")
            )
        else:
            self.stdout.write(
                self.style.WARNING("   ⚠️ HyperX setup needs attention")
            )
            self.stdout.write("\n💡 Suggestions:")
            self.stdout.write("   Run: python manage.py install_hyperx")
            self.stdout.write("   Or check the installation documentation")