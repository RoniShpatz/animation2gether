from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import signup 
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(success_url='/'), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'), 
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('animation/<int:animation_id>/', views.animation_detail, name='animation_detail'),
    path('delete_animation/<int:animation_id>/', views.delete_animation, name='delete_animation'),
]
