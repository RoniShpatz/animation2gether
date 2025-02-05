from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
# Create your models here.


class UploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.ImageField(storage=MediaCloudinaryStorage())
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(
    User, on_delete=models.CASCADE, 
    null=True,  
    blank=True  
)