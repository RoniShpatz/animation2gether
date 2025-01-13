from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
# Create your models here.

class Animations(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey( User, on_delete=models.CASCADE,
        related_name='animations'
    )
    date = models.DateTimeField(auto_now_add=True)
    shared_with = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # If user is deleted, keep the animation but set this to NULL
        related_name='shared_animations',
        null=True,
        blank=True
    )
    animation=models.ImageField(storage=MediaCloudinaryStorage(), null=True, blank=True)
    class Meta:
        ordering = ['-date']