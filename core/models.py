from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo USUARIO (Tabela USUARIO)
class Usuario(AbstractUser):
    gestao_inicio = models.DateField(null=True, blank=True)
    portaria = models.CharField(max_length=15, null=True, blank=True)

    # Adicione estes argumentos para resolver o conflito de nomes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_usuarios', 
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='core_usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_usuarios', 
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='core_usuario',
    )
    
    class Meta:
        db_table = 'USUARIO'
    
    def __str__(self):
        return self.username

# Modelo ALUNO (Tabela ALUNO)
class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=10)
    ano_ingresso = models.CharField(max_length=6)
    
    class Meta:
        db_table = 'ALUNO'

    def __str__(self):
        return self.nome

# Modelo MATRIZ_CURRICULAR (Tabela MATRIZ_CURRICULAR)
class MatrizCurricular(models.Model):
    
    nome = models.CharField(max_length=45)
    curso = models.CharField(max_length=100)
    ch_total = models.IntegerField()
    estagio = models.IntegerField(null=True, blank=True)
    acc = models.IntegerField()
    ano_referencia = models.IntegerField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'MATRIZ_CURRICULAR'

    def __str__(self):
        return self.nome

# Modelo DISCIPLINAS (Tabela DISCIPLINAS)
class Disciplinas(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10)
    ch = models.IntegerField()
    semestre = models.PositiveSmallIntegerField() # tinyint
    codigo = models.CharField(max_length=10)
    matriz_curricular = models.ForeignKey(MatrizCurricular, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'DISCIPLINAS'

    def __str__(self):
        return self.nome

# Modelo HISTORICO (Tabela HISTORICO)
class Historico(models.Model):
    STATUS_CHOICES = [
        
        ('APR', 'Aprovado'),
        ('CANC', 'Cancelado'),
        ('CUMP', 'Cumpriu'),
        ('DISP', 'Dispensado'),
        ('MATR', 'Matriculado'),
        ('REP', 'Reprovado por média'),
        ('REPF', 'Reprovado por falta'),
        ('REPMF', 'Reprovado por média e falta'),
        ('TRANC', 'Matrícula trancada'),
    ]
    
    status = models.CharField(max_length=5, choices=STATUS_CHOICES)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'HISTORICO'
        verbose_name_plural = 'Históricos'

    def __str__(self):
        return f"{self.aluno.nome} - {self.disciplina.nome} ({self.status})"

# Modelo AJUSTE (Tabela AJUSTE)
class Ajuste(models.Model):
    data_emissao = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'AJUSTE'

    def __str__(self):
        return f"Ajuste de {self.aluno.nome} - {self.data_emissao.strftime('%Y-%m-%d')}"

# Modelo TURMA (Tabela TURMA)
class Turma(models.Model):
    nome = models.CharField(max_length=45)
    ano_ingresso = models.IntegerField() # Usado IntegerField para YEAR
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'TURMA'

    def __str__(self):
        return self.nome

# Modelo HORARIO (Tabela HORARIO)
class Horario(models.Model):
    DIA_CHOICES = [
        ('SEG', 'Segunda-feira'),
        ('TER', 'Terça-feira'),
        ('QUA', 'Quarta-feira'),
        ('QUI', 'Quinta-feira'),
        ('SEX', 'Sexta-feira'),
    ]
    PERIODO_CHOICES = [
        ('1-2', 'Período 1 e 2'),
        ('3-4', 'Período 3 e 4'),
    ]
    dia_semana = models.CharField(max_length=3, choices=DIA_CHOICES)
    periodo = models.CharField(max_length=3, choices=PERIODO_CHOICES)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'HORARIO'
    
    def __str__(self):
        return f"Turma: {self.turma.nome} | Disciplina: {self.disciplina.sigla} | Dia: {self.dia_semana}"

# Modelo AJUSTE_ITENS (Tabela AJUSTE_ITENS)
# Esta é uma tabela de relacionamento N:M (muitos para muitos) entre AJUSTE e DISCIPLINAS.
class AjusteItens(models.Model):
    # A chave composta é definida pela combinação das chaves estrangeiras.
    ajuste = models.ForeignKey(Ajuste, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE)
    dia_semana = models.CharField(max_length=3)
    periodo = models.CharField(max_length=3)
    
    class Meta:
        db_table = 'AJUSTE_ITENS'
        # Define a chave primária composta
        unique_together = ('ajuste', 'disciplina')
        verbose_name_plural = 'Ajustes de Itens'

    def __str__(self):
        return f"Item do ajuste {self.ajuste.id} - Disciplina: {self.disciplina.nome}"