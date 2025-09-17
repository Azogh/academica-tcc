# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
     path('cadastro/', views.autocadastro_coordenador, name='autocadastro_coordenador'),
      path('login/', views.login_view, name='login'),
       path('painel/', views.painel_coordenador, name='painel'),
       path('matrizes/', views.listar_matrizes, name='listar_matrizes'),
        path('matrizes/adicionar/', views.adicionar_matriz, name='adicionar_matriz'),
        path('matrizes/editar/<int:pk>/', views.editar_matriz, name='editar_matriz'),
        path('matrizes/excluir/<int:pk>/', views.excluir_matriz, name='excluir_matriz'),
]