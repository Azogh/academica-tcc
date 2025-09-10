# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.autocadastro_coordenador, name='autocadastro_coordenador'),
     path('login/', views.login_view, name='login'),
]