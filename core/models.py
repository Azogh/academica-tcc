from django.db import models
from django.contrib.auth.models import AbstractUser

# ====================================================================
# Modelos de Usuário (Autenticação e Permissão)
# ====================================================================

class Usuario(AbstractUser):
    """
    Modelo customizado que estende o AbstractUser do Django para 
    adicionar campos específicos do coordenador, como início de gestão e portaria.
    Este modelo é central para a autenticação no sistema.
    """
    gestao_inicio = models.DateField(
        null=True, 
        blank=True,
        verbose_name="Início da Gestão"
    )
    portaria = models.CharField(
        max_length=15, 
        null=True, 
        blank=True,
        verbose_name="Número da Portaria"
    )

    # Sobrescrita para evitar conflitos de nomeação em projetos maiores
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_usuarios', 
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_query_name='core_usuario',
        verbose_name="Grupos de Usuário"
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_usuarios', 
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='core_usuario',
        verbose_name="Permissões de Usuário"
    )
    
    class Meta:
        # Define o nome da tabela no banco de dados
        db_table = 'USUARIO'
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    
    def __str__(self):
        """Retorna o nome de usuário (username) como representação do objeto."""
        return self.username

# ATENÇÃO: Os modelos Aluno, Historico, Ajuste e AjusteItens foram removidos
# desta aplicação e movidos para 'upload/models.py' para resolver o conflito
# de db_table e modularizar o projeto.

# ====================================================================
# Modelos de Estrutura Curricular (Domínio: Matrizes e Disciplinas)
# ====================================================================

class MatrizCurricular(models.Model):
    """
    Define a estrutura curricular de um curso específico.
    """
    nome = models.CharField(max_length=45, verbose_name="Nome da Matriz")
    curso = models.CharField(max_length=100, verbose_name="Curso")
    ch_total = models.IntegerField(verbose_name="Carga Horária Total")
    estagio = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Carga Horária Estágio"
    )
    acc = models.IntegerField(verbose_name="Carga Horária ACC")
    ano_referencia = models.IntegerField(verbose_name="Ano de Referência")
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        verbose_name="Criado por"
    )
    
    class Meta:
        db_table = 'MATRIZ_CURRICULAR'
        verbose_name = "Matriz Curricular"
        verbose_name_plural = "Matrizes Curriculares"

    def __str__(self):
        """Retorna o nome da matriz e o ano de referência."""
        return f"{self.nome} ({self.ano_referencia})"

# Em: academica-tcc/core/models.py

class Disciplinas(models.Model):
    """
    Lista de disciplinas vinculadas a uma Matriz Curricular.
    """
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10)
    ch = models.IntegerField(verbose_name="Carga Horária")
    semestre = models.PositiveSmallIntegerField()
    codigo = models.CharField(max_length=10)
    matriz_curricular = models.ForeignKey(
        MatrizCurricular, 
        on_delete=models.CASCADE,
        verbose_name="Matriz Curricular"
    )
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        verbose_name="Criado por"
    )
    
    # 👇👇👇 ADICIONE ESTE CAMPO NOVO 👇👇👇
    pre_requisitos = models.ManyToManyField(
        'self', 
        symmetrical=False, 
        blank=True, 
        verbose_name="Pré-requisitos"
    )
    # 👆👆👆 FIM DO CAMPO NOVO 👆👆👆
    
    class Meta:
        db_table = 'DISCIPLINAS'
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

    def __str__(self):
        """Retorna o nome da disciplina."""
        return self.nome
    
# ====================================================================
# Modelos de Oferta e Horários (Domínio: Turmas e Grade)
# ====================================================================

class Turma(models.Model):
    """
    Representa uma Turma específica (ex: SI 2025/1) no sistema.
    """
    nome = models.CharField(max_length=45)
    ano_ingresso = models.IntegerField(verbose_name="Ano de Ingresso")
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        verbose_name="Criado por"
    )
    
    class Meta:
        db_table = 'TURMA'
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"

    def __str__(self):
        """Retorna o nome da turma."""
        return self.nome

class Horario(models.Model):
    """
    Define o horário e o dia em que uma Disciplina será ofertada por uma Turma.
    """
    # Definição de Escolhas
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
    
    dia_semana = models.CharField(max_length=3, choices=DIA_CHOICES, verbose_name="Dia da Semana")
    periodo = models.CharField(max_length=3, choices=PERIODO_CHOICES, verbose_name="Período")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplinas, on_delete=models.CASCADE, verbose_name="Disciplina")
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE,
        verbose_name="Criado por"
    )
    
    class Meta:
        db_table = 'HORARIO'
        # Adiciona restrições de unicidade para evitar sobreposição (boa prática)
        unique_together = ('turma', 'dia_semana', 'periodo', 'disciplina') 
        verbose_name = "Horário"
        verbose_name_plural = "Horários"
    
    def __str__(self):
        """Retorna a descrição completa do horário."""
        return f"Turma: {self.turma.nome} | Disciplina: {self.disciplina.sigla} | Dia: {self.dia_semana}"

