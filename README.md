🚀 What’s New in 2.1.x
Declarative HyperX Tags

HyperX 2.1 introduces {% hx %} blocks and <hx:*> declarative syntax, turning complex HTMX code into readable server-side logic.

{% load hyperx %}

{% hx %}
  <hx:button get="lti:admin:course_table_view" target="#intel-container" label="Load Courses" />
  <hx:panel get="dashboard:refresh" target="#main-panel" swap="innerHTML" />
{% endhx %}


→ Automatically compiles to valid HTMX markup with full CSRF support and TabX headers.

💡 Features

⚡ TabX Protocol: Lightning-fast tab sync via X-Tab headers

🧠 Declarative Tags: Write <hx:button> instead of hx-get="..."

🔐 Smart Middleware: Auto-processes HTMX + TabX requests

🧩 Security Suite: Built-in rate-limit & header validation

🧭 Performance Metrics: Adds duration headers for every HTMX request

🛠️ Response Helpers: 15+ HTMX utilities for common cases

⚙️ Installation
1. Dependencies
pip install django-htmx hyperx-htmx

2. Django Settings
INSTALLED_APPS = [
    "django_htmx",
    "hyperx",
]

3. Middleware Order

(Always after django_htmx.middleware.HtmxMiddleware)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "hyperx.middleware.HyperXMiddleware",          # ✅ add this
    "hyperx.middleware.HyperXSecurityMiddleware",  # optional
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

🧠 Template Usage
Direct Tags
{% load hyperx %}
{% hx %}
  <hx:button get="users:list" target="#table" label="Refresh" />
  <hx:panel get="dashboard:stats" swap="outerHTML" />
{% endhx %}

Inline Attributes
<button {{ attrs|htmx_attrs }}>Submit</button>

🧩 Middleware Configuration
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

🧰 View Integration
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

# TabX view validation
@xtab_required(expected_tab='profile')
def profile_view(request):
    return JsonResponse({'tab': request.xtab})

🧱 Declarative Template Engine (Advanced)
Element	Description	Example
<hx:button>	Creates <button> with automatic HTMX mapping	<hx:button get="api:reload" label="Reload"/>
<hx:panel>	Generates <div> blocks with hx-get / hx-target	<hx:panel get="dashboard" swap="innerHTML" />
<hx:xtab>	Adds TabX headers automatically	<hx:xtab name="profile" function="view" />
🔒 Security Practices

Always include CSRF via {% csrf_token %} or automatic injection

Use @htmx_login_required for sensitive views

Validate expected targets in critical endpoints

Monitor hyperx.log for anomalies

📈 Performance

Smart caching for repeated HTMX attributes

Duration tracking in X-HyperX-Duration header

Non-blocking async-safe middleware

Log grouping for real-time profiling

🧡 License & Credits

MIT License © 2025 Jeff Panasuik
Built with love for the Django + HTMX community.
Inspired by htmx.org
 and the UNIX way.

----------------------
Design Philosophy — Server is the Source of Truth

HyperX is not a JavaScript framework.
It’s a new declarative language that lives inside Django’s templating engine —
a way for the server itself to describe interactivity without handing control to the client.

“If the browser can lie, the server must speak truth.”

That’s the core belief behind HyperX.

Modern web frameworks often treat the server as a data faucet and the browser as the brain.
HyperX reverses that: the server defines what happens, where it happens, and how it reacts — in pure HTML.

Declarative by Design

Django templates were never meant to evolve — until now.
HyperX transforms them into a reactive DSL, powered by tags like:

{% hx %}
  <hx:button get="dashboard:update" target="#main" />
  <hx:panel get="stats:overview" swap="outerHTML" trigger="every 30s" />
{% endhx %}


The result is compiled by the server into valid HTMX attributes — no manual wiring, no brittle JS.
This approach collapses the distance between backend logic and frontend behavior,
making HTML truly self-describing again.

---The Unix Principle, Applied to the Web

Every part of HyperX follows the Unix philosophy:

“Do one thing well, and speak a simple language.”

Middleware handles truth: security, validation, and flow.

Templatetags handle meaning: declarative intent.

HTMX handles motion: the minimal, composable runtime.

Together, they form a pipeline where HTML, not JavaScript, becomes the API boundary.

---Security by Composition

HyperX treats requests as conversations between trusted peers.
Every interaction is validated, introspected, and logged — not assumed safe.
That’s why it auto-injects CSRF meta tags, validates TabX headers,
and guards HTMX requests with intelligent middleware.

---Framework-Agnostic Evolution

HyperX doesn’t compete with Django — it amplifies it.
It doesn’t replace HTMX — it clarifies it.
And it doesn’t chase trends — it returns web to fundamentals:
simple, inspectable, declarative HTML, backed by a strong, honest server.

---Philosophical Credits — Standing on the Shoulders of Simplicity

“Every revolution begins with a return to first principles.”

HyperX exists because the web forgot its roots.
It’s a reminder that HTML is already declarative,
and that interactivity belongs to the server, not the browser.

This work stands on the quiet brilliance of others:

Aaron Gustafson — for proving that hypermedia can still evolve,
and for creating HTMX, the most humane frontend library of this decade.

Guido van Rossum — for giving us Python, where elegance is not optional.

Adrian Holovaty & Jacob Kaplan-Moss — for Django, the web framework that refused to compromise.

Dennis Ritchie & Ken Thompson — for Unix, the one philosophy every good system still bows to.

And finally — to the curious, the tinkerers, the ones who open the terminal and ask “What if the server could talk in HTML again?” —
HyperX was made for you.

---“The server is truth. The template is language. The web is alive again.”

🧑‍💻 Creator’s Note — Making Silence Speak in Code

I wrote my first shell script at age 9, on a machine that barely ran.  No frameworks. No noise. Just logic and blinking underscore light.

As a Deaf developer, silence became my native protocol — and over the years, I learned that code, like language, doesn’t need sound to communicate truth.
It needs clarity, structure, and integrity.  Unix is the perfect laws and it gave that to systems, and even to me.

HyperX is my way of honoring that.
It’s the moment where Django, HTMX, and the Unix philosophy finally shake hands — a framework that listens, even when it doesn’t hear.

---Django Team: I hope this elevates Django to next level.  :)

“When words fall silent, systems still speak.”

– Jeff Panasuik
Founder of SignaVision Solutions Inc.
Creator of HyperX
Toronto, Canada 🇨🇦
