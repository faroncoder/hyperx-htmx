"""
hyperx/compiler.py
────────────────────────────────────────────
HyperX Declarative Compiler and AST Builder.

Transforms {% hx %} blocks or .hx.html files into
intermediate representation trees for validation,
code generation, and introspection.
"""

from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
from .templatetags.hyperx import convert_import
from .core import *

# ─────────────────────────────────────────────
# 📦 AST Structures
# ─────────────────────────────────────────────
@dataclass
class HXNode:
    tag: str
    attrs: Dict[str, str]
    children: List["HXNode"] = field(default_factory=list)
    parent: Optional["HXNode"] = None

    def to_dict(self):
        return {
            "tag": self.tag,
            "attrs": self.attrs,
            "children": [c.to_dict() for c in self.children],
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


# ─────────────────────────────────────────────
# 🧠 Compiler
# ─────────────────────────────────────────────
class HyperXCompiler:
    def __init__(self, html: str):
        self.html = html
        self.root = None

    def parse(self):
        """Parse HTML into a hierarchical AST of HXNodes."""
        soup = BeautifulSoup(self.html, "html.parser")
        self.root = self._parse_node(soup)
        return self.root

    def _parse_node(self, element, parent=None) -> HXNode:
        node = HXNode(tag=element.name or "document", attrs=dict(element.attrs), parent=parent)

        for child in element.find_all(recursive=False):
            if child.name and child.name.startswith("hx:"):
                child_node = self._parse_node(child, parent=node)
                node.children.append(child_node)

        return node

    def compile_to_html(self, builder):
        """
        Compile the AST using a provided builder (like build_htmx_attrs)
        into standard HTMX-ready HTML.
        """
        html_fragments = []
        self._render_node(self.root, builder, html_fragments)
        return "\n".join(html_fragments)

    def _render_node(self, node, builder, fragments):
        tag_type = node.tag.split(":")[1] if ":" in node.tag else node.tag
        attrs = builder(**node.attrs) if callable(builder) else node.attrs

        # Render children recursively
        inner_html = "".join(self._render_child(c, builder) for c in node.children)
        fragments.append(f"<div {self._format_attrs(attrs)}>{inner_html}</div>")

    def _render_child(self, child, builder):
        fragments = []
        self._render_node(child, builder, fragments)
        return "".join(fragments)

    @staticmethod
    def _format_attrs(attrs: Dict[str, str]) -> str:
        return " ".join(f'{k}="{v}"' for k, v in attrs.items())


def _render_node(self, node, builder, fragments):
    tag_type = node.tag.split(":")[1] if ":" in node.tag else node.tag
    attrs = builder(**node.attrs) if callable(builder) else node.attrs

    # 🧩 Handle <hx:include>
    if tag_type == "include":
        from django.template.loader import render_to_string
        file_path = node.attrs.get("file")
        try:
            ctx_str = node.attrs.get("context", "{}")
            ctx = json.loads(ctx_str.replace("'", '"')) if ctx_str else {}
        except Exception:
            ctx = {}
        try:
            included = render_to_string(file_path, ctx)
        except Exception as e:
            included = f"<!-- include error: {e} -->"
        fragments.append(included)
        return

    if tag_type == "import":
        fragments.append(convert_import(tag_type, node.attrs))
        return


    # Otherwise render as normal
    inner_html = "".join(self._render_child(c, builder) for c in node.children)
    fragments.append(f"<div {self._format_attrs(attrs)}>{inner_html}</div>")



# ─────────────────────────────────────────────
# 🧪 Example Usage
# ─────────────────────────────────────────────
if __name__ == "__main__":
    sample = """
    {% hx %}
      <hx:panel get="lti:admin:course_table_view" target="#intel-container">
        <hx:button post="lti:teacher:sync_grades" label="Sync Grades" />
      </hx:panel>
    {% endhx %}
    """

    compiler = HyperXCompiler(sample)
    ast = compiler.parse()
    print("AST Tree:")
    print(ast)
