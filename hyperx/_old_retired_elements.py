"""
🎨 HyperX Elements Library
Declarative UI components built on top of the HyperX template system.

Version: 2.2.x
Author: Faron (MIT License)
https://github.com/faroncoder/hyperx-htmx
"""

from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape

# ─────────────────────────────────────────────────────────────
# 1️⃣  AI Chat Component (multi-room)
# ─────────────────────────────────────────────────────────────
@register_hx_tag("chat")
def convert_chat(tag, attrs):
    model = attrs.get("model", "gpt-4o-mini")
    title = attrs.get("title", "AI Chat Assistant")
    channel = attrs.get("channel", "default")
    room_id = escape(channel.replace(" ", "_").lower())
    send_url = attrs.get("send", "/lti/developer/tools/aichat/send/")
    room_target = f"#aichat-body-{room_id}"

    return f"""
    <div class="card shadow-lg border-0 mb-3" id="aichat-card-{room_id}">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0"><i class="fas fa-robot me-2"></i>{title}</h5>
        <small class="text-muted">Model: {model} | Channel: {channel}</small>
      </div>

      <div class="card-body" id="aichat-body-{room_id}" style="height: 300px; overflow-y: auto;">
        <div class="text-muted text-center mt-5">
          Enter your message to start chat in <b>{channel}</b>.
        </div>
      </div>

      <div class="card-footer bg-light">
        <form
          hx-post="{send_url}"
          hx-vals='{{"channel": "{channel}"}}'
          hx-target="{room_target}"
          hx-swap="beforeend"
          hx-indicator=".chat-loader-{room_id}"
        >
          <div class="input-group">
            <input type="text" name="prompt" class="form-control"
                   placeholder="Message {channel}..." required />
            <button type="submit" class="btn btn-primary">Send</button>
          </div>
        </form>
        <div class="chat-loader-{room_id} text-center mt-2" style="display:none;">
          <i class="fas fa-spinner fa-spin"></i> Thinking...
        </div>
      </div>
    </div>

    <script>
      document.body.addEventListener("aichat:new", function(e) {{
        const data = e.detail;
        const room = data.channel || "default";
        if (room !== "{channel}") return;
        const body = document.querySelector("{room_target}");
        if (!body) return;
        const msg = document.createElement("div");
        msg.className = "chat-bubble bg-primary text-white p-2 rounded my-1";
        msg.textContent = data.content;
        body.appendChild(msg);
        body.scrollTop = body.scrollHeight;
      }});
    </script>
    """

# ─────────────────────────────────────────────────────────────
# 2️⃣  Form Component (declarative)
# ─────────────────────────────────────────────────────────────
@register_hx_tag("form")
def convert_form(tag, attrs):
    """
    Simplified form builder:
    <hx:form post="user:save" target="#main" indicator="#loader" confirm="Save user?" />
    """
    action = attrs.get("post") or attrs.get("get", "")
    method = "post" if "post" in attrs else "get"
    target = attrs.get("target", "#main")
    indicator = attrs.get("indicator", "")
    confirm = attrs.get("confirm", "")
    swap = attrs.get("swap", "innerHTML")

    confirm_attr = f'hx-confirm="{escape(confirm)}"' if confirm else ""
    indicator_attr = f'hx-indicator="{indicator}"' if indicator else ""

    return f"""
    <form hx-{method}="{action}" hx-target="{target}" hx-swap="{swap}" {confirm_attr} {indicator_attr}>
      {tag.decode_contents()}
    </form>
    """

# ─────────────────────────────────────────────────────────────
# 3️⃣  Toast Notification Component
# ─────────────────────────────────────────────────────────────
@register_hx_tag("toast")
def convert_toast(tag, attrs):
    """
    Simple declarative notification:
    <hx:toast message="User saved!" level="success" duration="4000" />
    """
    message = attrs.get("message", "Operation successful!")
    level = attrs.get("level", "info")
    duration = int(attrs.get("duration", 4000))
    safe_msg = escape(message)

    return f"""
    <div class="toast align-items-center text-bg-{level} border-0 show fade" role="alert" id="toast-{level}">
      <div class="d-flex">
        <div class="toast-body">{safe_msg}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto"
                data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
    <script>
      setTimeout(() => {{
        const toast = document.getElementById("toast-{level}");
        if (toast) toast.remove();
      }}, {duration});
    </script>
    """

# ─────────────────────────────────────────────────────────────
# 4️⃣  Import Assets (CSS/JS)
# ─────────────────────────────────────────────────────────────
@register_hx_tag("import")
def convert_import(tag, attrs):
    """
    Import CSS/JS dynamically via HyperX:
    <hx:import css="css/admin.css" js="js/dashboard.js" />
    """
    css = attrs.get("css", "")
    js = attrs.get("js", "")
    html = ""

    if css:
        html += f'<link rel="stylesheet" href="/static/{css}">\n'
    if js:
        html += f'<script src="/static/{js}"></script>\n'

    return html 

