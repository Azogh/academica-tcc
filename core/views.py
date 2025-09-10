# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CoordenadorCadastroForm

def autocadastro_coordenador(request):
    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Opcional: Logar o usuário automaticamente após o cadastro
            login(request, user)
            return redirect('home')  # Redireciona para a página home
    else:
        form = CoordenadorCadastroForm()
    
    return render(request, 'core/autocadastro.html', {'form': form})