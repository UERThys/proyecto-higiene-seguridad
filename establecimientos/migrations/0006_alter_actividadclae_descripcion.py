# Generated by Django 5.2 on 2025-05-22 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('establecimientos', '0005_actividadclae'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actividadclae',
            name='descripcion',
            field=models.CharField(max_length=512),
        ),
    ]
