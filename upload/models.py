from django.db import models
# Importamos o modelo de usuário da aplicação 'core'
from core.models import Usuario 

# ====================================================================
# Modelos de Aluno e Histórico
# ====================================================================

class Aluno(models.Model):
    """
    Representa o registro básico de um Aluno na instituição. 
    Este modelo é preenchido manualmente e com o upload do histórico.
    """
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10, unique=True)
    curso = models.CharField(max_length=100, verbose_name="Curso de Ingresso")
    # Campo adicionado para preenchimento manual no formulário
    ano_ingresso = models.CharField(max_length=6, verbose_name="Ano de Ingresso")
    
    class Meta:
        db_table = 'ALUNO'
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"

    def __str__(self):
        """Retorna o nome e a matrícula do aluno."""
        return f"{self.nome} ({self.matricula})"

class Historico(models.Model):
    """
    Representa o registro de um Histórico Escolar importado e processado.
    """
    # Constantes para status de processamento (Boas Práticas)
    STATUS_CHOICES = [
        ('PENDENTE', 'Processamento Pendente'),
        ('CONCLUIDO', 'Processamento Concluído'),
        ('ERRO', 'Erro no Processamento'),
    ]
    
    aluno = models.ForeignKey(
        Aluno, 
        on_delete=models.CASCADE, 
        verbose_name="Aluno",
        related_name='historicos' # Permite consultar facilmente historicos do aluno
    )
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, # Mantém o histórico mesmo que o coordenador seja excluído
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
    # Campo para armazenar o caminho do arquivo (opcional, útil para debug)
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
        # Garante que um aluno tenha apenas um histórico 'CONCLUIDO' de cada vez (opcional, mas útil)
        # unique_together = ('aluno', 'status') 
        
    def __str__(self):
        """Retorna a descrição do histórico."""
        return f"Histórico de {self.aluno.nome} - {self.status}"

class HistoricoItens(models.Model):
    """
    Detalha as disciplinas contidas no Histórico Escolar (as linhas lidas do PDF).
    """
    historico = models.ForeignKey(
        Historico, 
        on_delete=models.CASCADE,
        verbose_name="Histórico",
        related_name='itens'
    )
    # Dados da disciplina conforme o PDF
    disciplina_nome = models.CharField(max_length=200, verbose_name="Nome da Disciplina")
    disciplina_sigla = models.CharField(max_length=10, verbose_name="Sigla")
    ch = models.IntegerField(verbose_name="Carga Horária")
    nota = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    frequencia = models.IntegerField(null=True, blank=True, verbose_name="Frequência (%)")
    status_disciplina = models.CharField(max_length=50, verbose_name="Situação") # Ex: APROVADO, REPROVADO, CANCELADO
    semestre_cursado = models.CharField(max_length=10, verbose_name="Semestre Cursado") # Ex: 2021.1

    class Meta:
        db_table = 'HISTORICO_ITENS'
        verbose_name = "Item de Histórico"
        verbose_name_plural = "Itens de Histórico"

    def __str__(self):
        """Retorna o nome da disciplina no histórico."""
        return self.disciplina_nome