from django.urls import path
from . import views

# Define o namespace para esta aplicação
app_name = 'upload'

urlpatterns = [
    # URL principal: Faz o upload, processa e lista (Tudo em um)
    path('historicos/', views.importar_historico, name='importar_historico'),
    
    # --- REMOVIDO: A rota 'importar_action' não existe mais, pois foi integrada acima ---
    # path('historicos/importar_action/', views.importar_historico_action, ...),
    
    # URL para a página de consulta/listagem de históricos (geral)
    path('historicos/consultar/', views.consultar_historicos, name='consultar_historicos'),
    
    # URL para a página de detalhes de um histórico específico
    path('historicos/detalhe/<int:pk>/', views.consultar_historico_detalhe, name='consultar_historico_detalhe'),
    
    # URL para excluir um histórico (ação POST)
    path('historicos/excluir/<int:pk>/', views.excluir_historico, name='excluir_historico'),
]