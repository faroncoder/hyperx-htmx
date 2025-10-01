# hyperx-htmx - Django

**HyperX – HTMX's Sidekick**

> TabX so fast! – the ultimate HTMX enhancement protocol for Django.
HyperX supercharges your Django+HTMX projects with a unified X-Tab protocol, attribute builders, decorators, security helpers, and response utilities.

Via PIP : 

`pip install hyperx-htmx`


[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.0+-green.svg)](https://djangoproject.com)
[![HTMX](https://img.shields.io/badge/HTMX-Compatible-orange.svg)](https://htmx.org)

##  What is HyperX?

- ** TabX Protocol**: Lightning-fast tab management with X-Tab headers
- ** Unified Attribute Builder**: Single function for all HTMX attributes
- ** Smart Middleware**: Auto-processing of HTMX requests and X-Tab headers
- ** Enhanced Security**: Built-in authentication, validation, and threat detection
- ** Performance Monitoring**: Real-time tracking and comprehensive logging
- ** Response Helpers**: 15+ HTMX response functions for every use case

##  Installation

### 1. Dependency: django-htmx

```bash
pip install django-htmx
```

### 2. Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    "django_htmx",  # default implementation
]
```

### 3. Git clone HyperX into your config directory or 

`pip install hyperx-htmx`

### 4. Add middleware to settings.py

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_htmx.middleware.HtmxMiddleware',  # default implementation
    'hyperx.middleware.HyperXMiddleware',   <---------------------------add this line
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 5. Add HyperX configuration to settings.py

```python
# HyperX Middleware Configuration
HYPERX_MIDDLEWARE = {
    'AUTO_VALIDATE_HTMX': True,      # Auto-validate HTMX requests
    'AUTO_PARSE_XTAB': True,         # Auto-parse X-Tab headers
    'SECURITY_LOGGING': True,        # Enhanced security logging
    'PERFORMANCE_TRACKING': True,    # Track request performance
    'STRICT_XTAB_VALIDATION': False, # Strict X-Tab format validation
}

HYPERX_SECURITY = {
    'RATE_LIMITING': True,           # Enable rate limiting
    'PATTERN_DETECTION': True,       # Detect suspicious patterns
    'AUTO_BLOCKING': False,          # Auto-block malicious requests
    'MAX_REQUESTS_PER_MINUTE': 60,   # Rate limit threshold
}
```

**Voilà! You are done.**

## Usage

### HTML Templates

```html
<!-- Method 1: Direct attribute rendering -->
<div {% for attr in hx_attrs %}{{ attr.name }}="{{ attr.value }}"{% endfor %}>
<button {% for attr in hx_attrs %}{{ attr.name }}="{{ attr.value }}"{% endfor %}>
<a {% for attr in hx_attrs %}{{ attr.name }}="{{ attr.value }}"{% endfor %}> 

<!-- Method 2: Advanced (easier once you understand the above) -->
<button {{ hx_attrs|htmx_attrs }}>Load Data</button>
```

### Views.py

```python
attrs = build_htmx_attrs(
    get='api:refresh',
    target='#content',
    trigger='load',
    on_before_request='showLoader()',
    on_after_request='hideLoader()',
    on_response_error='handleError(event)'
)
```

**That's it.** You will see the content get loaded without hardcoding the HTMX markers in HTML.

## Key Features

###  Smart Middleware (Auto-Processing!)

HyperX Middleware automatically handles HTMX detection and X-Tab parsing:

```python
# settings.py
MIDDLEWARE = [
    ...
    'your_app.utils.hyperx_middleware.HyperXMiddleware',
    ...
]

# Configuration
HYPERX_MIDDLEWARE = {
    'AUTO_VALIDATE_HTMX': True,      # Auto-validate HTMX requests
    'AUTO_PARSE_XTAB': True,         # Auto-parse X-Tab headers
    'SECURITY_LOGGING': True,        # Enhanced security logging
    'PERFORMANCE_TRACKING': True,    # Track request performance
}

# In your views - everything is automatic!
def my_view(request):
    if request.htmx:        # Auto-detected!
        if request.xtab:    # Auto-parsed!
            tab_name = request.xtab['tab']
            return JsonResponse({'tab': tab_name})
```

### ⚡ TabX Protocol (Revolutionary!)

The TabX protocol uses X-Tab headers for lightning-fast tab management:

```python
# Generate TabX headers automatically
attrs = build_htmx_attrs(
    get='profile:load',
    target='#tab-content',
    xtab=('profile', 'load', 'view', '1.0')
)
# Creates: X-Tab: "profile:1.0:load:view"

# Parse TabX in views
@xtab_required(expected_tab='profile')
def profile_view(request):
    tab_data = request.xtab  # Automatically parsed!
    return JsonResponse({'tab': tab_data['tab']})
```

###  Unified Attribute Builder

One function for ALL HTMX attributes:

```python
attrs = build_htmx_attrs(
    post='forms:submit',
    target='#form-container',
    swap='outerHTML',
    trigger='submit',
    confirm='Submit form?',
    headers={'X-CSRFToken': '{{ csrf_token }}'},
    on_before_request='showSpinner()',
    on_after_request='hideSpinner()',
    indicator='#loading'
)
```

###  Enhanced Security

Built-in authentication, validation, and threat protection:

```python
# Middleware provides automatic security
HYPERX_SECURITY = {
    'RATE_LIMITING': True,           # Prevent HTMX request flooding
    'PATTERN_DETECTION': True,       # Detect suspicious patterns
    'AUTO_BLOCKING': False,          # Auto-block malicious requests
    'MAX_REQUESTS_PER_MINUTE': 60,   # Rate limit threshold
}

# Decorators for additional protection
@htmx_login_required  # Shows inline login for HTMX, redirects for regular requests
@xtab_required(expected_tab='admin', expected_function='manage')
def admin_view(request):
    # Middleware already validated security!
    return render(request, 'admin_panel.html')
```

###  Response Helpers

15+ response helpers for every scenario:

```python
# Redirects & Navigation
return hx_redirect('/dashboard/')
return hx_refresh()
return hx_location('/profile/', target='#main')

# URL Management
return hx_push_url('/new-page/')
return hx_replace_url('/updated-page/')

# Dynamic Targeting
return hx_retarget('#different-element')
return hx_reswap('beforeend')

# Event Triggering
return hx_trigger('notification', {'message': 'Success!'})
return hx_trigger({
    'notification': {'type': 'success'},
    'analytics': {'action': 'form_submit'},
    'ui-update': {'refresh_menu': True}
})
```

##  Documentation

### Complete Function Reference

#### Core Utilities
- **`build_htmx_attrs()`** - Unified HTMX attribute generation
- **`htmx_form_submit()`** - Pre-configured form submission
- **`htmx_infinite_scroll()`** - Infinite scroll setup
- **`parse_xtab_header()`** - Parse TabX headers
- **`validate_xtab_request()`** - Validate TabX requests
- **`@xtab_required`** - Decorator for TabX validation
- **`@htmx_login_required`** - HTMX-aware authentication
- **`render_htmx()`** - Smart template rendering
- **`is_htmx_request()`** - Request type detection
- **`validate_htmx_request()`** - Enhanced request validation

#### Middleware Classes
- **`HyperXMiddleware`** - Auto-processing HTMX and X-Tab headers
- **`HyperXSecurityMiddleware`** - Enhanced security and threat protection
- **`add_hyperx_to_request()`** - Manual middleware integration utility

### Response Helpers

| Function | Purpose | Example |
|--------------------|-----------------------  |-------------------------------
| `hx_redirect()`    | Navigate without reload | `hx_redirect('/dashboard/')` 
| `hx_refresh()`     | Force page refresh      | `hx_refresh()` 
| `hx_location()`    | Navigate with options   | `hx_location('/profile/', target='#main')` 
| `hx_push_url()`    | Add to history          | `hx_push_url('/new-page/')` 
| `hx_replace_url()` | Replace history         | `hx_replace_url('/updated/')` 
| `hx_retarget()`    | Change target           | `hx_retarget('#new-target')` 
| `hx_reswap()`      | Change swap method      | `hx_reswap('beforeend')` 
| `hx_trigger()`     | Trigger events          | `hx_trigger('saved', {'id': 123})` 

## Real-World Examples

### Complete Dashboard with TabX + Middleware

```python
# views.py - With HyperX Middleware
@htmx_login_required
@xtab_required(expected_tab='dashboard')
def dashboard_view(request):
    # Middleware automatically parsed request.xtab!
    tab_function = request.xtab['function']
    
    if tab_function == 'refresh':
        data = get_dashboard_data()
        return render_htmx(request, 'dashboard/refresh.html', {
            'data': data,
            'refresh_attrs': build_htmx_attrs(
                get='dashboard:refresh',
                target='#dashboard-content',
                trigger='every 30s',
                xtab=('dashboard', 'refresh', 'auto', '1.1')
            ),
            # Middleware provides performance info in response headers:
            # X-HyperX-Processed: true
            # X-HyperX-Duration: 0.045s
        })
    
    return render_htmx(request, 'dashboard/main.html')

# Simplified version without decorators
def simple_dashboard_view(request):
    # Middleware handles all the heavy lifting!
    if request.htmx and request.xtab:
        if request.xtab['tab'] == 'dashboard':
            return render_htmx(request, 'dashboard_content.html')
    
    return render_htmx(request, 'dashboard_full.html')
```

### Interactive Form with Validation

```python
def contact_form_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return hx_trigger('form-success', {
                'message': 'Message sent successfully!',
                'redirect_url': '/thank-you/'
            })
    else:
        form = ContactForm()
    
    return render(request, 'contact_form.html', {
        'form': form,
        'submit_attrs': build_htmx_attrs(
            post='contact:submit',
            target='#contact-form',
            swap='outerHTML',
            on_before_request='disableSubmit()',
            on_after_request='enableSubmit()',
            indicator='#form-loading'
        )
    })
```

### Live Search with Debouncing

```python
def search_view(request):
    query = request.GET.get('q', '')
    if query:
        results = search_database(query)
        return render(request, 'search_results.html', {'results': results})
    
    return render(request, 'search.html', {
        'search_attrs': build_htmx_attrs(
            get='search:results',
            target='#search-results',
            trigger='keyup changed delay:500ms',
            vals='{"live": true}',
            indicator='#search-loading'
        )
    })
```

##  Configuration

### Middleware Setup (settings.py)

```python
# Add HyperX Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    
    # HyperX Middleware - Add here
    'your_app.utils.hyperx_middleware.HyperXMiddleware',
    'your_app.utils.hyperx_middleware.HyperXSecurityMiddleware',  # Optional
    
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# HyperX Configuration
HYPERX_MIDDLEWARE = {
    'AUTO_VALIDATE_HTMX': True,      # Auto-validate HTMX requests
    'AUTO_PARSE_XTAB': True,         # Auto-parse X-Tab headers
    'SECURITY_LOGGING': True,        # Enhanced security logging
    'PERFORMANCE_TRACKING': True,    # Track request performance
    'STRICT_XTAB_VALIDATION': False, # Strict X-Tab format validation
}

# Enhanced Security (Optional)
HYPERX_SECURITY = {
    'RATE_LIMITING': True,           # Enable rate limiting
    'PATTERN_DETECTION': True,       # Detect suspicious patterns
    'AUTO_BLOCKING': False,          # Auto-block malicious requests
    'MAX_REQUESTS_PER_MINUTE': 60,   # Rate limit threshold
}
```

### Logging Setup (settings.py)

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'hyperx.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'core.htmx_implementation.main': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core.htmx_implementation.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core.htmx_implementation.performance': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core.htmx_implementation.middleware': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

##  Security Best Practices

 **Always validate HTMX requests** in sensitive views  
 **Use TabX validation** for complex interfaces  
 **Include CSRF tokens** in form submissions  
 **Monitor security logs** for unusual patterns  
 **Use `@htmx_login_required`** for protected views  
 **Validate expected targets** in critical endpoints  
 **Log all TabX parsing** for audit trails  

##  Performance Features

- **Smart Middleware**: Auto-processing with minimal overhead
- **Smart URL Reversal**: Automatic Django URL name resolution
- **Real-time Monitoring**: Request duration tracking in headers
- **Efficient Logging**: 8 specialized logger categories including middleware
- **Request Validation**: Lightning-fast HTMX request detection
- **Attribute Caching**: Optimized attribute generation
- **Memory Efficient**: Minimal overhead design
- **Security Optimization**: Intelligent threat detection without blocking performance

##  Contributing

HyperX is open source and contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

##  License

MIT License - see [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **HTMX Team** - For creating the amazing HTMX library
- **Django Community** - For the robust framework
- **Contributors** - Everyone who helps make HyperX better

##  Support

- **Documentation**: Full examples included in source code
- **Issues**: Report bugs via GitHub issues
- **Discussions**: Join the community discussions

---

** HyperX - HTMX's Sidekick ⚡**  
*TabX so fast! Making Django + HTMX development lightning fast and incredibly intuitive.*

---

Made with ❤️ for the Django and HTMX communities.
