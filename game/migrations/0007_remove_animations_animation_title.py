# Generated by Django 5.1.4 on 2025-02-04 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_animations_animation_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animations',
            name='animation_title',
        ),
    ]