@register_hx_tag("plaintable")
def convert_plaintable(tag, attrs):
    """
    Render a plain Bootstrap-style table with no CRUD logic.
    Example:
      <hx:plaintable fields="id,username,email" data-target="#users-table" />
    """
    fields = [f.strip() for f in attrs.get("fields", "").split(",") if f.strip()]
    table_class = attrs.get("class", "table table-striped table-hover align-middle")
    caption = attrs.get("caption", "")

    # Build header
    header_html = "".join(f"<th>{f.title()}</th>" for f in fields)

    html = f"""
    <table class="{table_class}">
        {"<caption>" + caption + "</caption>" if caption else ""}
        <thead><tr>{header_html}</tr></thead>
        <tbody>
            <tr><td colspan="{len(fields)}" class="text-center text-muted py-3">
                <i class="fas fa-info-circle me-2"></i>No data available.
            </td></tr>
        </tbody>
    </table>
    """
    return html


@register_hx_tag("form")
def convert_form(tag, attrs):
    """
    Declarative form component.
    Example:
    <hx:form post="users:create" target="#main" toast="User created!" />
    """
    post = attrs.get("post")
    target = attrs.get("target", "#main")
    confirm = attrs.get("confirm", "")
    toast = attrs.get("toast", "")
    indicator = attrs.get("indicator", "")
    swap = attrs.get("swap", "innerHTML")

    confirm_attr = f'hx-confirm="{escape(confirm)}"' if confirm else ""
    indicator_attr = f'hx-indicator="{indicator}"' if indicator else ""

    toast_script = ""
    if toast:
        toast_script = f"""
        <script>
        document.body.addEventListener("htmx:afterOnLoad", function(e) {{
            const toast = document.createElement("div");
            toast.className = "toast align-items-center text-bg-success border-0 show fade";
            toast.innerHTML = `<div class='toast-body'>{escape(toast)}</div>`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }});
        </script>
        """

    # Render the form’s inner content (fields, buttons, etc.)
    inner_html = tag.decode_contents() or "<!-- form fields go here -->"

    return f"""
    <form hx-post="{post}" hx-target="{target}" hx-swap="{swap}" {confirm_attr} {indicator_attr}>
      <input type="hidden" name="csrfmiddlewaretoken" value="{{{{ csrf_token }}}}">
      {inner_html}
    </form>
    {toast_script}
    """

@register_hx_tag("field")
def convert_field(tag, attrs):
    """
    Generic field generator.

    <hx:field label="Email" name="email" type="email" required="true" help="We'll never share it." />
    """
    label = attrs.get("label", "")
    name = attrs.get("name", "")
    ftype = attrs.get("type", "text")
    required = "required" if attrs.get("required") in ("true", "1", True) else ""
    helptext = attrs.get("help", "")
    placeholder = attrs.get("placeholder", label)

    return f"""
    <div class="mb-3">
      <label for="id_{name}" class="form-label">{label}</label>
      <input type="{ftype}" name="{name}" id="id_{name}"
             class="form-control" placeholder="{placeholder}" {required}>
      {f'<div class="form-text">{helptext}</div>' if helptext else ''}
    </div>
    """


@register_hx_tag("select")
def convert_select(tag, attrs):
    """
    Declarative dropdown.

    <hx:select label="Role" name="role" options="Student,Teacher,Admin" />
    """
    label = attrs.get("label", "")
    name = attrs.get("name", "")
    options = attrs.get("options", "")
    choices = [o.strip() for o in options.split(",") if o.strip()]

    opts_html = "".join(f'<option value="{escape(o)}">{escape(o)}</option>' for o in choices)

    return f"""
    <div class="mb-3">
      <label for="id_{name}" class="form-label">{label}</label>
      <select name="{name}" id="id_{name}" class="form-select">
        {opts_html}
      </select>
    </div>
    """


@register_hx_tag("input")
def convert_input(tag, attrs):
    """
    Quick standalone input.

    <hx:input name="username" placeholder="Enter username" />
    """
    name = attrs.get("name", "")
    placeholder = attrs.get("placeholder", "")
    value = attrs.get("value", "")
    itype = attrs.get("type", "text")

    return f'<input type="{itype}" name="{name}" value="{value}" class="form-control" placeholder="{placeholder}">'


