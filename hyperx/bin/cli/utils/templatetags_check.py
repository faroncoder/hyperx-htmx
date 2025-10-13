import platform, os
from django.conf import settings
import platform, os
import subprocess




def templatetags_install():
    try:
        from hyperx.templatetags.hyperx import TAG_CONVERTERS
        count = len(TAG_CONVERTERS)
        print(f"✅ {count} declarative <hx:*> tags loaded.")
        report["tags"] = True
    except Exception as e:
        print(f"❌ Failed to load template tags: {e}")
        report["tags"] = False


def _run_templatetags_check():
    templatetags_install = []
    try:
        from hyperx.templatetags import hyperx_elements
        count = len(hyperx_elements.__all__)
        print(f"✅ {count} HyperX Elements modules loaded.")
        report["elements"] = True
    except Exception as e:
        print(f"❌ Failed to load HyperX Elements: {e}")
        report["elements"] = False


