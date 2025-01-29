# Generated by Django 5.1.4 on 2025-01-28 19:27

import cloudinary_storage.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_rename_user_shaed_with_tempframe_user_share_with'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='messagegame',
            options={'ordering': ['timestamp']},
        ),
        migrations.AlterField(
            model_name='animations',
            name='animation_file',
            field=models.FileField(blank=True, null=True, storage=cloudinary_storage.storage.MediaCloudinaryStorage(), upload_to=''),
        ),
    ]
