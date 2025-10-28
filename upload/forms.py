from django import forms
from .models import Aluno 

# ====================================================================
# Formulário para Upload de Histórico
# ====================================================================

class HistoricoUploadForm(forms.Form):
    """
    Formulário para o coordenador inserir os dados básicos do aluno
    e fazer o upload do arquivo PDF do histórico escolar.
    """
    nome = forms.CharField(
        max_length=100, 
        label="Nome Completo do Aluno",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: João da Silva'})
    )
    matricula = forms.CharField(
        max_length=10, 
        label="Número de Matrícula",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 2023010001'})
    )
    curso = forms.CharField(
        max_length=100, 
        label="Curso de Ingresso",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Bacharelado em Sistemas de Informação'})
    )
    ano_ingresso = forms.CharField(
        max_length=6, 
        label="Ano/Semestre de Ingresso",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 2023.1'})
    )
    pdf_file = forms.FileField(
        label="Arquivo PDF do Histórico",
        help_text="Selecione o arquivo PDF.",
        # Validação para aceitar apenas PDF (opcional, mas boa prática)
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf'}) 
    )

    def clean_matricula(self):
        """
        Validação customizada para garantir que a matrícula seja única
        (embora o get_or_create na view já trate isso, é bom ter no form).
        """
        matricula = self.cleaned_data.get('matricula')
        # Verifica se já existe um aluno com essa matrícula (case-insensitive)
        # if Aluno.objects.filter(matricula__iexact=matricula).exists():
        #     raise forms.ValidationError("Já existe um aluno cadastrado com esta matrícula.")
        # Comentado pois get_or_create lida com isso. Descomente se preferir a validação aqui.
        return matricula
    
    def clean_pdf_file(self):
        """Validação para o tipo de arquivo PDF."""
        file = self.cleaned_data.get('pdf_file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("O arquivo deve ser do tipo PDF.")
            # Você pode adicionar outras validações aqui (tamanho, etc.)
        return file