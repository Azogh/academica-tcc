from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import views as auth_views

from .models import (
    Usuario, MatrizCurricular, Disciplinas, Aluno, Historico,
    Ajuste, Turma, Horario, AjusteItens
)
from .forms import (
    CoordenadorCadastroForm, MatrizCurricularForm, DisciplinaForm,
    TurmaForm, HorarioForm
)

# Views de Páginas e Autenticação
def landing_page(request):
    return render(request, 'core/landing_page.html', {})

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
    
    return render(request, 'core/matrizes/listar_matrizes.html', {'matrizes': matrizes})

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

    return render(request, 'core/matrizes/adicionar_matriz.html', {'form': form})

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
    
    return render(request, 'core/matrizes/editar_matriz.html', {'form': form})

@login_required
def excluir_matriz(request, pk):
    matriz = get_object_or_404(MatrizCurricular, pk=pk)
    if request.method == 'POST':
        matriz.delete()
        return redirect('listar_matrizes')

    return render(request, 'core/matrizes/excluir_matriz.html', {'matriz': matriz})

# Views para o CRUD de Disciplinas
@login_required
def listar_disciplinas(request):
    disciplinas_list = Disciplinas.objects.all().order_by('semestre', 'nome')
    paginator = Paginator(disciplinas_list, 15)
    page = request.GET.get('page')
    try:
        disciplinas = paginator.page(page)
    except PageNotAnInteger:
        disciplinas = paginator.page(1)
    except EmptyPage:
        disciplinas = paginator.page(paginator.num_pages)
    return render(request, 'core/disciplinas/listar_disciplinas.html', {'disciplinas': disciplinas})

@login_required
def adicionar_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save(commit=False)
            disciplina.usuario = request.user
            disciplina.save()
            return redirect('listar_disciplinas')
    else:
        form = DisciplinaForm()
    return render(request, 'core/disciplinas/adicionar_disciplina.html', {'form': form})

@login_required
def editar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplinas, pk=pk)
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            return redirect('listar_disciplinas')
    else:
        form = DisciplinaForm(instance=disciplina)
    return render(request, 'core/disciplinas/editar_disciplina.html', {'form': form})

@login_required
def excluir_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplinas, pk=pk)
    if request.method == 'POST':
        disciplina.delete()
        return redirect('listar_disciplinas')
    return render(request, 'core/disciplinas/excluir_disciplina.html', {'disciplina': disciplina})

# Views para o CRUD de Turmas
@login_required
def listar_turmas(request):
    turmas_list = Turma.objects.all().order_by('-ano_ingresso')
    paginator = Paginator(turmas_list, 10)
    page = request.GET.get('page')
    try:
        turmas = paginator.page(page)
    except PageNotAnInteger:
        turmas = paginator.page(1)
    except EmptyPage:
        turmas = paginator.page(paginator.num_pages)
    return render(request, 'core/turmas/listar_turmas.html', {'turmas': turmas})

@login_required
def adicionar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save(commit=False)
            turma.usuario = request.user
            turma.save()
            return redirect('listar_turmas')
    else:
        form = TurmaForm()
    return render(request, 'core/turmas/adicionar_turma.html', {'form': form})

@login_required
def editar_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma)
        if form.is_valid():
            form.save()
            return redirect('listar_turmas')
    else:
        form = TurmaForm(instance=turma)
    return render(request, 'core/turmas/editar_turma.html', {'form': form})

@login_required
def excluir_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        turma.delete()
        return redirect('listar_turmas')
    return render(request, 'core/turmas/excluir_turma.html', {'turma': turma})

# Views para o CRUD de Horários
@login_required
def listar_horarios(request):
    horarios_list = Horario.objects.all().order_by('turma', 'dia_semana', 'periodo')
    paginator = Paginator(horarios_list, 20)
    page = request.GET.get('page')
    try:
        horarios = paginator.page(page)
    except PageNotAnInteger:
        horarios = paginator.page(1)
    except EmptyPage:
        horarios = paginator.page(paginator.num_pages)
    return render(request, 'core/horarios/listar_horarios.html', {'horarios': horarios})

@login_required
def adicionar_horario(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.usuario = request.user
            horario.save()
            return redirect('listar_horarios')
    else:
        form = HorarioForm()
    return render(request, 'core/horarios/adicionar_horario.html', {'form': form})

@login_required
def editar_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect('listar_horarios')
    else:
        form = HorarioForm(instance=horario)
    return render(request, 'core/horarios/editar_horario.html', {'form': form})

@login_required
def excluir_horario(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        horario.delete()
        return redirect('listar_horarios')
    return render(request, 'core/horarios/excluir_horario.html', {'horario': horario})