# No arquivo core/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # URLs de Páginas e Autenticação
    path('', views.landing_page, name='landing_page'),
    path('cadastro/', views.autocadastro_coordenador, name='autocadastro_coordenador'),
    path('login/', views.login_view, name='login'),
    path('painel/', views.painel_coordenador, name='painel'),
    path('logout/', auth_views.LogoutView.as_view(next_page='landing_page'), name='logout'),
    
    # URLs para o CRUD de Matriz Curricular
    path('matrizes/', views.listar_matrizes, name='listar_matrizes'),
    path('matrizes/adicionar/', views.adicionar_matriz, name='adicionar_matriz'),
    path('matrizes/editar/<int:pk>/', views.editar_matriz, name='editar_matriz'),
    path('matrizes/excluir/<int:pk>/', views.excluir_matriz, name='excluir_matriz'),
    
    # URLs para o CRUD de Disciplinas
    path('disciplinas/', views.listar_disciplinas, name='listar_disciplinas'),
    path('disciplinas/adicionar/', views.adicionar_disciplina, name='adicionar_disciplina'),
    path('disciplinas/editar/<int:pk>/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplinas/excluir/<int:pk>/', views.excluir_disciplina, name='excluir_disciplina'),
    
     # URLs para o CRUD de Turmas
    path('turmas/', views.listar_turmas, name='listar_turmas'),
    path('turmas/adicionar/', views.adicionar_turma, name='adicionar_turma'),
    path('turmas/editar/<int:pk>/', views.editar_turma, name='editar_turma'),
    path('turmas/excluir/<int:pk>/', views.excluir_turma, name='excluir_turma'),
    
    # URLs para o CRUD de Horários
    path('horarios/', views.listar_horarios, name='listar_horarios'),
    path('horarios/adicionar/', views.adicionar_horario, name='adicionar_horario'),
    path('horarios/editar/<int:pk>/', views.editar_horario, name='editar_horario'),
    path('horarios/excluir/<int:pk>/', views.excluir_horario, name='excluir_horario'),
]