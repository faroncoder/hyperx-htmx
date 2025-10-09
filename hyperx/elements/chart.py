"""
hx:chart
────────────────────────────────────────────
Declarative Chart.js data visualization.
"""

from hyperx.templatetags.hyperx import register_hx_tag
import json

@register_hx_tag("chart")
def convert_chart(tag, attrs):
    """
    Usage:
      <hx:chart type="bar" labels="Q1,Q2,Q3,Q4" data="10,20,30,40" title="Sales" />
    """
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
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
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
