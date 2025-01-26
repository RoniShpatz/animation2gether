from django.shortcuts import render
from users.forms import LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

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
    

def profile(request):


    return render('profile.html')