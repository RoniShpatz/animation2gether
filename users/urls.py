from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import signup 

app_name = 'users'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(success_url='/'), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(next_page='users:login'), name='logout'), 
    path('signup/', signup, name='signup'),
]
