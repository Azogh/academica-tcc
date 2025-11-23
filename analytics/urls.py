from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # 1. A página do formulário
    path('analisar/<int:historico_pk>/', views.analisar_historico, name='analisar_historico'),
    
    # 2. A página de resultado (grade)
    path('resultado/<int:analise_pk>/', views.consultar_analise, name='consultar_analise'),
    
    # 3. A página de edição da grade
    path('editar/<int:analise_pk>/', views.editar_analise, name='editar_analise'),
    
    # --- NOVAS URLS ADICIONADAS ---
    
    # 4. A nova página de listagem
    path('listar/', views.listar_analises, name='listar_analises'),
    
    # 5. Ação de excluir
    path('excluir/<int:analise_pk>/', views.excluir_analise, name='excluir_analise'),
    path('imprimir-solicitacao/<int:analise_id>/', views.gerar_pdf_solicitacao, name='imprimir_solicitacao'),
]