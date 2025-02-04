from django.db import models
from game.models import Animations
from django.contrib.auth.models import User

class Post(models.Model):
    id = models.AutoField(primary_key=True )
    title = models.CharField(max_length=200, null=True)
    content = models.TextField(null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    animation = models.ForeignKey(Animations, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title
