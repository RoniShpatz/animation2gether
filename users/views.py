from django.shortcuts import render
from users.forms import LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from game.models import Animations
from blog.models import Post
# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('users:login') 
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})



class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'


def debug_template_path(request):
    try:
        template = get_template('users/login.html')
        return render(request, 'users/login.html')
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})
    
@login_required
def profile(request):
    current_user = request.user
    animation_of_user = Animations.objects.filter(user=current_user)
    animation_with_user = Animations.objects.filter(shared_with=current_user)
    context = {
        'my_animations': animation_of_user,
        'with_animaton': animation_with_user

    }

    return render(request, 'profile.html', context)


@login_required
def animation_detail(request, animation_id):
    animation = Animations.objects.filter(id=animation_id).first()
    return render (request, 'animation_detail.html', {'animation': animation})


@login_required
def delete_animation(request, animation_id):
    if request.method == 'POST':
        current_aniamtion = Animations.objects.filter(id=animation_id).first()
        if current_aniamtion:
            current_aniamtion.delete()
            messages.success(request, "Animation deleted successfully.")
            return redirect("users:profile")
    else: messages.error(request, 'Animaton didnt found')
    return redirect("profile")

@login_required
def share_animation(request, animation_id):
    if request.method == 'POST':
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        current_aniamtion = Animations.objects.filter(id=animation_id).first()
        if current_aniamtion:
           new_post = Post(
            title = title,
            content = content,
            author = request.user,
            animation= current_aniamtion,  
           )
           new_post.save()
           messages.success(request, "Post created successfully.")
           return redirect("blog:post_list") 
        else: messages.error(request, "Invalid request method.")   
      
    return redirect("blog:post_list")
