from django.apps import AppConfig


class DeclarativesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'declaratives'
    verbose_name = 'HyperX Declaratives Showcase'
    
    def ready(self):
        """Initialize declaratives app with htmx_core integration"""
        print("[DECLARATIVES] 🎭 HyperX Declaratives app loading...")
        print("[DECLARATIVES] 🔗 Integrated with HTMX Core")
        print("[DECLARATIVES] ✨ Declarative reactive components ready")
