# Clasificador de Imágenes

Aplicación web desarrollada con Django y desplegada en AWS Elastic Beanstalk que permite clasificar imágenes automáticamente usando Amazon Rekognition a través de una función Lambda.

## Descripción

El usuario sube una imagen desde la interfaz web. Django recibe la imagen, la convierte a base64 y la envía a una función Lambda a través de API Gateway. Lambda sube la imagen a S3, llama a Rekognition para detectar etiquetas y determina el tipo de imagen. El resultado se devuelve a Django que lo guarda en la base de datos y lo muestra al usuario.

## Tecnologías utilizadas

- Django 4.2 con Django REST Framework
- AWS Elastic Beanstalk para el despliegue del backend
- AWS Lambda para la clasificación de imágenes
- AWS S3 para el almacenamiento de imágenes
- AWS Rekognition para la detección y clasificación
- AWS API Gateway para exponer la función Lambda
- SQLite en desarrollo

## Tipos de imagen detectados

- Documento
- Foto
- Factura
- Gráfico
- Captura
- Otro

## Estructura del proyecto
clasificador_vera/
├── .ebextensions/         configuración para Elastic Beanstalk
├── catalogo/              app principal con modelos, vistas y API REST
│   └── migrations/        migraciones de base de datos
├── imagen_classifier/     configuración del proyecto Django
├── lambda/
│   └── lambda_function.py función Lambda desplegada en AWS
├── index.html             interfaz de usuario
├── manage.py
├── Procfile               comando de inicio para Elastic Beanstalk
└── requirements.txt       dependencias del proyecto

## Pasos de despliegue

1. Se creó un bucket S3 en la región us-east-1 con acceso público habilitado y configuración CORS para permitir solicitudes desde el frontend.

2. Se creó un usuario IAM con permisos de acceso a S3 y se generaron las claves de acceso para usarlas en Django.

3. Se configuró el proyecto Django con la app catalogo que define el modelo Imagen con los campos nombre, tipo_detectado, descripcion, archivo, s3_key, fecha_subida y procesada. Se habilitó la API REST con Django REST Framework y el panel de administración.

4. Se desplegó el backend en AWS Elastic Beanstalk usando Python 3.11 sobre Amazon Linux 2023. Las variables de entorno se configuraron directamente en EB incluyendo las credenciales AWS, la clave secreta de Django y la URL de Lambda.

5. Se creó la función Lambda en Python 3.11 con los permisos AmazonS3FullAccess y AmazonRekognitionFullAccess. La función recibe la imagen en base64, la sube a S3, llama a Rekognition para detectar etiquetas, clasifica la imagen según las etiquetas detectadas y devuelve el resultado.

6. Se creó una HTTP API en API Gateway con una ruta POST /clasificar conectada a la función Lambda.

7. Para evitar el error de CORS entre el frontend en HTTP y la API Gateway en HTTPS, se implementó un proxy en Django. El frontend llama a /clasificar/ en el mismo servidor y Django reenvía la petición a Lambda internamente.

## Variables de entorno requeridas

Copiar .env.example como .env y completar los valores:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_STORAGE_BUCKET_NAME
- AWS_S3_REGION_NAME
- LAMBDA_URL

## Ejecución local
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

La clasificación funciona localmente siempre que las variables de entorno AWS estén configuradas correctamente y LAMBDA_URL apunte al endpoint de API Gateway desplegado.

https://github.com/user-attachments/assets/be97014d-a09f-4f90-8911-db1c943e13ca
