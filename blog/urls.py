from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name = 'blog'

urlpatterns= [
     path('', views.post_list, name='post_list'),
#     path('post/new/', views.post_create, name='post_create'),
#     path('post/<int:pk>/', views.post_detail, name='post_detail'),
     
]