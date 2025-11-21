from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, MatrizCurricular, Disciplinas, Turma, Horario

# ====================================================================
# Formulários de Usuário
# ====================================================================

class CoordenadorCadastroForm(UserCreationForm):
    """
    Formulário para cadastro de novos coordenadores (Usuários).
    Herda de UserCreationForm para tratar senhas e criptografia automaticamente.
    """
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # Campos que aparecerão no formulário HTML
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'gestao_inicio', 'portaria')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Torna campos de nome e email obrigatórios para coordenadores
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

# ====================================================================
# Formulários de Estrutura Curricular
# ====================================================================

class MatrizCurricularForm(forms.ModelForm):
    """Formulário para Criar/Editar Matrizes Curriculares."""
    class Meta:
        model = MatrizCurricular
        fields = ['nome', 'curso', 'ch_total', 'estagio', 'acc', 'ano_referencia']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Sistemas de Informação 2023'}),
            'curso': forms.TextInput(attrs={'class': 'form-control'}),
            'ch_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'estagio': forms.NumberInput(attrs={'class': 'form-control'}),
            'acc': forms.NumberInput(attrs={'class': 'form-control'}),
            'ano_referencia': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2023'}),
        }

class DisciplinaForm(forms.ModelForm):
    """Formulário para Criar/Editar Disciplinas."""
    class Meta:
        model = Disciplinas
        fields = ['nome', 'sigla', 'ch', 'semestre', 'codigo', 'matriz_curricular', 'pre_requisitos']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control'}),
            'ch': forms.NumberInput(attrs={'class': 'form-control'}),
            'semestre': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'matriz_curricular': forms.Select(attrs={'class': 'form-control'}),
            'pre_requisitos': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }

# ====================================================================
# Formulários de Oferta (Turmas e Horários)
# ====================================================================

class TurmaForm(forms.ModelForm):
    """Formulário para Criar/Editar Turmas."""
    class Meta:
        model = Turma
        fields = ['nome', 'ano_ingresso']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: SI 2024/1'}),
            'ano_ingresso': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class HorarioForm(forms.ModelForm):
    """Formulário para Criar/Editar Horários."""
    class Meta:
        model = Horario
        fields = ['turma', 'disciplina', 'dia_semana', 'periodo']
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-control'}),
            'disciplina': forms.Select(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'periodo': forms.Select(attrs={'class': 'form-control'}),
        }