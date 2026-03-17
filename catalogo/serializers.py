from rest_framework import serializers
from .models import Imagen


class ImagenSerializer(serializers.ModelSerializer):
    url_archivo = serializers.ReadOnlyField()

    class Meta:
        model  = Imagen
        fields = ['id', 'nombre', 'tipo_detectado', 'descripcion',
                  'archivo', 's3_key', 'url_archivo', 'fecha_subida', 'procesada']
        read_only_fields = ['id', 'fecha_subida', 'url_archivo']


class ImagenSubidaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Imagen
        fields = ['id', 'nombre', 'archivo', 's3_key']


class ImagenResultadoLambdaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Imagen
        fields = ['id', 'nombre', 'tipo_detectado', 'descripcion', 's3_key', 'procesada']
        read_only_fields = ['id', 'nombre']


class ImagenListSerializer(serializers.ModelSerializer):
    url_archivo = serializers.ReadOnlyField()

    class Meta:
        model  = Imagen
        fields = ['id', 'nombre', 'tipo_detectado', 'fecha_subida', 'url_archivo', 'procesada']
