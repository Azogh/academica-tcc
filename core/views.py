from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from .forms import CoordenadorCadastroForm, MatrizCurricularForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import MatrizCurricular, Disciplinas, Usuario, Aluno, Historico


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

# Views existentes de login e cadastro
def autocadastro_coordenador(request):
    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('login')
    else:
        form = CoordenadorCadastroForm()
    
    return render(request, 'core/autocadastro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('painel')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

@login_required
def painel_coordenador(request):
    return render(request, 'core/painel.html', {})

def landing_page(request):
    return render(request, 'core/landing_page.html', {})

# Views para o CRUD de Matriz Curricular
@login_required
def listar_matrizes(request):
    matrizes_list = MatrizCurricular.objects.all().order_by('-ano_referencia')
    paginator = Paginator(matrizes_list, 10)
    page = request.GET.get('page')
    try:
        matrizes = paginator.page(page)
    except PageNotAnInteger:
        matrizes = paginator.page(1)
    except EmptyPage:
        matrizes = paginator.page(paginator.num_pages)
    
    return render(request, 'core/listar_matrizes.html', {'matrizes': matrizes})

@login_required
def adicionar_matriz(request):
    if request.method == 'POST':
        form = MatrizCurricularForm(request.POST)
        if form.is_valid():
            matriz = form.save(commit=False)
            matriz.usuario = request.user
            matriz.save()
            return redirect('listar_matrizes')
    else:
        form = MatrizCurricularForm()

    return render(request, 'core/adicionar_matriz.html', {'form': form})

@login_required
def editar_matriz(request, pk):
    matriz = get_object_or_404(MatrizCurricular, pk=pk)
    if request.method == 'POST':
        form = MatrizCurricularForm(request.POST, instance=matriz)
        if form.is_valid():
            form.save()
            return redirect('listar_matrizes')
    else:
        form = MatrizCurricularForm(instance=matriz)
    
    return render(request, 'core/editar_matriz.html', {'form': form})

@login_required
def excluir_matriz(request, pk):
    matriz = get_object_or_404(MatrizCurricular, pk=pk)
    if request.method == 'POST':
        matriz.delete()
        return redirect('listar_matrizes')

    return render(request, 'core/excluir_matriz.html', {'matriz': matriz})