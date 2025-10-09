from django.shortcuts import render
import socket

def daphne_status_view(request):
    host = "localhost"
    port = 7777
    daphne_running = False

    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                daphne_running = True
                break
        except ConnectionRefusedError:
            port += 1
            if port > 7787:
                daphne_running = False
                break
        except Exception:
            daphne_running = False
            break

    context = {
        "daphne_running": daphne_running,
        "host": host,
        "port": port,
    }

    # For HTMX requests, return only the partial fragment
    if request.headers.get("HX-Request") == "true":
        return render(request, "partials/daphne_status_fragment.html", context)

    # For normal requests, return the full page wrapper
    return render(request, "daphne_status.html", context)
