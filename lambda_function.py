import json
import base64
import uuid
import os
import logging
import urllib.request
import urllib.error
from datetime import datetime

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client  = boto3.client('s3')
rek_client = boto3.client('rekognition')

DJANGO_API_URL = os.environ.get('DJANGO_API_URL', '')
S3_BUCKET      = os.environ.get('S3_BUCKET', '')
MAX_LABELS     = 20
MIN_CONFIDENCE = 70.0

CORS_HEADERS = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,OPTIONS',
    'Content-Type': 'application/json',
}


def lambda_handler(event, context):
    logger.info("Evento recibido: %s", json.dumps(event)[:500])

    # Manejar preflight OPTIONS
    method = event.get('requestContext', {}).get('http', {}).get('method', '') \
             or event.get('httpMethod', '')
    if method == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    # Parsear body
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        elif isinstance(event.get('body'), dict):
            body = event['body']
        else:
            body = event
    except (json.JSONDecodeError, TypeError) as e:
        return _response(400, {'error': f'Body inválido: {str(e)}'})

    nombre       = body.get('nombre', f'imagen_{uuid.uuid4().hex[:8]}.jpg')
    imagen_b64   = body.get('imagen_base64', '')
    content_type = body.get('content_type', 'image/jpeg')
    s3_key       = body.get('s3_key', '')

    # 1. Subir a S3 si viene en base64
    if imagen_b64 and not s3_key:
        s3_key = _subir_a_s3(imagen_b64, nombre, content_type)
        if not s3_key:
            return _response(500, {'error': 'No se pudo subir la imagen a S3'})

    if not s3_key:
        return _response(400, {'error': 'Se requiere imagen_base64 o s3_key'})

    logger.info("Imagen en S3: s3://%s/%s", S3_BUCKET, s3_key)

    # 2. Llamar a Rekognition
    etiquetas = _detectar_etiquetas(s3_key)
    if etiquetas is None:
        return _response(500, {'error': 'Error al llamar a Rekognition'})

    logger.info("Etiquetas: %s", [e['Name'] for e in etiquetas[:8]])

    # 3. Clasificar
    tipo_detectado = _clasificar(etiquetas)
    descripcion    = _generar_descripcion(etiquetas, tipo_detectado, nombre)

    logger.info("Clasificación: tipo=%s", tipo_detectado)

    # 4. Guardar en Django
    id_imagen = _guardar_en_django(nombre, s3_key, tipo_detectado, descripcion)

    # 5. Responder
    return _response(200, {
        'nombre':         nombre,
        's3_key':         s3_key,
        'tipo_detectado': tipo_detectado,
        'descripcion':    descripcion,
        'etiquetas_top':  [{'nombre': e['Name'], 'confianza': round(e['Confidence'], 1)}
                           for e in etiquetas[:5]],
        'id_django':      id_imagen,
    })


def _subir_a_s3(imagen_b64, nombre, content_type):
    try:
        imagen_bytes = base64.b64decode(imagen_b64)
        fecha_path   = datetime.utcnow().strftime('%Y/%m/%d')
        unique_name  = f"{uuid.uuid4().hex[:8]}_{nombre}"
        s3_key       = f"imagenes/{fecha_path}/{unique_name}"
        s3_client.put_object(
            Bucket=S3_BUCKET, Key=s3_key,
            Body=imagen_bytes, ContentType=content_type,
        )
        logger.info("Subida exitosa a S3: %s", s3_key)
        return s3_key
    except Exception as e:
        logger.error("Error subiendo a S3: %s", str(e))
        return None


def _detectar_etiquetas(s3_key):
    try:
        response = rek_client.detect_labels(
            Image={'S3Object': {'Bucket': S3_BUCKET, 'Name': s3_key}},
            MaxLabels=MAX_LABELS,
            MinConfidence=MIN_CONFIDENCE,
        )
        return response.get('Labels', [])
    except Exception as e:
        logger.error("Error en Rekognition: %s", str(e))
        return None


def _clasificar(etiquetas):
    nombres = {e['Name'].lower() for e in etiquetas}
    reglas = [
        ('Factura',   {'invoice','receipt','bill','payment','voucher','tax','barcode','qr code','price tag','financial'}),
        ('Documento', {'text','document','paper','letter','page','form','contract','certificate','report','newspaper','book','handwriting','signature','id card','passport','license'}),
        ('Gráfico',  {'diagram','chart','graph','flowchart','map','blueprint','plan','schematic','infographic','presentation','whiteboard','drawing'}),
        ('Captura',   {'screenshot','screen','monitor','computer','laptop','tablet','phone','mobile','display','interface','website','app','software','desktop'}),
        ('Foto',      {'person','people','face','portrait','selfie','animal','nature','landscape','building','car','food','sport','travel','sky','tree','flower','city','street','photography'}),
    ]
    for tipo, palabras in reglas:
        if nombres & palabras:
            return tipo
    return 'Otro'


def _generar_descripcion(etiquetas, tipo, nombre):
    plantillas = {
        'Factura':   f"Factura o comprobante detectado en '{nombre}'.",
        'Documento': f"Documento de texto detectado en '{nombre}'.",
        'Gráfico':   f"Gráfico o diagrama detectado en '{nombre}'.",
        'Captura':   f"Captura de pantalla detectada en '{nombre}'.",
        'Foto':      f"Fotografía detectada en '{nombre}'.",
        'Otro':      f"Imagen '{nombre}' clasificada como tipo general.",
    }
    return plantillas.get(tipo, f"Imagen procesada: '{nombre}'.")


def _guardar_en_django(nombre, s3_key, tipo, descripcion):
    if not DJANGO_API_URL:
        logger.warning("DJANGO_API_URL no configurada")
        return None
    try:
        payload = json.dumps({
            'nombre': nombre,
            'tipo_detectado': tipo,
            'descripcion': descripcion,
            'procesada': True,
        }).encode('utf-8')
        req = urllib.request.Request(
            url=DJANGO_API_URL.rstrip('/') + '/',
            data=payload,
            method='POST',
            headers={'Content-Type': 'application/json', 'User-Agent': 'Lambda-Clasificador/1.0'},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_body = json.loads(resp.read().decode('utf-8'))
            id_creado = resp_body.get('id')
            logger.info("Registro creado en Django, id=%s", id_creado)
            return id_creado
    except Exception as e:
        logger.error("Error guardando en Django: %s", str(e))
        return None


def _response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body, ensure_ascii=False),
    }
