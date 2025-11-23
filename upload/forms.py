from django import forms
from core.models import Curso
from .models import Aluno, Historico

class UploadHistoricoForm(forms.ModelForm):
    """
    Formulário unificado: Cria/Atualiza o Aluno e recebe o PDF.
    """
    nome = forms.CharField(
        label="Nome do Aluno",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'})
    )
    matricula = forms.CharField(
        label="Matrícula",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 20231001', 'maxlength': '10'})
    )
    
    # Dropdown dinâmico ligado ao banco de dados
    curso = forms.ModelChoiceField(
        queryset=Curso.objects.all().order_by('nome'),
        label="Curso",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Selecione o Curso..."
    )

    ano_ingresso = forms.CharField(
        label="Ano de Ingresso",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2023'})
    )
    
    # Campo de Arquivo (Processado manualmente na View)
    arquivo = forms.FileField(
        label="Arquivo PDF do Histórico",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'})
    )

    class Meta:
        model = Aluno
        fields = ['nome', 'matricula', 'curso', 'ano_ingresso']

    def clean_matricula(self):
        return self.cleaned_data['matricula'].strip()

    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            if not arquivo.name.lower().endswith('.pdf'):
                raise forms.ValidationError("O arquivo deve ser um PDF.")
        return arquivo