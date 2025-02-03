from django.shortcuts import render
from game.models import Animations
from django.contrib.auth.decorators import login_required
from .models import Post
from django.contrib.auth.models import User

@login_required
def post_list(request):
    files_all = Animations.objects.all()
    posts = Post.objects.all().order_by('-created_at')

    
    return render(request, 'post_list.html', {'posts': posts, 'all_files': files_all})