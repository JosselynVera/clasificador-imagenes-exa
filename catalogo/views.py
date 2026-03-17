import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Imagen
from .serializers import (
    ImagenSerializer,
    ImagenSubidaSerializer,
    ImagenResultadoLambdaSerializer,
    ImagenListSerializer,
)

logger = logging.getLogger(__name__)


class ImagenViewSet(viewsets.ModelViewSet):
    """
    ViewSet CRUD completo para el modelo Imagen.

    Endpoints generados automáticamente:
        GET    /api/imagenes/          → listar todas
        POST   /api/imagenes/          → crear / subir nueva imagen
        GET    /api/imagenes/{id}/     → detalle de una imagen
        PUT    /api/imagenes/{id}/     → actualizar completa
        PATCH  /api/imagenes/{id}/     → actualizar parcial
        DELETE /api/imagenes/{id}/     → eliminar

    Endpoints personalizados:
        PATCH  /api/imagenes/{id}/resultado_lambda/  → Lambda actualiza tipo+descripcion
        GET    /api/imagenes/pendientes/             → imágenes sin procesar
    """

    queryset = Imagen.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        """Usa el serializer adecuado según la acción."""
        if self.action == 'list':
            return ImagenListSerializer
        if self.action == 'create':
            return ImagenSubidaSerializer
        if self.action == 'resultado_lambda':
            return ImagenResultadoLambdaSerializer
        return ImagenSerializer

    def create(self, request, *args, **kwargs):
        """
        POST /api/imagenes/
        Sube la imagen a S3 y crea el registro en BD.
        El frontend llama a este endpoint; luego Lambda clasifica.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Si no viene nombre, usar el nombre del archivo
        if not serializer.validated_data.get('nombre'):
            archivo = serializer.validated_data.get('archivo')
            serializer.validated_data['nombre'] = archivo.name if archivo else 'sin_nombre'

        imagen = serializer.save()
        logger.info(f'Imagen subida: id={imagen.id}, nombre={imagen.nombre}')

        # Retornar el detalle completo
        response_serializer = ImagenSerializer(imagen, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='resultado_lambda')
    def resultado_lambda(self, request, pk=None):
        """
        PATCH /api/imagenes/{id}/resultado_lambda/
        Endpoint exclusivo para que la función Lambda actualice
        el tipo_detectado y la descripción de la imagen.

        Body esperado:
        {
            "tipo_detectado": "Factura",
            "descripcion": "Factura comercial con IVA del 15%",
            "procesada": true
        }
        """
        imagen = self.get_object()
        serializer = ImagenResultadoLambdaSerializer(
            imagen, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        imagen = serializer.save(procesada=True)

        logger.info(
            f'Lambda actualizó imagen id={imagen.id}: '
            f'tipo={imagen.tipo_detectado}'
        )

        return Response(
            ImagenSerializer(imagen, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'], url_path='pendientes')
    def pendientes(self, request):
        """
        GET /api/imagenes/pendientes/
        Retorna las imágenes que Lambda aún no ha procesado.
        """
        qs = Imagen.objects.filter(procesada=False)
        serializer = ImagenListSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        GET /api/imagenes/stats/
        Estadísticas rápidas por tipo de imagen.
        """
        from django.db.models import Count
        data = (
            Imagen.objects
            .values('tipo_detectado')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        return Response({
            'total_imagenes': Imagen.objects.count(),
            'por_tipo': list(data),
        })
