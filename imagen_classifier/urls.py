from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('catalogo.urls')),
    path('', include('catalogo.urls_frontend')),  # Interfaz HTML
]

# Servir media en desarrollo (en prod lo sirve S3)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
