import os
import json
import base64
import urllib.request
import urllib.error
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Imagen

logger = logging.getLogger(__name__)


def index(request):
    imagenes = Imagen.objects.order_by('-fecha_subida')[:20]
    return render(request, 'index.html', {'imagenes': imagenes})


@csrf_exempt
def proxy_clasificar(request):
    """
    Proxy: el frontend llama aquí (mismo origen, sin CORS),
    y Django reenvía a Lambda internamente.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Body inválido'}, status=400)

    lambda_url = os.environ.get('LAMBDA_URL', '')
    if not lambda_url:
        return JsonResponse({'error': 'LAMBDA_URL no configurada'}, status=500)

    try:
        payload = json.dumps(body).encode('utf-8')
        req = urllib.request.Request(
            url=lambda_url,
            data=payload,
            method='POST',
            headers={'Content-Type': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            resultado = json.loads(resp.read().decode('utf-8'))
            return JsonResponse(resultado)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        logger.error("Lambda HTTPError %s: %s", e.code, error_body)
        return JsonResponse({'error': f'Lambda error {e.code}: {error_body}'}, status=500)
    except Exception as e:
        logger.error("Error llamando a Lambda: %s", str(e))
        return JsonResponse({'error': str(e)}, status=500)
