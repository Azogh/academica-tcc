from django.contrib import admin
from .models import Aluno, Historico, HistoricoItens

# ====================================================================
# Configuração para o Admin Django
# ====================================================================

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    """Configuração de exibição para o modelo Aluno."""
    list_display = ('nome', 'matricula', 'curso', 'ano_ingresso')
    search_fields = ('nome', 'matricula', 'curso')
    list_filter = ('curso', 'ano_ingresso')
    ordering = ('nome',)

@admin.register(Historico)
class HistoricoAdmin(admin.ModelAdmin):
    """Configuração de exibição para o modelo Historico."""
    # Define a ordem de exibição na lista
    list_display = ('aluno_nome', 'status', 'data_upload', 'usuario')
    search_fields = ('aluno__nome', 'aluno__matricula', 'status')
    list_filter = ('status', 'usuario', 'data_upload')
    date_hierarchy = 'data_upload'
    ordering = ('-data_upload',)
    
    # Define como buscar o nome do aluno no related_field
    @admin.display(description='Aluno')
    def aluno_nome(self, obj):
        return obj.aluno.nome

@admin.register(HistoricoItens)
class HistoricoItensAdmin(admin.ModelAdmin):
    """Configuração de exibição para o modelo HistoricoItens."""
    list_display = ('historico_aluno', 'disciplina_nome', 'disciplina_sigla', 'status_disciplina', 'semestre_cursado')
    search_fields = ('historico__aluno__nome', 'disciplina_nome', 'disciplina_sigla')
    list_filter = ('status_disciplina', 'semestre_cursado')
    
    # Define como buscar o nome do aluno relacionado ao item de histórico
    @admin.display(description='Aluno')
    def historico_aluno(self, obj):
        return obj.historico.aluno.nome
