from hyperx.bin.cli.logger.hx_logger import *
_logger = load_logger("jsx_extractor")
_logger.info("jsx_extractor initialized")
import os, sys, re, json, hmac, hashlib

from pathlib import Path
from playwright.sync_api import sync_playwright
from hyperx.bin.cli.kernel.hx_recorder import Recorder
from bs4 import BeautifulSoup
import json


try:
    from hyperx.bin.cli.kernel.hx_recorder import Recorder
except Exception:
    Recorder = None

recorder = Recorder() if callable(Recorder) else None


def extract_assets(
    file_path: Path,
    output_dir="/tmp/hyperx_assets",
    css_name="reactjs.css",
    js_name="reactjs.js",
):
    """
    Build CSS and JS bundles from parsed HTML.
    Adds:
      <hx:import css="reactjs.css" />
      <hx:import js="reactjs.js" />
    to the top of the template.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    html = Path(file_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # ─────────────────────────────────────────────
    #  1️⃣  Collect styles
    # ─────────────────────────────────────────────
    class_styles, inline_rules = {}, {}
    for el in soup.find_all(True):
        if el.has_attr("style"):
            rule = el["style"].strip()
            sel = el.get("class", [el.name])
            key = "." + sel[0] if sel else el.name
            inline_rules[key] = rule
            del el["style"]

        if el.has_attr("class"):
            for cls in el["class"]:
                class_styles.setdefault(cls, [])
                class_styles[cls].append(el.name)

    css_lines = []
    for cls, tags in class_styles.items():
        css_lines.append(f".{cls} {{ /* used by: {', '.join(set(tags))} */ }}")
    for sel, rule in inline_rules.items():
        css_lines.append(f"{sel} {{{rule}}}")
    css_path = output_dir / css_name
    css_path.write_text("\n".join(css_lines), encoding="utf-8")

    # ─────────────────────────────────────────────
    #  2️⃣  Collect JavaScript
    # ─────────────────────────────────────────────
    js_blocks = []
    for script in soup.find_all("script"):
        if script.string:
            js_blocks.append(script.string.strip())
        elif script.has_attr("src"):
            js_blocks.append(f"// external: {script['src']}")
        script.decompose()  # remove from DOM after capture

    if js_blocks:
        js_text = "\n\n".join(js_blocks)
        js_path = output_dir / js_name
        js_path.write_text(js_text, encoding="utf-8")
    else:
        js_path = None

    # ─────────────────────────────────────────────
    #  3️⃣  Inject <hx:import> tags
    # ─────────────────────────────────────────────
    if not soup.find("hx:import", attrs={"css": css_name}):
        css_tag = soup.new_tag("hx:import")
        css_tag["css"] = css_name
        soup.insert(0, css_tag)

    if js_path and not soup.find("hx:import", attrs={"js": js_name}):
        js_tag = soup.new_tag("hx:import")
        js_tag["js"] = js_name
        soup.insert(1, js_tag)

    # ─────────────────────────────────────────────
    #  4️⃣  Save results
    # ─────────────────────────────────────────────
    updated_html = output_dir / Path(file_path).name
    updated_html.write_text(str(soup), encoding="utf-8")

    summary = {
        "classes": class_styles,
        "inline_rules": inline_rules,
        "script_blocks": len(js_blocks),
    }
    (output_dir / (Path(file_path).stem + "_summary.json")).write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    recorder.log_event(
        "asset_extract_complete",
        css=str(css_path),
        js=str(js_path) if js_path else None,
        file=str(updated_html),
    )
    return css_path, js_path, updated_html



    return summary_path

def run_jsc(args=None):
    """
    CLI entrypoint: extract JS + CSS assets and inject <hx:import> tags.
    Usage:
        hyperx jsc --file /tmp/hyperx_converted/index.html
    """
    from pathlib import Path
    file_path = Path(getattr(args, "file", "/tmp/hyperx_converted/index.html"))
    out_dir = getattr(args, "out", "/tmp/hyperx_assets")

    css, js, updated = extract_assets(file_path, output_dir=out_dir)
    print(f"✅ Assets extracted:\n  CSS: {css}\n  JS: {js}\n  Updated: {updated}")
