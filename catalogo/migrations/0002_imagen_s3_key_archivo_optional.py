from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagen',
            name='s3_key',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Clave S3'),
        ),
        migrations.AlterField(
            model_name='imagen',
            name='archivo',
            field=models.ImageField(blank=True, null=True, upload_to='imagenes/%Y/%m/%d/', verbose_name='Archivo de imagen'),
        ),
    ]
