# upload/urls.py

from django.urls import path
from . import views

# Define o namespace para esta aplicação
app_name = 'upload'

urlpatterns = [
    # URL para a página de upload e listagem de históricos
    path('historicos/', views.importar_historico, name='importar_historico'),
    
    # URL para processar o formulário de upload (via AJAX)
    path('historicos/importar_action/', views.importar_historico_action, name='importar_historico_action'),
    
    # URL para a página de consulta/listagem de históricos (geral)
    path('historicos/consultar/', views.consultar_historicos, name='consultar_historicos'),
    
    # URL para a página de detalhes de um histórico específico
    path('historicos/detalhe/<int:pk>/', views.consultar_historico_detalhe, name='consultar_historico_detalhe'),
    
    # URL para excluir um histórico (ação POST)
    path('historicos/excluir/<int:pk>/', views.excluir_historico, name='excluir_historico'),
    
    # URLs para editar histórico e consultar análise IA (implementações futuras)
    # path('historicos/editar/<int:pk>/', views.editar_historico, name='editar_historico'),
    # path('historicos/analise/<int:pk>/', views.consultar_analise_ia, name='consultar_analise_ia'),
]