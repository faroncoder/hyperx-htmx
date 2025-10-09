#!/usr/bin/env python3
"""
AI Schema Autogen — Auto-build Django models on dataset creation
----------------------------------------------------------------
Triggered by inotify/systemd whenever a new CSV or JSON file appears in /datasets.
"""

import os, csv, json, re, io, logging, django, importlib.util
from pathlib import Path
from django.apps import apps
from django.db import models, connection
from django.utils.text import slugify
from openai import OpenAI
from ...core.core import *

# ──────────────────────────────────────────────
# Setup Django environment
# ──────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
DATASET_DIR = Path("/datasets")
LOG_FILE = Path("/var/log/ai_schema_watcher.log")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("ai_schema")

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
def load_dataset(file_path):
    ext = file_path.suffix.lower()
    if ext == ".csv":
        with open(file_path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    elif ext == ".json":
        data = json.loads(file_path.read_text())
        return data if isinstance(data, list) else data.get("data", [])
    return []

def sample_columns(dataset, max_rows=50):
    keys = dataset[0].keys() if dataset else []
    return {k: [str(r.get(k, "")) for r in dataset[:max_rows]] for k in keys}

def ask_ai_for_schema(samples):
    """Ask OpenAI for Django model field mapping."""
    prompt = f"""
You are a Django ORM schema expert.
Given sample column data, return the best Django field definitions.

Use ONLY these field types:
CharField(max_length=255), TextField(), IntegerField(), FloatField(),
DecimalField(max_digits=10, decimal_places=2), BooleanField(),
DateField(), DateTimeField(), EmailField(), JSONField()

Return valid JSON like:
{{
  "column_name": "FieldType"
}}
    
Samples:
{json.dumps(samples, indent=2)}
"""
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        reply = res.choices[0].message.content.strip()
        if "```json" in reply:
            reply = reply.split("```json")[1].split("```")[0].strip()
        return json.loads(reply)
    except Exception as e:
        logger.error(f"AI schema inference failed: {e}")
        return {}

# ──────────────────────────────────────────────
# Build model dynamically
# ──────────────────────────────────────────────
def create_dynamic_model(model_name, field_map):
    attrs = {"__module__": "lti.models"}  # Adjust to your main app
    for field, field_type in field_map.items():
        safe = re.sub(r"\W+", "_", field.lower())
        try:
            attrs[safe] = eval(f"models.{field_type}")
        except Exception:
            attrs[safe] = models.TextField(blank=True, null=True)
    return type(model_name, (models.Model,), attrs)

def create_table_and_load_data(model, dataset):
    with connection.schema_editor() as editor:
        editor.create_model(model)
    model.objects.bulk_create([model(**row) for row in dataset], ignore_conflicts=True)

# ──────────────────────────────────────────────
# Core pipeline
# ──────────────────────────────────────────────
def process_dataset(file_path):
    dataset = load_dataset(file_path)
    if not dataset:
        logger.warning(f"⚠️ Empty or invalid dataset: {file_path.name}")
        return

    samples = sample_columns(dataset)
    schema = ask_ai_for_schema(samples)

    model_name = re.sub(r"\W+", "", file_path.stem.title())
    logger.info(f"🧩 Generating model: {model_name} from {file_path.name}")

    model = create_dynamic_model(model_name, schema)
    apps.all_models["lti"][model_name.lower()] = model

    create_table_and_load_data(model, dataset)

    logger.info(f"✅ Model {model_name} created with {len(dataset)} rows and {len(schema)} fields.")

# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    for file in DATASET_DIR.glob("*"):
        if file.suffix.lower() in (".csv", ".json"):
            process_dataset(file)


