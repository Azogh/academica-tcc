# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
     path('cadastro/', views.autocadastro_coordenador, name='autocadastro_coordenador'),
      path('login/', views.login_view, name='login'),
       path('painel/', views.painel_coordenador, name='painel'),
]