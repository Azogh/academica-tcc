from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# Importamos apenas os modelos que permanecem neste módulo
from .models import (
    Usuario, MatrizCurricular, Disciplinas, Turma, Horario
)

# ====================================================================
# Constantes de Escolha (Boas Práticas: Mover para um arquivo 'choices.py' na V2)
# ====================================================================

# Lista de cursos do IFFar - São Borja
CURSO_CHOICES = [
        ('', 'Selecione um curso'), # Este é o "placeholder"
    ('LICENCIATURA EM MATEMÁTICA', 'Licenciatura em Matemática'),
    ('LICENCIATURA EM FÍSICA', 'Licenciatura em Física'),
    ('TECNÓLOGO EM GASTRONOMIA', 'Tecnólogo em Gastronomia'),
    ('BACHARELADO EM SISTEMAS DE INFORMAÇÃO', 'Bacharelado em Sistemas de Informação'),
    ('TECNÓLOGO EM GESTÃO DE TURISMO', 'Tecnólogo em Gestão de Turismo'),
]

# ====================================================================
# Formulários de Autenticação
# ====================================================================

class CoordenadorCadastroForm(UserCreationForm):
    """
    Formulário de criação de usuário para o Coordenador.
    Estende o UserCreationForm do Django e adiciona campos específicos do modelo Usuario.
    """

    gestao_inicio = forms.IntegerField(
        label="Gestão Início (Ano)",
        required=False,
        min_value=1900,
        max_value=2100,
        widget=forms.NumberInput(attrs={'placeholder': 'Ex: 2025'}),
        help_text="O ano em que o Coordenador iniciou a gestão do curso."
    )
    
    # Sobrescrita do campo 'username' apenas para tradução do label
    username = forms.CharField(label="Nome de Usuário") 
    
    # Sobrescrita dos campos de senha para tradução dos labels
    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        help_text=UserCreationForm.base_fields['password2'].help_text
    )
    password2 = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput,
        help_text=UserCreationForm.base_fields['password2'].help_text
    )
    
    class Meta(UserCreationForm.Meta):
        """Metadados do formulário de cadastro."""
        model = Usuario
        # Inclui os campos customizados 'gestao_inicio' e 'portaria'
        fields = UserCreationForm.Meta.fields + ('gestao_inicio', 'portaria',)

# O formulário de login (AuthenticationForm) é importado diretamente do Django
# pois o padrão é suficiente para a view 'login_view'.

# ====================================================================
# Formulários de Gestão Acadêmica (CRUD)
# ====================================================================

class MatrizCurricularForm(forms.ModelForm):
    """
    Formulário para o CRUD de Matriz Curricular.
    Usa ModelForm para facilitar a criação/edição.
    """
    # Sobrescreve 'curso' para usar uma lista fixa de opções (CURSO_CHOICES)
    curso = forms.ChoiceField(choices=CURSO_CHOICES, label='Curso')
    
    class Meta:
        model = MatrizCurricular
        fields = ['nome', 'curso', 'ch_total', 'estagio', 'acc', 'ano_referencia']
        labels = {
            'nome': 'Nome da Matriz (Ex: SI 2021)',
            'ch_total': 'Carga Horária Total (h)',
            'estagio': 'Carga Horária Estágio (h)',
            'acc': 'Carga Horária ACC (h)',
            'ano_referencia': 'Ano de Referência',
        }

class DisciplinaForm(forms.ModelForm):
    """
    Formulário para o CRUD de Disciplinas.
    """
    # Usa ModelChoiceField para selecionar Matriz Curricular (Foreign Key)
    matriz_curricular = forms.ModelChoiceField(
        queryset=MatrizCurricular.objects.all(), 
        empty_label="Selecione a Matriz Curricular",
        label="Matriz Curricular"
    )
    
    class Meta:
        model = Disciplinas
        fields = ['nome', 'sigla', 'ch', 'semestre', 'codigo', 'matriz_curricular']
        labels = {
            'ch': 'Carga Horária (h)',
            'semestre': 'Semestre Ideal',
            'codigo': 'Código SIGAA',
        }

class TurmaForm(forms.ModelForm):
    """
    Formulário para o CRUD de Turmas.
    """
    class Meta:
        model = Turma
        fields = ['nome', 'ano_ingresso']
        labels = {
            'nome': 'Nome da Turma (Ex: T415)',
            'ano_ingresso': 'Ano de Ingresso',
        }

class HorarioForm(forms.ModelForm):
    """
    Formulário para o CRUD de Horários.
    Usa as constantes de escolha definidas no model Horario.
    """
    class Meta:
        model = Horario
        fields = ['dia_semana', 'periodo', 'turma', 'disciplina']
        labels = {
            'dia_semana': 'Dia da Semana',
            'periodo': 'Período (Ex: 1-2 ou 3-4)',
        }

<<<<<<< HEAD
# O formulário HistoricoUploadForm foi removido deste arquivo e transferido 
# para 'upload/forms.py', respeitando a modularização.
=======
# Formulário para Upload de Histórico
class HistoricoUploadForm(forms.Form):
    # Campos de texto para dados do aluno
    nome_aluno = forms.CharField(label='Nome Completo', max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Nome do estudante'}))
    matricula = forms.CharField(label='Matrícula', max_length=10, required=True, widget=forms.TextInput(attrs={'placeholder': 'Número da matrícula'}))
    
    # Campo de seleção para Curso (usando a lista existente)
    curso = forms.ChoiceField(choices=[('', 'Selecione o Curso')] + CURSO_CHOICES, label='Curso', required=True)
    
    # Campo de arquivo para o PDF
    pdf_file = forms.FileField(
        label='Escolher Arquivo PDF', 
        required=True, 
        widget=forms.FileInput(attrs={'style': 'display: none;'})
    )
    
>>>>>>> 928ea7b5e7244cd38faaea9f4c500a753caba395
