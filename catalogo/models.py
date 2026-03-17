from django.db import models
from django.utils import timezone


class Imagen(models.Model):
    TIPOS_IMAGEN = [
        ('Documento',  'Documento'),
        ('Foto',       'Foto'),
        ('Factura',    'Factura'),
        ('Gráfico',    'Gráfico'),
        ('Captura',    'Captura de pantalla'),
        ('Otro',       'Otro'),
        ('Pendiente',  'Pendiente de clasificar'),
    ]

    nombre         = models.CharField(max_length=255, verbose_name='Nombre del archivo')
    tipo_detectado = models.CharField(max_length=50, choices=TIPOS_IMAGEN, default='Pendiente', verbose_name='Tipo detectado')
    descripcion    = models.TextField(blank=True, default='', verbose_name='Descripción')
    archivo        = models.ImageField(upload_to='imagenes/%Y/%m/%d/', blank=True, null=True, verbose_name='Archivo de imagen')
    s3_key         = models.CharField(max_length=500, blank=True, default='', verbose_name='Clave S3')
    fecha_subida   = models.DateTimeField(default=timezone.now, verbose_name='Fecha de subida')
    procesada      = models.BooleanField(default=False, verbose_name='¿Procesada por Lambda?')

    class Meta:
        verbose_name        = 'Imagen'
        verbose_name_plural = 'Imágenes'
        ordering            = ['-fecha_subida']

    def __str__(self):
        return f'{self.nombre} ({self.tipo_detectado})'

    @property
    def url_archivo(self):
        """Retorna la URL pública del archivo en S3."""
        if self.archivo:
            return self.archivo.url
        if self.s3_key:
            bucket = 'clasificador-imagenes-vera'
            region = 'us-east-1'
            return f'https://{bucket}.s3.{region}.amazonaws.com/{self.s3_key}'
        return None
