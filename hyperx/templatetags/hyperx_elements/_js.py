 """
    <hx:import>
    ─────────────────────────────────────────────
    Declaratively import CSS and JS resources.

    🧠 ATTRIBUTES
    • css="css/dashboard.css"
    • js="js/app.js"

    🧩 EXAMPLE
    {% hx %}
      <hx:import css="css/admin.css" js="js/dashboard.js" />
    {% endhx %}
    """
    
    
    
@register_hx_tag("js")
def convert_js(tag, attrs):
    subtype = tag.name.split(":")[1]
    if subtype == "fetch":
        url, method, then = attrs.get("url"), attrs.get("method", "GET").upper(), attrs.get("then", "")
        return f"""
        <script>
        fetch("{url}", {{method:"{method}"}})
          .then(r=>r.text())
          .then(html=>{{const [sel,tgt] = "{then}".split(":"); if(sel==="render") document.querySelector(tgt).innerHTML = html;}});
        </script>
        """
    if subtype == "on":
        event, target, url = attrs.get("event","click"), attrs.get("target"), attrs.get("url","")
        return f"""
        <script>
        document.querySelector("{target}").addEventListener("{event}", async()=>{{
            const res = await fetch("{url}"); const html = await res.text();
            document.querySelector("{attrs.get('then','#output')}").innerHTML = html;
        }});
        </script>
        """
    return "<!-- Unknown hxjs subtype -->"
