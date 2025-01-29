from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils import timezone
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
    animation_file=models.FileField(storage=MediaCloudinaryStorage(), null=True, blank=True)
    class Meta:
        ordering = ['-date']


class ActiveGame(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='active_games'
    )
    user_share = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_active_games'
    )
    is_accepted = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)

class TempFrame(models.Model):
    id = models.AutoField(primary_key=True)
    animation_title = models.CharField(max_length=20) 
    user = models.ForeignKey( User, on_delete=models.CASCADE,
        related_name='temp_img'
    )
    user_share_with=models.ForeignKey( User, on_delete=models.CASCADE,
        related_name='temp_img_shared',
         null=True,
         blank=True,
    )
    frame_number = models.PositiveIntegerField()
    file = models.ImageField(storage=MediaCloudinaryStorage())
    created_at = models.DateTimeField(auto_now_add=True)
    game_id= models.ForeignKey(
    ActiveGame,
    on_delete=models.CASCADE,
    related_name='temp_frames'
)

class MessageGame(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    temp_frame = models.ForeignKey(TempFrame, on_delete=models.CASCADE, related_name='temp_file')
    game_id= models.ForeignKey(ActiveGame, on_delete=models.CASCADE,related_name='game_active')
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    class Meta:
        ordering = ['timestamp']

    def get_frame_chain(self):
        """
        Returns all frames in the game ordered by frame number
        """
        return TempFrame.objects.filter(
            game_id=self.game_id
        ).order_by('frame_number')