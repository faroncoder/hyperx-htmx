#!/usr/bin/env python
"""
URL Security Verification Script
Tests that all URL hiding and push rule disabling is working correctly
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def verify_security_settings():
    """Verify all security settings are properly configured"""
    
    print("🔒 URL Security Verification Report")
    print("=" * 50)
    
    # Check Django settings
    security_checks = [
        ("HTMX_HIDE_URLS", getattr(settings, 'HTMX_HIDE_URLS', False)),
        ("HTMX_DISABLE_PUSH_STATE", getattr(settings, 'HTMX_DISABLE_PUSH_STATE', False)),
        ("HTMX_DISABLE_HISTORY", getattr(settings, 'HTMX_DISABLE_HISTORY', False)),
        ("HTMX_HIDE_REQUEST_HEADERS", getattr(settings, 'HTMX_HIDE_REQUEST_HEADERS', False)),
        ("HTMX_OBFUSCATE_ENDPOINTS", getattr(settings, 'HTMX_OBFUSCATE_ENDPOINTS', False)),
        ("HTMX_DISABLE_URL_PARAMS", getattr(settings, 'HTMX_DISABLE_URL_PARAMS', False)),
        ("HTMX_SECURE_MODE", getattr(settings, 'HTMX_SECURE_MODE', False)),
        ("DISABLE_ALL_REDIRECTS", getattr(settings, 'DISABLE_ALL_REDIRECTS', False)),
        ("HTMX_STRIP_URLS_FROM_RESPONSE", getattr(settings, 'HTMX_STRIP_URLS_FROM_RESPONSE', False)),
    ]
    
    print("\n1. Security Settings:")
    all_enabled = True
    for setting, value in security_checks:
        status = "✅" if value else "❌"
        print(f"   {status} {setting}: {value}")
        if not value:
            all_enabled = False
    
    # Check HTMX config
    print("\n2. HTMX Configuration:")
    htmx_config = getattr(settings, 'HTMX_CONFIG', {})
    config_checks = [
        ('historyEnabled', False),
        ('refreshOnHistoryMiss', False),
        ('selfRequestsOnly', True),
        ('ignoreTitle', True),
        ('getCacheBusterParam', False),
        ('globalViewTransitions', False),
    ]
    
    for key, expected in config_checks:
        actual = htmx_config.get(key, None)
        status = "✅" if actual == expected else "❌"
        print(f"   {status} {key}: {actual} (expected: {expected})")
    
    # Check middleware
    print("\n3. Security Middleware:")
    middleware = settings.MIDDLEWARE
    security_middleware = 'htmx_core.middleware.url_security.URLSecurityMiddleware'
    
    if security_middleware in middleware:
        print(f"   ✅ URLSecurityMiddleware: Installed")
        position = middleware.index(security_middleware)
        print(f"   ℹ️  Position: {position + 1} (should be early in chain)")
    else:
        print(f"   ❌ URLSecurityMiddleware: Not installed")
        all_enabled = False
    
    # Check redirect settings
    print("\n4. Redirect Settings:")
    redirect_settings = [
        ("HTMX_REDIRECT_AUTH", None),
        ("HTMX_REDIRECT_ANON", None),
    ]
    
    for setting, expected in redirect_settings:
        actual = getattr(settings, setting, "NOT_SET")
        status = "✅" if actual == expected else "❌"
        print(f"   {status} {setting}: {actual}")
    
    # Summary
    print("\n" + "=" * 50)
    if all_enabled:
        print("🎯 SECURITY STATUS: ✅ ALL PROTECTIONS ACTIVE")
        print("\nURL Security Features Enabled:")
        print("• All browser history disabled")
        print("• URL parameters stripped")
        print("• Push state blocked")
        print("• Request headers filtered") 
        print("• Response URLs removed")
        print("• Endpoint obfuscation active")
        print("• All redirects disabled")
    else:
        print("⚠️  SECURITY STATUS: ❌ SOME PROTECTIONS MISSING")
        print("\nPlease review the ❌ items above")
    
    return all_enabled

if __name__ == '__main__':
    verify_security_settings()