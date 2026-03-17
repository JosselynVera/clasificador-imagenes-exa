from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Imagen',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Nombre original del archivo subido', max_length=255, verbose_name='Nombre del archivo')),
                ('tipo_detectado', models.CharField(
                    choices=[
                        ('Documento', 'Documento'), ('Foto', 'Foto'), ('Factura', 'Factura'),
                        ('Diagrama', 'Diagrama'), ('Captura', 'Captura de pantalla'),
                        ('Otro', 'Otro'), ('Pendiente', 'Pendiente de clasificar'),
                    ],
                    default='Pendiente', max_length=50, verbose_name='Tipo detectado'
                )),
                ('descripcion', models.TextField(blank=True, default='', verbose_name='Descripción')),
                ('archivo', models.ImageField(upload_to='imagenes/%Y/%m/%d/', verbose_name='Archivo de imagen')),
                ('fecha_subida', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de subida')),
                ('procesada', models.BooleanField(default=False, verbose_name='¿Procesada por Lambda?')),
            ],
            options={
                'verbose_name': 'Imagen',
                'verbose_name_plural': 'Imágenes',
                'ordering': ['-fecha_subida'],
            },
        ),
    ]
