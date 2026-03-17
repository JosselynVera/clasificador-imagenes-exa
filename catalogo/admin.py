from django.contrib import admin
from django.utils.html import format_html
from .models import Imagen


@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display    = ['id', 'nombre', 'tipo_detectado', 'procesada', 'fecha_subida', 'vista_previa']
    list_filter     = ['tipo_detectado', 'procesada', 'fecha_subida']
    search_fields   = ['nombre', 'descripcion']
    readonly_fields = ['fecha_subida', 'url_archivo', 'vista_previa']
    ordering        = ['-fecha_subida']

    fieldsets = (
        ('Archivo', {
            'fields': ('nombre', 'archivo', 'url_archivo', 'vista_previa')
        }),
        ('Clasificación (completada por Lambda)', {
            'fields': ('tipo_detectado', 'descripcion', 'procesada')
        }),
        ('Metadatos', {
            'fields': ('fecha_subida',),
            'classes': ('collapse',)
        }),
    )

    def vista_previa(self, obj):
        if obj.archivo:
            return format_html(
                '<img src="{}" style="max-height:80px; max-width:120px; '
                'border-radius:4px; object-fit:cover;" />',
                obj.archivo.url
            )
        return '—'
    vista_previa.short_description = 'Vista previa'
