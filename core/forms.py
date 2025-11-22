from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, MatrizCurricular, Disciplinas, Turma, Horario

# ====================================================================
# Formulários de Usuário (COORDENADOR)
# ====================================================================

class CoordenadorCadastroForm(UserCreationForm):
    """
    Formulário para cadastro de novos coordenadores.
    """
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'gestao_inicio', 'portaria')
        
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail Institucional',
            'gestao_inicio': 'Início da Gestão',
            'portaria': 'Número da Portaria'
        }

        widgets = {
            'gestao_inicio': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'  
            }),
            'portaria': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: 12345/2023',
                'maxlength': '15' 
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: João'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: da Silva'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: joao.silva@instituicao.edu.br'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['username'].widget.attrs['placeholder'] = 'Digite o usuário para login'
        
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

# ====================================================================
# Formulários de Estrutura Curricular
# ====================================================================

class MatrizCurricularForm(forms.ModelForm):
    class Meta:
        model = MatrizCurricular
        fields = ['nome', 'curso', 'ch_total', 'estagio', 'acc', 'ano_referencia']
        
        labels = {
            'ch_total': 'Carga Horária Total',
            'acc': 'Horas de Atividades Complementares (ACC)',
            'estagio': 'Horas de Estágio Obrigatório'
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: Bacharelado em Sistemas de Informação - 2023'
            }),
            
            # --- CORREÇÃO APLICADA AQUI: Select em vez de TextInput ---
            'curso': forms.Select(attrs={
                'class': 'form-control'
            }),
            # ----------------------------------------------------------
            
            'ch_total': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: 3200'
            }),
            'estagio': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: 300'
            }),
            'acc': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: 100'
            }),
            'ano_referencia': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ex: 2023'
            }),
        }

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplinas
        fields = ['nome', 'sigla', 'ch', 'semestre', 'codigo', 'matriz_curricular', 'pre_requisitos']
        
        labels = {
            'ch': 'Carga Horária',
            'matriz_curricular': 'Matriz Pertencente'
        }
        
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Programação Orientada a Objetos'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: POO-I'}),
            'ch': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 60'}),
            'semestre': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: INF001'}),
            'matriz_curricular': forms.Select(attrs={'class': 'form-control'}),
            'pre_requisitos': forms.SelectMultiple(attrs={'class': 'form-control select2', 'data-placeholder': 'Selecione pré-requisitos...'}),
        }

# ====================================================================
# Formulários de Oferta (Turmas e Horários)
# ====================================================================

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['nome', 'ano_ingresso']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Turma 2024/1 - Noturno'}),
            'ano_ingresso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2024'}),
        }

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['turma', 'disciplina', 'dia_semana', 'periodo']
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-control'}),
            'disciplina': forms.Select(attrs={'class': 'form-control'}),
            'dia_semana': forms.Select(attrs={'class': 'form-control'}),
            'periodo': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        """
        Validação customizada para impedir choque de horários na mesma turma.
        """
        cleaned_data = super().clean()
        turma = cleaned_data.get('turma')
        dia_semana = cleaned_data.get('dia_semana')
        periodo = cleaned_data.get('periodo')
        
        # Se os campos básicos foram preenchidos, verifica conflito
        if turma and dia_semana and periodo:
            # Busca se já existe algum horário para essa turma, nesse dia e período
            # O .exclude(pk=self.instance.pk) é importante para permitir a EDIÇÃO do próprio registro sem dar erro
            conflito = Horario.objects.filter(
                turma=turma, 
                dia_semana=dia_semana, 
                periodo=periodo
            ).exclude(pk=self.instance.pk).first()

            if conflito:
                # Aqui Mensagem de erro
                raise forms.ValidationError(
                    f"Conflito de Horário! A disciplina '{conflito.disciplina.nome}' já está cadastrada para a turma {turma.nome} neste dia e período."
                )
        
        return cleaned_data