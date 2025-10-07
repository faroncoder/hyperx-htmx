🧩 Template Tags Reference (Declarative Syntax)

HyperX 2.1 introduces a declarative Django template syntax for building HTMX components directly in templates.

Wrap your <hx:*> elements in a {% hx %}...{% endhx %} block — HyperX will automatically compile them into valid HTMX markup during rendering.

{% load hyperx %}

{% hx %}
  <hx:button get="dashboard:update" target="#main-panel" label="Refresh Data" />
  <hx:panel get="dashboard:stats" swap="outerHTML" target="#stats" />
  <hx:xtab name="dashboard" function="refresh" command="update" version="1.0" />
{% endhx %}

🔘 <hx:button>

A declarative shortcut for building HTMX buttons.

Attribute	Description	Example
get / post	HTMX action URL name	get="api:refresh"
target	Target selector	target="#content"
label	Text on the button	label="Reload"
swap	Swap strategy	swap="outerHTML"
trigger	Trigger behavior	trigger="click"

Compiles to:

<button hx-get="/api/refresh" hx-target="#content" hx-swap="outerHTML">
  Reload
</button>

🪟 <hx:panel>

Creates a reactive <div> block with HTMX attributes.

Attribute	Description	Example
get / post	HTMX endpoint	get="users:list"
target	Nested swap target	target="#table"
swap	Swap behavior	swap="innerHTML"
trigger	Auto-refresh trigger	trigger="every 10s"

Compiles to:

<div hx-get="/users/list" hx-swap="innerHTML" hx-trigger="every 10s" hx-target="#table"></div>

🧭 <hx:xtab>

Builds an HTMX container with TabX headers automatically applied.

Attribute	Description	Example
name	Tab name (namespace)	name="profile"
function	Logical function	function="load"
command	Command identifier	command="refresh"
version	Optional version ID	version="1.0"

Compiles to:

<div hx-headers='{"X-Tab":"profile:1.0:load:refresh"}'></div>

🧠 <hx:*> Universal Attributes

All declarative elements share the same common attributes:

Common Attribute	Description
confirm="..."	Adds an inline hx-confirm dialog
indicator="#id"	HTMX request indicator element
on_before_request="fn()"	JS event hook
on_after_request="fn()"	JS event hook
on_response_error="fn(event)"	Error handling
csrf="auto"	Automatically inject CSRF token
✨ Full Example
{% load hyperx %}

{% hx %}
  <hx:button
      post="forms:submit"
      target="#form-container"
      label="Submit Form"
      confirm="Are you sure?"
      indicator="#form-loader"
  />

  <hx:panel
      get="dashboard:refresh"
      swap="innerHTML"
      target="#main"
      trigger="every 30s"
  />

  <hx:xtab
      name="profile"
      function="load"
      command="info"
      version="2.0"
  />
{% endhx %}


Compiles to:

<button hx-post="/forms/submit" hx-target="#form-container" hx-confirm="Are you sure?" hx-indicator="#form-loader">
  Submit Form
</button>

<div hx-get="/dashboard/refresh" hx-swap="innerHTML" hx-target="#main" hx-trigger="every 30s"></div>

<div hx-headers='{"X-Tab":"profile:2.0:load:info"}'></div>

🧩 Adding Your Own Custom <hx:*> Tags

You can register your own declarative tag converters inside hyperx/templatetags/hyperx.py:

from hyperx.templatetags.hyperx import register_hx_tag

@register_hx_tag("toast")
def convert_toast(tag, attrs):
    message = attrs.get("message", "Success!")
    level = attrs.get("level", "info")
    return f'<div class="toast toast-{level}">{message}</div>'


Usage:

{% hx %}
  <hx:toast message="Data saved successfully!" level="success" />
{% endhx %}


Compiles to:

<div class="toast toast-success">Data saved successfully!</div>

🧮 Advanced Examples
🔍 Example Output (with debug=True)
[HyperX Compiler] Parsed nodes:
{
  "tag": "document",
  "attrs": {},
  "children": [
    {"tag": "hx:panel", "attrs": {"get": "lti:admin:course_table_view"}, "children": [
      {"tag": "hx:button", "attrs": {"post": "lti:teacher:sync_grades"}}
    ]}
  ]
}

[HyperX Rendered HTML]
<div hx-get="lti:admin:course_table_view">
  <button hx-post="lti:teacher:sync_grades">Action</button>
</div>

🧱 Including Other Templates
{% hx %}
  <hx:panel>
      <hx:include file="lti/student_panel.html" context="{'user': user}" />
  </hx:panel>
{% endhx %}


Compiles to:

<div>
  <div class="student-panel"> ... </div>
</div>


Or with attributes:

{% hx %}
  <hx:panel get="lti:admin:course_table_view" target="#intel-container">
      <hx:include file="lti/student_panel.html" context="{'title': 'My Panel'}" />
  </hx:panel>
{% endhx %}


Compiles to:

<div hx-get="lti:admin:course_table_view" hx-target="#intel-container">
  <div class="student-panel">
    <h3>My Panel</h3>
  </div>
</div>

🎨 Importing CSS/JS for Elements
{% hx %}
  <hx:import css="css/admin.css" js="js/dashboard.js" />
  <hx:panel get="lti:admin:course_table_view" target="#intel-container" />
{% endhx %}

🧾 Meta and CSRF Integration
{% hx %}
  <hx:meta title="Admin Dashboard" description="Control panel for instructors" />
  <hx:meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <hx:meta type="json" id="config" data='{"theme":"dark"}' />
{% endhx %}


Compiles to:

<title>Admin Dashboard</title>
<meta name="description" content="Control panel for instructors">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script id="config" type="application/json">
{"theme":"dark"}
</script>

🔐 CSRF Auto-Injection
{% hx %}
  <hx:meta title="Dashboard" />
  <hx:meta csrf="auto" />
{% endhx %}


Compiles to:

<title>Dashboard</title>
<meta name="csrf-token" content="vT1x8d3OABK...">
<script>
  document.body.dataset.csrf = "vT1x8d3OABK...";
  htmx.config.headers['X-CSRFToken'] = "vT1x8d3OABK...";
</script>

