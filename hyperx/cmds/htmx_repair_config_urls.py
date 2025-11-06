import re
from pathlib import Path
import sys

def run_add_app_to_config_urls(app_label, config_urls_path="config/urls.py"):
    """
    Ensure the targeted app is included in config/urls.py.
    If not present, add: path('', include('<app_label>.urls_<app_label>'))
    """
    urls_file = Path(config_urls_path)
    if not urls_file.exists():
        print(f"❌ {config_urls_path} not found.")
        return

    with urls_file.open("r", encoding="utf-8") as f:
        content = f.read()

    # Check if the app's urls are already included
    pattern = rf"include\(['\"]{app_label}\.urls_{app_label}['\"]\)"
    if re.search(pattern, content):
        print(f"ℹ️ {app_label} is already included in {config_urls_path}.")
        return

    # Ensure 'include' is imported
    if "from django.urls import path, include" not in content:
        content = "from django.urls import path, include\n" + content

    # Find urlpatterns list
    urlpatterns_pattern = r"(urlpatterns\s*=\s*\[)(.*?)(\])"
    match = re.search(urlpatterns_pattern, content, re.DOTALL)
    if match:
        before = match.group(1)
        urls_list = match.group(2)
        after = match.group(3)
        new_entry = f"\n    path('', include('{app_label}.urls_{app_label}')),"
        new_urls_list = urls_list + new_entry
        new_content = content[:match.start()] + before + new_urls_list + after + content[match.end():]
        with urls_file.open("w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ Added {app_label} to {config_urls_path}.")
    else:
        print("❌ Could not find urlpatterns list in config/urls.py.")

# Example usage:
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python htmx_repair_config_urls.py <app_label>")
    else:
        add_app_to_config_urls(sys.argv[1])