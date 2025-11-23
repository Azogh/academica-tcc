from django.db import models
# IMPORTANTE: Precisamos importar o 'Curso' aqui para usá-lo abaixo
from core.models import Usuario, Curso 

# ====================================================================
# Modelos de Aluno e Histórico
# ====================================================================

class Aluno(models.Model):
    """
    Representa o registro básico de um Aluno na instituição. 
    """
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10, unique=True)
    
    # Aqui usamos a classe 'Curso' que importamos lá em cima
    curso = models.ForeignKey(
        Curso, 
        on_delete=models.CASCADE, 
        verbose_name="Curso de Ingresso"
    )
    
    ano_ingresso = models.CharField(max_length=6, verbose_name="Ano de Ingresso")
    
    class Meta:
        db_table = 'ALUNO'
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self):
        return f"{self.nome} ({self.matricula})"

class Historico(models.Model):
    """
    Representa o registro de um Histórico Escolar importado e processado.
    """
    STATUS_CHOICES = [
        ('PENDENTE', 'Processamento Pendente'),
        ('CONCLUIDO', 'Processamento Concluído'),
        ('ERRO', 'Erro no Processamento'),
    ]
    
    aluno = models.ForeignKey(
        Aluno, 
        on_delete=models.CASCADE, 
        verbose_name="Aluno",
        related_name='historicos'
    )
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Coordenador Responsável"
    )
    data_upload = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Data de Upload"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDENTE',
        verbose_name="Status de Processamento"
    )
    arquivo_original = models.FileField(
        upload_to='historicos/', 
        null=True, 
        blank=True,
        verbose_name="Arquivo PDF Original"
    )
    
    class Meta:
        db_table = 'HISTORICO'
        verbose_name = "Histórico Escolar"
        verbose_name_plural = "Históricos Escolares"
        
    def __str__(self):
        return f"Histórico de {self.aluno.nome} - {self.status}"

class HistoricoItens(models.Model):
    """
    Detalha as disciplinas contidas no Histórico Escolar (linhas do PDF).
    """
    historico = models.ForeignKey(
        Historico, 
        on_delete=models.CASCADE,
        verbose_name="Histórico",
        related_name='itens'
    )
    disciplina_nome = models.CharField(max_length=200, verbose_name="Nome da Disciplina")
    disciplina_sigla = models.CharField(max_length=10, verbose_name="Sigla")
    ch = models.IntegerField(verbose_name="Carga Horária")
    nota = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    frequencia = models.IntegerField(null=True, blank=True, verbose_name="Frequência (%)")
    status_disciplina = models.CharField(max_length=50, verbose_name="Situação") 
    semestre_cursado = models.CharField(max_length=10, verbose_name="Semestre Cursado")

    class Meta:
        db_table = 'HISTORICO_ITENS'
        verbose_name = "Item de Histórico"
        verbose_name_plural = "Itens de Histórico"

    def __str__(self):
        return self.disciplina_nome