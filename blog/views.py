from django.shortcuts import render
from game.models import Animations
from django.contrib.auth.decorators import login_required
from blog.models import Post
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
    current_post = Post.objects.filter(id=post_id).first()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        # Only update if there's an actual change
        if title == current_post.title and content == current_post.content:
            messages.info(request, "No changes detected.")
            return redirect("blog:post_list")

        if title:
            current_post.title = title
        if content:
            current_post.content = content

        current_post.save()  
        messages.success(request, "Post updated successfully.")
        return redirect("blog:post_list")

    return render(request, 'post_edit.html', {'post': current_post})



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