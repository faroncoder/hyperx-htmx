"""
    <hx:tablecrud>
    ─────────────────────────────────────────────
    Smart table with CRUD bindings, pagination, and actions.

    🧠 ATTRIBUTES
    • source="users"
    • fields="username,email,role"
    • actions="edit,delete,export"
    • per-page="10"
    • paginate="true"

    🧩 EXAMPLE
    <hx:tablecrud source="users" fields="username,email,role" actions="edit,delete" />
    """
from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json

_logger = load_logger("hx-tablecrud")
_logger.info("hx-tablecrud initialized")

@register_hx_tag("tablecrud")
def convert_tablecrudized(tag, attrs):

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