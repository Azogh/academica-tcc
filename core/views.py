from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CoordenadorCadastroForm
from django.contrib.auth.decorators import login_required

def autocadastro_coordenador(request):
    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Opcional: Logar o usuário automaticamente após o cadastro
            login(request, user)
            return redirect('login')  # Redireciona para a página login
    else:
        form = CoordenadorCadastroForm()
    
    return render(request, 'core/autocadastro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('painel') # Redireciona para a página inicial após o login
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

@login_required
def painel_coordenador(request):
    return render(request, 'core/painel.html', {})

def landing_page(request):
    return render(request, 'core/landing_page.html', {})

