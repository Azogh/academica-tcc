from django import forms
# Não precisamos mais importar os modelos do core
# from core.models import MatrizCurricular 

# -------------------------------------------------------------------
# LISTA DE CURSOS FIXA (HARDCODED)
# -------------------------------------------------------------------
# Como você mencionou, aqui fica a lista de cursos do seu campus
# Adicione ou remova os cursos que precisar
CURSO_CHOICES = [
    ('', 'Selecione um curso'), # Este é o "placeholder"
    ('LICENCIATURA EM MATEMÁTICA', 'Licenciatura em Matemática'),
    ('LICENCIATURA EM FÍSICA', 'Licenciatura em Física'),
    ('TECNÓLOGO EM GASTRONOMIA', 'Tecnólogo em Gastronomia'),
    ('BACHARELADO EM SISTEMAS DE INFORMAÇÃO', 'Bacharelado em Sistemas de Informação'),
    ('TECNÓLOGO EM GESTÃO DE TURISMO', 'Tecnólogo em Gestão de Turismo'),
    # Adicione os outros cursos aqui...
]

# -------------------------------------------------------------------
# SEU FORMULÁRIO MODIFICADO
# -------------------------------------------------------------------
class HistoricoUploadForm(forms.Form):
    # Campos do Aluno
    nome = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'placeholder': 'Nome completo do Aluno', 'class': 'form-control'})
    )
    matricula = forms.CharField(
        max_length=10, 
        widget=forms.TextInput(attrs={'placeholder': 'Nº da Matrícula', 'class': 'form-control'})
    )
    
    # --- CAMPO MODIFICADO ---
    # Agora usa a lista de cursos fixa
    curso = forms.ChoiceField(
        choices=CURSO_CHOICES, # Usa a lista estática que definimos acima
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    # -------------------------

    ano_ingresso = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 2019.1', 'class': 'form-control'})
    )
    
    # Campo do Arquivo
    pdf_file = forms.FileField(
        label="Arquivo PDF do Histórico",
        widget=forms.FileInput(attrs={'class': 'form-control'})
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