from django.shortcuts import render
from users.forms import LoginForm, UploadedFile, UserUpdateForm, UploadForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from game.models import Animations
from blog.models import Post
from django.shortcuts import get_object_or_404, redirect

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
    form = UserUpdateForm(instance=request.user)
    profile_photo_form = UploadForm()
    files = UploadedFile.objects.filter(user_id=request.user)

    if request.method == 'POST':
        if 'upload-profile-photo' in request.POST:
            profile_photo_form = UploadForm(request.POST, request.FILES)
            
            if profile_photo_form.is_valid():
                try:
                    uploaded_file = profile_photo_form.save(commit=False)
                    uploaded_file.user_id = request.user
                    uploaded_file.save()
                    messages.success(request, 'Profile photo uploaded successfully!')
                except Exception as e:
                    messages.error(request, f'Upload failed: {str(e)}')
                    # Log the full error for debugging
                    import logging
                    logging.error(f"File upload error: {e}")
            else:
                # Log form errors
                messages.error(request, 'Form is invalid')
                for field, errors in profile_photo_form.errors.items():
                    messages.error(request, f"{field}: {errors}")
        elif 'update-profile' in request.POST:
            form = UserUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        elif 'update-profile-photo' in request.POST:
            photo_id = request.POST.get("photo-id")
            current_photo = get_object_or_404(UploadedFile, id=photo_id)
            profile_photo_form = UploadForm(request.POST, request.FILES, instance=current_photo)
            if profile_photo_form.is_valid():
                profile_photo_form.save()
                messages.success(request, 'Profile photo updated successfully!')
            else:
                messages.error(request, 'Failed to update profile photo.')
                for field, errors in profile_photo_form.errors.items():
                    messages.error(request, f"{field}: {errors}")

        elif 'delete-profile-photo' in request.POST:
            photo_id = request.POST.get("photo-id")
            try:
                current_photo = get_object_or_404(UploadedFile, id=photo_id)
                current_photo.delete()
                messages.success(request, 'Profile photo deleted successfully!')
            except Exception as e:
                messages.error(request, f'Failed to delete profile photo: {str(e)}')
    
    else:
        form = UserUpdateForm(instance=request.user)
        profile_photo_form = UploadForm()
    context = {
        'my_animations': animation_of_user,
        'with_animaton': animation_with_user,
        'form': form, 
        'profile_photo_form': profile_photo_form, 
        'files': files

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
