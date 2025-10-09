🚀 HyperX 3.1.0 — The Paradigm Shift
From “Coding for Django” → Declaring Django

HyperX 3.1.0 marks a paradigm shift — from writing Django code about behavior to declaring behavior directly inside templates.
yp
🧠 Declarative HyperX Elements

HyperX 2.1 introduced {% hx %} blocks and <hx:*> declarative syntax.
Version 3.1.0 expands this vision into a full server-side DSL that compiles HTML intent into dynamic, CSRF-aware HTMX actions.

{% load hyperx %}
{% hx %}
  <hx:button get="lti:admin:course_table_view"
             target="#intel-container"
             label="Load Courses" />
  <hx:panel get="dashboard:refresh"
            target="#main-panel"
            swap="innerHTML" />
{% endhx %}


✅ Server-authored, browser-executed, declaratively controlled.

🌟 What’s New in 3.1.0

Declarative by Default Mode — all <hx:*> tags now compile automatically through middleware, no manual imports.

Drawer & Drop Elements — <hx:drawer> and <hx:drop> bring built-in side panels + drag-and-drop upload zones.

Bootstrap Integration — {% load hyperx %} now includes Django-Bootstrap5 + static tags automatically.

Runtime Autodiscovery — Context processor injects HyperX JS helpers (loader.js, dragdrop.js, drawer.js) in DEBUG mode.

Self-installing CLI — python manage.py install_hyperx auto-patches settings.py with middleware + security config.

Improved Security Core — rate-limiting, pattern detection, and TabX validation now declarative in HYPERX_SECURITY.

Refined Compiler AST — faster parse/render for nested hyperx-elements and inline JSON payloads.

🛠️ Installation
Quick Start
pip install django-htmx hyperx-htmx
python manage.py install_hyperx
python manage.py check_hyperx

Manual Setup
INSTALLED_APPS = [
    "django_htmx",
    "hyperx",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "hyperx.middleware.HyperXMiddleware",
    "hyperx.middleware.HyperXSecurityMiddleware",
]

💡 Design Philosophy

The server is truth.
HyperX isn’t a JavaScript framework — it’s Django speaking declaratively.
The template becomes the language; middleware becomes the logic; HTML becomes the API.

HyperX collapses the distance between backend logic and frontend behavior — making templates self-describing again.

🧩 Unix Always Wins

Every part of HyperX follows the Unix philosophy:

Do one thing well.

Middleware → truth, Templatetags → meaning, HTMX → motion.

HTML becomes the single, inspectable contract between human and machine.

🔒 Security by Composition

Automatic CSRF injection

Verified TabX headers

Intelligent rate limiting + pattern detection

Explicit declarative intents for all requests

🧭 Creator’s Note

“When words fall silent, systems still speak.”

HyperX was born from the belief that the server should speak truth in its own language — HTML.
Built in the Unix spirit, for Django developers who value clarity, simplicity, and honesty in code.

Jeff Panasuik
Faroncoder — SignaVision Solutions Inc.
Toronto 🇨🇦