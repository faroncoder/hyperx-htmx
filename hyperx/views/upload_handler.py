"""
upload_handler.py
────────────────────────────────────────────
Handles HTMX-powered dataset uploads for HyperX.
"""

import os
import subprocess
import logging
from pathlib import Path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from hyperx.core.core import *
from hyperx.templatetags.hyperx import register_hx_tag
from django.utils.html import escape



ROOT_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT_DIR / 'media/uploads'
AI_AUTOGEN_SCRIPT = ROOT_DIR / 'opt/hyperx/ai_schema_autogen.py'
WATCHER_LOG = ROOT_DIR / 'var/log/hyperx_dataset.log'

log = logging.getLogger("hyperx.upload")

@csrf_exempt
def upload_handler(request):
    """Receive CSV/JSON uploads via <hx:upload>"""
    if request.method != "POST" or "file" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)

    file_obj = request.FILES["file"]
    ext = Path(file_obj.name).suffix.lower()

    if ext not in (".csv", ".json"):
        return JsonResponse({"error": "Unsupported file type"}, status=400)

    # 1️⃣ Save the file to /opt/hyperx/uploads
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file_obj.name
    with open(file_path, "wb+") as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    # 2️⃣ Trigger AI schema autogen
    ai_result = ""
    try:
        result = subprocess.run(
            ["python3", str(AI_AUTOGEN_SCRIPT), str(file_path)],
            capture_output=True, text=True, timeout=60
        )
        ai_result = result.stdout.strip()
        log.info(f"[AI Schema Autogen] {file_obj.name}: {ai_result[:100]}...")
    except Exception as e:
        ai_result = f"AI schema autogen failed: {e}"
        log.error(ai_result)

    # 3️⃣ Log to dataset watcher file
    with open(WATCHER_LOG, "a") as wf:
        wf.write(f"{timezone.now()} :: Uploaded {file_obj.name} ({ext})\n")

    # 4️⃣ Respond back to HTMX frontend
    badge = '<span class="badge bg-success">Schema generated</span>' if "model" in ai_result.lower() else '<span class="badge bg-warning">Uploaded</span>'
    return JsonResponse({
        "status": "ok",
        "file": file_obj.name,
        "message": f"{file_obj.name} processed successfully.",
        "ai_result": ai_result,
        "hx_trigger": {"dataset:uploaded": {"filename": file_obj.name}},
        "html": f"<div class='alert alert-success'><b>{file_obj.name}</b> uploaded! {badge}</div>"
    })
