#!/usr/bin/env python
"""
Debug Helper Script for S5 Portal
Run this to diagnose common issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth.models import User
from htmx_core.views.views_dashboard import paneltab
from acct.views.views_account import get_user_context

def test_basic_functionality():
    """Test basic functionality that might be broken"""
    
    print("🔍 S5 Portal Debug Report")
    print("=" * 50)
    
    # Test 1: URL Resolution
    print("\n1. Testing URL Resolution:")
    try:
        url = reverse('htmx:paneltab')
        print(f"   ✅ Base URL: {url}")
        
        url_with_param = reverse('htmx:panel', kwargs={'tab_active': 'dashboard'})
        print(f"   ✅ Parameterized URL: {url_with_param}")
    except Exception as e:
        print(f"   ❌ URL Error: {e}")
    
    # Test 2: View Function
    print("\n2. Testing View Function:")
    try:
        factory = RequestFactory()
        request = factory.get('/hx/paneltab/dashboard/')
        request.user = User.objects.first() or User.objects.create_user('testuser', 'test@test.com', 'pass')
        
        # Test the view
        response = paneltab(request, 'dashboard')
        print(f"   ✅ View Response Status: {response.status_code}")
        print(f"   ✅ Response Type: {type(response).__name__}")
    except Exception as e:
        print(f"   ❌ View Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: User Context
    print("\n3. Testing User Context:")
    try:
        if 'request' in locals():
            context = get_user_context(request)
            print(f"   ✅ User Context Keys: {list(context.keys())}")
    except Exception as e:
        print(f"   ❌ User Context Error: {e}")
    
    # Test 4: Template Files
    print("\n4. Testing Template Files:")
    template_paths = [
        'templates/base/default.html',
        'templates/base/vessel_holder.html', 
        'templates/base/panels/dash_dashboard.html'
    ]
    
    for path in template_paths:
        if os.path.exists(path):
            print(f"   ✅ Found: {path}")
        else:
            print(f"   ❌ Missing: {path}")
    
    # Test 5: Static Files
    print("\n5. Testing Static Files:")
    static_paths = [
        'static/js/htmx.min.js',
        'static/css/styles.css',
        'static/css/all.min.css'
    ]
    
    for path in static_paths:
        if os.path.exists(path):
            print(f"   ✅ Found: {path}")
        else:
            print(f"   ❌ Missing: {path}")
    
    # Test 6: Database
    print("\n6. Testing Database:")
    try:
        from acct.models import PlatformUser
        user_count = User.objects.count()
        platform_user_count = PlatformUser.objects.count()
        print(f"   ✅ Users: {user_count}")
        print(f"   ✅ Platform Users: {platform_user_count}")
    except Exception as e:
        print(f"   ❌ Database Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Debug Complete!")
    print("\nIf you see any ❌ errors above, those are likely the issues.")
    print("If everything shows ✅, the problem might be:")
    print("- Browser cache (try hard refresh)")
    print("- Authentication issues (try logging in)")
    print("- JavaScript errors (check browser console)")
    print("- HTMX request issues (check network tab)")

if __name__ == '__main__':
    test_basic_functionality()