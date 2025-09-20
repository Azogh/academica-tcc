from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    Usuario, MatrizCurricular, Disciplinas, Aluno, Historico,
    Ajuste, Turma, Horario, AjusteItens
)

# Lista de cursos do IFFar - São Borja
CURSO_CHOICES = [
    ('LICENCIATURA EM MATEMÁTICA', 'Licenciatura em Matemática'),
    ('LICENCIATURA EM FÍSICA', 'Licenciatura em Física'),
    ('TECNÓLOGO EM GASTRONOMIA', 'Tecnólogo em Gastronomia'),
    ('BACHARELADO EM SISTEMAS DE INFORMAÇÃO', 'Bacharelado em Sistemas de Informação'),
    ('TECNÓLOGO EM GESTÃO DE TURISMO', 'Tecnólogo em Gestão de Turismo'),
]

# Formulário de Cadastro de Coordenador (versão recomendada)
class CoordenadorCadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('gestao_inicio', 'portaria',)

# Formulário para Matriz Curricular
class MatrizCurricularForm(forms.ModelForm):
    curso = forms.ChoiceField(choices=CURSO_CHOICES, label='Curso')
    
    class Meta:
        model = MatrizCurricular
        fields = ['nome', 'curso', 'ch_total', 'estagio', 'acc', 'ano_referencia']

# Formulário para Disciplina
class DisciplinaForm(forms.ModelForm):
    matriz_curricular = forms.ModelChoiceField(queryset=MatrizCurricular.objects.all(), empty_label="Selecione a Matriz Curricular")
    
    class Meta:
        model = Disciplinas
        fields = ['nome', 'sigla', 'ch', 'semestre', 'codigo', 'matriz_curricular']

# Formulário para Turma
class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'ano_ingresso']

# Formulário para Horário
class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['dia_semana', 'periodo', 'turma', 'disciplina']

# Formulário para Upload de Histórico
class HistoricoUploadForm(forms.Form):
    pdf_file = forms.FileField(label='Selecione o arquivo PDF')