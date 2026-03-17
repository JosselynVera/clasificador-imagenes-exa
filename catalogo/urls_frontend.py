from django.urls import path
from .views_frontend import index, proxy_clasificar

urlpatterns = [
    path('', index, name='index'),
    path('clasificar/', proxy_clasificar, name='proxy_clasificar'),
]
