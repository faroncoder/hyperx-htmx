# hyperx/urls.py
from django.urls import path
from hyperx.views.upload_handler import upload_handler

app_name = "hyperx"

urlpatterns = [
    path("upload/", upload_handler, name="upload_handler"),
    path("install/", hyperx_install, name="hyperx_install"),  # from core_install_hyperx.py
    
]
