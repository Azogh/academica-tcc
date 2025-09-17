from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, MatrizCurricular


class CoordenadorCadastroForm(forms.ModelForm):
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirme a Senha', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'gestao_inicio', 'portaria', 'password']
        
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('As senhas não coincidem.')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
    
    # Formulário de Cadastro de Coordenador
class CoordenadorCadastroForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('gestao_inicio', 'portaria',)

# Formulário para Matriz Curricular
class MatrizCurricularForm(forms.ModelForm):
    class Meta:
        model = MatrizCurricular
        fields = ['nome', 'curso', 'ch_total', 'estagio', 'acc', 'ano_referencia']