# Generated by Django 5.1.4 on 2025-01-09 19:33

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='animations',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='animations',
            name='animation',
            field=models.ImageField(blank=True, null=True, storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to=''),
        ),
    ]
