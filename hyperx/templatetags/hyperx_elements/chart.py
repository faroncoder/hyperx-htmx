
"""
    <hx:chart>
    ─────────────────────────────────────────────
    Declarative Chart.js visualization block.

    🧠 ATTRIBUTES
    • type="bar|line|pie|doughnut" → Chart type.
    • labels="Q1,Q2,Q3" → CSV list of axis labels.
    • data="10,20,30" → CSV of data points.
    • title="..." → Chart title.

    🧩 EXAMPLE
    {% hx %}
      <hx:chart type="bar" labels="Q1,Q2,Q3" data="12,19,7" title="Sales" />
    {% endhx %}
    """

from django import template
register = template.Library()
# from hyperx.templatetags.hyperx import *
from hyperx.bin.cli.logger.hx_logger import *
from hyperx.core.hx.hx_converter import register_hx_tag
from hyperx.core.hx.hx_actions_rules import build_htmx_attrs
from django.utils.html import escape
import json
_logger = load_logger("hx-chart")
_logger.info("hx-chart initialized")



@register_hx_tag("chart")
def convert_chart(tag, attrs):


    chart_id = attrs.get("id", "hx-chart")
    chart_type = attrs.get("type", "bar")
    labels = attrs.get("labels", "").split(",")
    data = attrs.get("data", "").split(",")
    title = attrs.get("title", "Chart")
    color = attrs.get("color", "rgba(54,162,235,0.5)")

    dataset = {
        "labels": labels,
        "datasets": [{
            "label": title,
            "data": [float(d.strip() or 0) for d in data],
            "backgroundColor": color
        }]
    }

    return f"""
    <canvas id="{chart_id}" style="max-height:400px;"></canvas>
    <script type="text/javascript" src="{{% static 'js/chart.js' %}}"></script>
    <script type="text/javascript">
    const ctx = document.getElementById("{chart_id}");
    new Chart(ctx, {{
      type: "{chart_type}",
      data: {json.dumps(dataset)},
      options: {{
        responsive: true,
        plugins: {{ legend: {{ position: 'bottom' }} }}
      }}
    }});
    </script>
    """
