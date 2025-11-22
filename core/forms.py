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
    # --- Campos Extras (Lógica de Interface) ---
    CREDITOS_CHOICES = [
        ('2', '2 Créditos (1 Encontro Semanal)'),
        ('4', '4 Créditos (2 Encontros Semanais)'),
    ]
    
    creditos = forms.ChoiceField(
        choices=CREDITOS_CHOICES, 
        widget=forms.RadioSelect, 
        initial='2',
        label="Carga Horária da Oferta"
    )
    
    # Campos para o Segundo Horário (opcionais na validação padrão, obrigatórios se 4 créditos)
    dia_semana_2 = forms.ChoiceField(
        choices=Horario.DIA_CHOICES, 
        required=False, 
        label="Dia da Semana (2º Encontro)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    periodo_2 = forms.ChoiceField(
        choices=Horario.PERIODO_CHOICES, 
        required=False, 
        label="Período (2º Encontro)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

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
        cleaned_data = super().clean()
        turma = cleaned_data.get('turma')
        creditos = cleaned_data.get('creditos')
        
        # --- Validação do Horário 1 (Padrão) ---
        dia1 = cleaned_data.get('dia_semana')
        per1 = cleaned_data.get('periodo')
        
        if turma and dia1 and per1:
            # Verifica conflito no horário 1 (excluindo o próprio se for edição)
            conflito1 = Horario.objects.filter(turma=turma, dia_semana=dia1, periodo=per1)
            if self.instance.pk:
                conflito1 = conflito1.exclude(pk=self.instance.pk)
            
            conflito1 = conflito1.first()
            
            if conflito1:
                self.add_error('dia_semana', f"Conflito! A disciplina '{conflito1.disciplina}' já ocupa {dia1} {per1}.")

        # --- Validação do Horário 2 (Se for 4 créditos) ---
        if creditos == '4':
            dia2 = cleaned_data.get('dia_semana_2')
            per2 = cleaned_data.get('periodo_2')

            # 1. Verifica se preencheu
            if not dia2 or not per2:
                raise forms.ValidationError("Para 4 créditos, você DEVE informar o dia e período do 2º encontro.")
            
            # 2. Verifica se é igual ao primeiro (não faz sentido)
            if dia1 == dia2 and per1 == per2:
                raise forms.ValidationError("O 2º encontro não pode ser no mesmo horário do 1º.")

            # 3. Verifica conflito no banco para o horário 2
            conflito2 = Horario.objects.filter(turma=turma, dia_semana=dia2, periodo=per2).first()
            if conflito2:
                self.add_error('dia_semana_2', f"Conflito no 2º Horário! A disciplina '{conflito2.disciplina}' já ocupa {dia2} {per2}.")

        return cleaned_data