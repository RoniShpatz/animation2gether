from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

app_name = 'blog'

urlpatterns= [
     path('', RedirectView.as_view(url='blog/', permanent=True)),
     path('users/', include('users.urls')),
]