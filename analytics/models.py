from django.db import models
# 👇 CORRIGIDO AQUI: Importando 'Disciplinas' (plural)
from core.models import Usuario, Disciplinas
from upload.models import Historico

class Analise(models.Model):
    """
    Armazena o cabeçalho de uma análise gerada.
    Ex: "Análise 'Hardcore' para João da Silva"
    """
    TIPO_ANALISE_CHOICES = [
        ('padrao', 'Padrão'),
        ('soft', 'Soft'),
        ('hard', 'Hardcore'),
    ]
    
    # Link para o histórico original que foi analisado
    historico = models.ForeignKey(Historico, on_delete=models.CASCADE, related_name='analises')
    
    # Quem gerou a análise
    coordenador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Opções que foram usadas
    tipo_analise = models.CharField(max_length=10, choices=TIPO_ANALISE_CHOICES)
    dias_excluidos = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: 'SEG,TER'")
    
    # Status
    data_criacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='PENDENTE') # PENDENTE, CONCLUIDO, ERRO
    
    # O resultado da IA (o texto/resumo, se houver)
    resultado_texto = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Análise {self.get_tipo_analise_display()} para {self.historico.aluno.nome}"

# Em: academica-tcc/analytics/models.py

# ... (imports e classe Analise) ...

class AnaliseItens(models.Model):
    """
    Armazena cada disciplina *sugerida* pela IA, 
    com o horário e dia (para montar a grade).
    """
    analise = models.ForeignKey(Analise, on_delete=models.CASCADE, related_name='itens')
    
    # Apontando para 'Disciplinas' (plural)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    
    # Onde ela se encaixa (para a grade)
    dia_semana = models.CharField(max_length=3) # SEG, TER, QUA...
    
    # --- CAMPO CORRIGIDO ---
    # Trocamos TimeFields por CharField para bater com o core/models.py
    periodo = models.CharField(max_length=10) # Ex: '1-2', '3-4'
    
    def __str__(self):
        # Atualizamos o __str__ para refletir a mudança
        return f"{self.disciplina.sigla} @ {self.dia_semana} ({self.periodo})"