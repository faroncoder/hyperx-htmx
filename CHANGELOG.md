[3.1.0] – 2025-10-09
🚀 The Paradigm Shift — From Coding to Declaring

HyperX 3.1.0 transforms Django development into a declarative experience.
Templates are now a first-class language where HTML defines behavior, security, and flow — directly compiled by the server.

✨ Added

Declarative Runtime Expansion

New <hx:drawer> element for slide-in panels.

New <hx:drop> element for drag-and-drop upload zones.

<hxjs:*> syntax for declarative JavaScript event logic.

Automatic Runtime Injection

Context processor hyperx.context_processors.hyperx_runtime auto-injects loader.js, dragdrop.js, and drawer.js when DEBUG=True.

Optional middleware HyperXRuntimeInjector for HTML-safe injection on all views.

Bootstrap5 & Static Integration

{% load hyperx %} now merges both bootstrap5 and Django’s static tags automatically.

CLI Installer

python manage.py install_hyperx auto-patches settings.py with apps, middleware, and security configuration.

Security Configuration

New HYPERX_MIDDLEWARE and HYPERX_SECURITY dictionaries for declarative runtime control.

Installer Disclosure

Adds an audit section in settings.py describing what was changed.

Philosophy Docs

New docs/Philosophy.md and docs/HyperX_Principles.md — “If the browser can lie, the server must speak truth.”

🧩 Changed

{% hx %} compiler rewritten for nested tags, inline JSON, and scoped variables.

Middleware refactored with AST-driven parsing.

HyperXConfig now executes autodiscover() at startup.

Packaging modernized via setuptools entry_points.

Installer improved for proper indentation and backup handling.

🧰 Fixed

E999 f-string escape issue in installer resolved.

Full PEP8 / Flake8 compliance.

Bootstrap tag namespace collision resolved.

Circular imports between compiler and middleware eliminated.

🔒 Security

Built-in rate limiting (MAX_REQUESTS_PER_MINUTE = 60).

Suspicious pattern detection.

Automatic CSRF token handling in compiled HTMX forms.

TabX header validation and logging.

⚙️ Performance

Compiler throughput ↑ 30%.

Middleware latency ↓ 12%.

Adds X-HyperX-Duration header for runtime profiling.

💡 Developer Experience

{% load hyperx %} auto-loads Bootstrap & Static.

Autodiscovery logging on startup.

Runtime helpers injected automatically in development.

🧠 Philosophy

“Server is truth. Template is language.”
HyperX 3.1 is the moment Django begins to speak declaratively.

[3.0.0] – 2025-06-01
“Language Born” — The Compiler Era

Introduced the first generation of {% hx %} and <hx:*> compiler.

Added TabX protocol, decorators, and middleware for X-Tab routing.

Implemented HyperXCompiler and build_htmx_attrs() utilities.

Released under MIT License as a stable base for future declarative expansion.

[2.x] – 2025 Early Access
“The TabX Era”

Introduced TabX headers for multi-tab awareness.

Added HyperXSecurityMiddleware prototype.

Implemented structured request logging and response metrics.

Served as bridge between middleware-only model and declarative 3.x syntax.

[1.0.0] – 2024-11-20
🏁 The Origin Release — HyperX is Born

The first public foundation of HyperX HTMX.
A proof-of-concept showing Django could natively understand HTMX without client-side JS frameworks.

🧩 Added

HyperXMiddleware — parses HX-* headers and exposes request.htmx.

Decorators:

@htmx_only

@htmx_login_required

@htmx_view

build_htmx_attrs() helper for generating HTMX attributes in views.

Automatic CSRF token injection for all HTMX requests.

Early experimental TabX protocol for multi-tab persistence.

Basic request telemetry and X-HyperX-Duration performance header.

🧠 Philosophy (then)

“If HTMX could listen, Django should speak.”

HyperX 1.0.0 proved Django could serve as both controller and orchestrator for HTMX interactions —
a server-rendered SPA without any front-end frameworks.

⚙️ Setup Example
INSTALLED_APPS = [
    "django_htmx",
    "hyperx",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "hyperx.middleware.HyperXMiddleware",
]

🧭 Version Timeline
Version	Codename	Date	Theme
3.1.0	Paradigm Shift	2025-10	Declarative HTML language
3.0.0	Language Born	2025-06	Compiler and middleware synthesis
2.x	TabX Era	2025 Q1	Header protocols and middleware focus
1.0.0	Origin Release	2024-11	HTMX integration and CSRF harmony
📜 License

MIT License © 2025 Jeff Panasuik

Faroncoder — SignaVision Solutions Inc.
Toronto, Canada 🇨🇦

Would you like me to now generate a RELEASE.md (the short-form version used by GitHub’s “Create Release” page) — about 2,000 characters with just key highlights and emojis for copy-paste? It pairs nicely with this full CHANGELOG.md.