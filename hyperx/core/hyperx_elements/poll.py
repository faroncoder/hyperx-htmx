"""
hx:poll
────────────────────────────────────────────
Periodic polling for real-time updates using HTMX.
"""

from hyperx.templatetags.hyperx import register_hx_tag

@register_hx_tag("poll")
def convert_poll(tag, attrs):
    """
    Usage:
      <hx:poll get="dashboard:update" every="5s" target="#stats" />
    """
    get = attrs.get("get")
    every = attrs.get("every", "10s")
    target = attrs.get("target", "#content")
    swap = attrs.get("swap", "innerHTML")

    return f'''
    <div hx-get="/{get}" hx-trigger="every {every}" hx-target="{target}" hx-swap="{swap}">
      <div class="text-muted small">
        <i class="fas fa-sync-alt fa-spin me-1"></i>Auto-updating every {every}
      </div>
    </div>
    '''
