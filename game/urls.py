from django.urls import path
from . import views 


app_name = 'game'

urlpatterns = [
    path('', views.index, name='index'),

    path('animate/<int:game_id>/', views.animate, name='animate'),
    path('create_game', views.create_game, name='create_game'),         
    path('save-frame/', views.save_frame, name='save_frame'),
    path('games-on/', views.games_on, name='games_on'),
    path('accept_game/', views.accept_game, name='accept_game'),
    path('respond/', views.respond, name='respond'),
 
    
]


