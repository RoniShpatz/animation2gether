from django.shortcuts import render
from game.models import Animations
from django.contrib.auth.decorators import login_required
from .models import Post
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages

@login_required
def post_list(request):
    files_all = Animations.objects.all()
    posts = Post.objects.all().order_by('-created_at')

    
    return render(request, 'post_list.html', {'posts': posts, 'all_files': files_all})


@login_required
def post_edit(request, post_id):
    if request.method == 'POST':
        current_post = Post.objects.filter(id=post_id).first()
        if current_post:
            return render('post_edit.html', {'post':current_post})
        else:
            messages.error(request, "Invalid post.")   
    return redirect('blog:post_list')



@login_required
def post_delete(request, post_id):
    if request.method == 'POST':
        current_post = Post.objects.filter(id=post_id).first() 
        if current_post:
            current_post.delete()
            return redirect('blog:post_list')
        else: 
            messages.error(request, "Invalid post.") 

    return redirect('blog:post_list')