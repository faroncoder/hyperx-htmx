![Python](https://img.shields.io/badge/language-python-blue.svg)
![Django](https://img.shields.io/badge/framework-django-green.svg)
![htmx](https://img.shields.io/badge/library-htmx-blueviolet)
![PyPI](https://img.shields.io/pypi/v/your-package-name.svg)
→ Built on Python 3.12



What’s New in 2.1.x

Declarative HyperX Tags

→ HyperX 2.1 introduces {% hx %} blocks and <hx:*> declarative syntax, turning complex HTMX code into readable server-side logic.
```
{% load hyperx %}

{% hx %}
  <hx:button get="lti:admin:course_table_view" target="#intel-container" label="Load Courses" />
  <hx:panel get="dashboard:refresh" target="#main-panel" swap="innerHTML" />
{% endhx %}
```

→ Automatically compiles to valid HTMX markup with full CSRF support and TabX headers.

→ Features
1. TabX Protocol: Lightning-fast tab sync via X-Tab headers
2. Declarative Tags: Write <hx:button> instead of hx-get="..."
3. Smart Middleware: Auto-processes HTMX + TabX requests
4. Security Suite: Built-in rate-limit & header validation

 → Performance Metrics: Adds duration headers for every HTMX request
Response Helpers: 15+ HTMX utilities for common cases

→ Installation
1. Dependencies
`pip install django-htmx hyperx-htmx`

2. Django Settings
`INSTALLED_APPS = [
   ...
   "django_htmx",
   "hyperx",
]
`
3. Middleware Order
```
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware", #  <---- required dependency
    "hyperx.middleware.HyperXMiddleware", # <--- add this
    "hyperx.middleware.HyperXSecurityMiddleware", # <--- optional
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
```
4. Settings.py hyperx configration
```
HYPERX_MIDDLEWARE = {
    'AUTO_VALIDATE_HTMX': True,
    'AUTO_PARSE_XTAB': True,
    'SECURITY_LOGGING': True,
    'PERFORMANCE_TRACKING': True,
    'STRICT_XTAB_VALIDATION': False,
}

HYPERX_SECURITY = {
    'RATE_LIMITING': True,
    'PATTERN_DETECTION': True,
    'AUTO_BLOCKING': False,
    'MAX_REQUESTS_PER_MINUTE': 60,
}
```

5. Usage

→ Templatetag Usage
`{% load hyperx %}`

Example
```
{% load hyperx %}
{% hx %}
  <hx:button get="users:list" target="#table" label="Refresh" />
  <hx:panel get="dashboard:stats" swap="outerHTML" />
{% endhx %}
```

→ Inline Attributes
`<button {{ attrs|htmx_attrs }}>Submit</button>`

→ View Integration
```
from hyperx.core import build_htmx_attrs
from hyperx.decorators import xtab_required

def dashboard_view(request):
    if request.htmx:
        return render_htmx(request, "partials/dashboard.html", {
            "attrs": build_htmx_attrs(get="dashboard:update", target="#main")
        })
    return render(request, "dashboard.html")

⚡ TabX Protocol
# TabX header auto-generation
attrs = build_htmx_attrs(
    get='profile:load',
    target='#profile',
    xtab=('profile', 'view', 'load', '1.0')
)
```
→ TabX view validation
```
@xtab_required(expected_tab='profile')
def profile_view(request):
    return JsonResponse({'tab': request.xtab})
```

→ Declarative Template Engine (Advanced)

`<hx:button>`	Creates <button> with automatic HTMX mapping	<hx:button get="api:reload" label="Reload"/>
`<hx:panel>`	Generates <div> blocks with hx-get / hx-target	<hx:panel get="dashboard" swap="innerHTML" />
`<hx:xtab>`	Adds TabX headers automatically	<hx:xtab name="profile" function="view" />


→ Security Practices

- Always include CSRF via {% csrf_token %} or automatic injection
- Use `@htmx_login_required` for sensitive views
- Validate expected targets in critical endpoints
- Monitor `hyperx.log` for anomalies
- See `HX_Templating_Delcarations.md` and `HX_Commands_Reference.md` for more examples
to use under your sleeve.  :)

→ Performance

- Smart caching for repeated HTMX attributes
- Duration tracking in X-HyperX-Duration header
- Non-blocking async-safe middleware
- Log grouping for real-time profiling

→ License & Credits

MIT License © 2025 Jeff Panasuik
Built with love for the Django + HTMX community.
Inspired by htmx.org and honoring unix.

----------------------
→ Design Philosophy — Server is the Source of Truth
HyperX is not a JavaScript framework.
It’s a new declarative language that lives inside Django’s templating engine —
a way for the server itself to describe interactivity without handing control to the client.

“If the browser can lie, the server must speak truth.”

That’s the core belief behind HyperX.
Modern web frameworks often treat the server as a data faucet and the browser as the brain.
HyperX reverses that: the server defines what happens, where it happens, and how it reacts — in pure HTML.

→ Declarative by Design
Django templates were never meant to evolve — until now.
HyperX transforms them into a reactive DSL, powered by tags like:
`
{% hx %}
  <hx:button get="dashboard:update" target="#main" />
  <hx:panel get="stats:overview" swap="outerHTML" trigger="every 30s" />
{% endhx %}
`
The result is compiled by the server into valid HTMX attributes — no manual wiring, no brittle JS.
This approach collapses the distance between backend logic and frontend behavior,
making HTML truly self-describing again.

→ The Unix Principle - and Unix always wins.
Every part of HyperX follows the Unix philosophy:
- “Do one thing well, and speak a simple language.”
- Middleware handles truth: security, validation, and flow.
- Templatetags handle meaning: declarative intent.
- HTMX handles motion: the minimal, composable runtime.

Together, they form a pipeline where HTML, not JavaScript, becomes the API boundary.

→ Security by Composition
Every request is a conversation, not an assumption.
Auto-injects CSRF
Validates TabX headers
Guards HTMX flows via intelligent middleware
No silent trust — only verified intent.

→ Framework-Agnostic Evolution
- HyperX doesn’t replace Django.
- It is not a new invention.
- It connects and amplifies Django.
- It doesn’t compete with HTMX — it clarifies it.
- It doesn’t chase trends — it returns to fundamentals: unix principles.

Simple. Inspectable. Declarative HTML.
Backed by a strong, honest server.

→ Philosophical Credits
“Every revolution begins with a return to first principles.”
HyperX exists because the web forgot its roots.
It’s a reminder that HTML is already declarative,
and interactivity belongs to the server, not the browser.

Acknowledgements:
Aaron Gustafson — for HTMX
Guido van Rossum — for Python’s elegance
Adrian Holovaty & Jacob Kaplan-Moss — for Django
Dennis Ritchie & Ken Thompson — for UNIX

To the tinkerers — for asking “What if the server could talk in HTML again?”

“The server is truth.
The template is language.
The web is alive again.”

→ Creator’s Note — Making Silence Speak in Code
“When words fall silent, systems still speak.” — Jeff Panasuik

The coding world was first introduced to me at age 9
when I discovered a terminal with a blinking underscore cursor
emitting so much light making my dark room visible in nighttime.  
Unknowing that I was embracing shell scripting language, I learned
the laws of Unix.  

Unix mindset has become part of my life.
As a developer who communicates in sign language,
unix became my native protocol.

A creation of HyperX is that same philosophy —
clear, structured, and truthful and it gives
django and server the "ability to speak".

Motto: "If you build it in unix way, unix always wins"

Jeff Panasuik
Faroncoder
Founder, SignaVision Solutions Inc.
Creator of HyperX
Toronto, Canada 🇨🇦
