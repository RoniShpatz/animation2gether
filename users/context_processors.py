from users.models import UploadedFile
from django.contrib.auth.models import AnonymousUser

def profile_photo(request):
    if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
        return {'profile_photo_url': None}  # No photo for logged-out users

    profile_photo = UploadedFile.objects.filter(user_id=request.user).first()
    
    return {'profile_photo_url': profile_photo.file.url if profile_photo else None}