@register_hx_tag("pagination")
def convert_pagination(tag, attrs):
    """
    Declarative pagination builder.
    Example:
      <hx:pagination source="users:list" current="3" total="12" target="#table" />
    """
    from django.urls import reverse
    current = int(attrs.get("current", 1))
    total = int(attrs.get("total", 1))
    source = attrs.get("source")
    target = attrs.get("target", "#content")
    swap = attrs.get("swap", "innerHTML")
    size = attrs.get("size", "").lower()

    size_class = f"pagination-{size}" if size in ("sm", "small", "lg", "large") else ""

    prev_page = current - 1 if current > 1 else None
    next_page = current + 1 if current < total else None

    def page_link(page, label, disabled=False, active=False):
        if disabled:
            return f'<li class="page-item disabled"><span class="page-link">{label}</span></li>'
        if active:
            return f'<li class="page-item active"><a class="page-link" href="#">{label}</a></li>'
        return (
            f'<li class="page-item">'
            f'<a class="page-link" hx-get="/{source}?page={page}" '
            f'hx-target="{target}" hx-swap="{swap}">{label}</a>'
            f'</li>'
        )

    html = '<nav aria-label="Pagination"><ul class="pagination justify-content-center {0}">'.format(size_class)

    # previous
    html += page_link(prev_page, "&laquo; Prev", disabled=prev_page is None)

    # center pages (up to 5 window)
    window = range(max(1, current - 2), min(total + 1, current + 3))
    for p in window:
        html += page_link(p, p, active=(p == current))

    # next
    html += page_link(next_page, "Next &raquo;", disabled=next_page is None)
    html += "</ul></nav>"

    return html


@register_hx_tag("crud")
def convert_crud(tag, attrs):
    """
    Declarative CRUD container that auto-wires form + table + pagination.
    Example:
      <hx:crud model="User" endpoint="users" target="#crud-zone">
        <hx:form ... />
        <hx:table ... />
      </hx:crud>
    """
    model_name = attrs.get("model")
    endpoint = attrs.get("endpoint")
    target = attrs.get("target", "#content")

    inner_html = tag.decode_contents()
    base = f"""
    <div id="{target.strip('#')}" class="hx-crud"
         data-model="{model_name}" data-endpoint="{endpoint}">
      {inner_html}
    </div>
    """
    return base


@register_hx_tag("tablecrud")
def convert_tablecrudized(tag, attrs):
    """
    Smart table with CRUD bindings, pagination, and actions (including export).
    Example:
      <hx:tablecrud source="users" fields="username,email,role"
                    actions="edit,delete,export" per-page="10" />
    """
    source = attrs.get("source")
    fields = [f.strip() for f in attrs.get("fields", "").split(",") if f.strip()]
    actions = [a.strip() for a in attrs.get("actions", "").split(",") if a.strip()]
    per_page = int(attrs.get("per-page", 10))
    paginate = attrs.get("paginate", "true").lower() == "true"
    target = attrs.get("target", "#crud-zone")
    swap = attrs.get("swap", "innerHTML")

    # --- Table header ---
    header_html = "".join(f"<th>{f.title()}</th>" for f in fields)
    if actions:
        header_html += "<th class='text-center'>Actions</th>"

    # --- Action Button Factory ---
    def action_buttons(row_id_var="{{id}}"):
        buttons = []
        for act in actions:
            act = act.lower().strip()

            if act == "edit":
                buttons.append(f'''
                  <button class="btn btn-sm btn-outline-primary"
                          hx-get="/{source}/edit/{row_id_var}/"
                          hx-target="{target}"
                          hx-swap="{swap}">
                    <i class="fas fa-pen"></i>
                  </button>''')

            elif act == "delete":
                buttons.append(f'''
                  <button class="btn btn-sm btn-outline-danger"
                          hx-delete="/{source}/delete/{row_id_var}/"
                          hx-target="{target}"
                          hx-swap="{swap}"
                          hx-confirm="Are you sure you want to delete this record?">
                    <i class="fas fa-trash"></i>
                  </button>''')

            elif act == "view":
                buttons.append(f'''
                  <button class="btn btn-sm btn-outline-secondary"
                          hx-get="/{source}/view/{row_id_var}/"
                          hx-target="{target}"
                          hx-swap="{swap}">
                    <i class="fas fa-eye"></i>
                  </button>''')

            elif act == "export":
                buttons.append(f'''
                  <button class="btn btn-sm btn-outline-success"
                          hx-get="/{source}/export/"
                          hx-boost="true"
                          title="Export your data as CSV">
                    <i class="fas fa-file-csv"></i>
                  </button>''')

        return "\n".join(buttons)

    # --- Table body ---
    actions_html = action_buttons()
    tbody_attrs = f'hx-get="/{source}/list/?page=1" hx-trigger="load" hx-target="{target}" hx-swap="{swap}"'
    body_html = f"""
    <tbody {tbody_attrs}>
      <tr>
        {''.join(f'<td>{{{{ {f} }}}}</td>' for f in fields)}
        {'<td class="text-center">' + actions_html + '</td>' if actions else ''}
      </tr>
    </tbody>
    """

    # --- Table structure ---
    html = f"""
    <div id="{target.strip('#')}" class="hx-crud-table">
        <table class="table table-striped table-hover align-middle">
            <thead><tr>{header_html}</tr></thead>
            {body_html}
        </table>
    """

    # --- Pagination ---
    if paginate:
        html += f"""
        <hx:pagination source="{source}/list" target="{target}" per-page="{per_page}" />
        """

    html += "</div>"
    return html