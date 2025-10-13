from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import subprocess
from django.core import management
from hyperx.core.core import *
from hyperx.hx_cli import *
from hxperx.bin.autodiscover import autodiscover

def hx_cli_terminal(request):
    subprocess.run(["hx-cli"], check=True)


def hx_install_core(*args, **kwargs):
    from .opt.hyperx.core_install_hyperx import main as install_hyperx
    install_hyperx(*args, **kwargs)


def hx_mgr_cmd(install_hyperx, *args, **kwargs):
        management.call_command(install_hyperx, *args, **kwargs)


def hx_dbready(*args, **kwargs):
    subprocess.run(["python", "manage.py", "makemigrations"], check=True)
    subprocess.run(["python", "manage.py", "migrate"], check=True)
    subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=True)


def hx_daphne(*args, **kwargs):
    subprocess.run(["daphne", "-b", "0.0.0.0:8000", "config.asgi:application"], check=True)
    
    
