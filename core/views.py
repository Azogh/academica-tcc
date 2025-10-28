from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Count

# Importações de Modelos e Formulários
from .models import (
    Usuario, MatrizCurricular, Disciplinas, Turma, Horario
)
from .forms import (
    CoordenadorCadastroForm, MatrizCurricularForm, DisciplinaForm,
    TurmaForm, HorarioForm
)
from .templatetags.dict_filters import get_item # Utilizado em consultar_horarios

# ====================================================================
# Views de Páginas e Autenticação
# ====================================================================

def landing_page(request):
    """Renderiza a página inicial (Landing Page) do sistema."""
    return render(request, 'core/landing_page.html', {})

def autocadastro_coordenador(request):
    """
    Permite que um novo coordenador se cadastre no sistema.
    Após o cadastro, o usuário é redirecionado para a tela de login.
    """
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
    """Gerencia o processo de login do usuário."""
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
    """Renderiza o painel de controle principal do coordenador (dashboard)."""
    return render(request, 'core/painel.html', {})

# ====================================================================
# Views para o CRUD de Matriz Curricular
# ====================================================================

@login_required
def listar_matrizes(request):
    """Lista e filtra as Matrizes Curriculares cadastradas."""
    matrizes_list = MatrizCurricular.objects.all().order_by('-ano_referencia')
    
    # Filtro por ano de referência
    ano = request.GET.get('ano')
    if ano:
        matrizes_list = matrizes_list.filter(ano_referencia=ano)

    # Coleta anos disponíveis para o filtro
    anos_disponiveis = MatrizCurricular.objects.values_list('ano_referencia', flat=True).distinct().order_by('-ano_referencia')

    # Configuração da paginação
    paginator = Paginator(matrizes_list, 10)
    page = request.GET.get('page')
    try:
        matrizes = paginator.page(page)
    except PageNotAnInteger:
        matrizes = paginator.page(1)
    except EmptyPage:
        matrizes = paginator.page(paginator.num_pages)
    
    return render(request, 'core/matrizes/listar_matrizes.html', {
        'matrizes': matrizes,
        'anos_disponiveis': anos_disponiveis
    })

@login_required
def adicionar_matriz(request):
    """Permite adicionar uma nova Matriz Curricular."""
    if request.method == 'POST':
        form = MatrizCurricularForm(request.POST)
        if form.is_valid():
            matriz = form.save(commit=False)
            matriz.usuario = request.user # Associa ao usuário logado
            matriz.save()
            return redirect('listar_matrizes')
    else:
        form = MatrizCurricularForm()

    return render(request, 'core/matrizes/adicionar_matriz.html', {'form': form})

@login_required
def editar_matriz(request, pk):
    """Permite editar uma Matriz Curricular existente."""
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
    """Permite excluir uma Matriz Curricular."""
    matriz = get_object_or_404(MatrizCurricular, pk=pk)
    if request.method == 'POST':
        matriz.delete()
        return redirect('listar_matrizes')

    return render(request, 'core/matrizes/excluir_matriz.html', {'matriz': matriz})

# ====================================================================
# Views para o CRUD de Disciplinas
# ====================================================================

@login_required
def listar_disciplinas(request):
    """Lista e filtra as Disciplinas cadastradas."""
    disciplinas_list = Disciplinas.objects.all().order_by('semestre', 'nome')
    
    # Filtros
    matriz_id = request.GET.get('matriz')
    semestre = request.GET.get('semestre')
    
    if matriz_id:
        # Filtra por chave estrangeira (matriz_curricular)
        disciplinas_list = disciplinas_list.filter(matriz_curricular__pk=matriz_id)
    
    if semestre:
        disciplinas_list = disciplinas_list.filter(semestre=semestre)

    matrizes_disponiveis = MatrizCurricular.objects.all()
    semestres_disponiveis = Disciplinas.objects.values_list('semestre', flat=True).distinct().order_by('semestre')

    # Configuração da paginação
    paginator = Paginator(disciplinas_list, 15)
    page = request.GET.get('page')
    try:
        disciplinas = paginator.page(page)
    except PageNotAnInteger:
        disciplinas = paginator.page(1)
    except EmptyPage:
        disciplinas = paginator.page(paginator.num_pages)
        
    return render(request, 'core/disciplinas/listar_disciplinas.html', {
        'disciplinas': disciplinas,
        'matrizes_disponiveis': matrizes_disponiveis,
        'semestres_disponiveis': semestres_disponiveis,
    })

@login_required
def adicionar_disciplina(request):
    """Permite adicionar uma nova Disciplina."""
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
    """Permite editar uma Disciplina existente."""
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
    """Permite excluir uma Disciplina."""
    disciplina = get_object_or_404(Disciplinas, pk=pk)
    if request.method == 'POST':
        disciplina.delete()
        return redirect('listar_disciplinas')
    return render(request, 'core/disciplinas/excluir_disciplina.html', {'disciplina': disciplina})

# ====================================================================
# Views para o CRUD de Turmas
# ====================================================================

@login_required
def listar_turmas(request):
    """Lista e filtra as Turmas cadastradas."""
    turmas_list = Turma.objects.all().order_by('-ano_ingresso')
    
    # Filtro por ano de ingresso
    ano = request.GET.get('ano')
    if ano:
        turmas_list = turmas_list.filter(ano_ingresso=ano)
        
    anos_disponiveis = Turma.objects.values_list('ano_ingresso', flat=True).distinct().order_by('-ano_ingresso')

    # Configuração da paginação
    paginator = Paginator(turmas_list, 10)
    page = request.GET.get('page')
    try:
        turmas = paginator.page(page)
    except PageNotAnInteger:
        turmas = paginator.page(1)
    except EmptyPage:
        turmas = paginator.page(paginator.num_pages)
    return render(request, 'core/turmas/listar_turmas.html', {
        'turmas': turmas,
        'anos_disponiveis': anos_disponiveis
    })

@login_required
def adicionar_turma(request):
    """Permite adicionar uma nova Turma."""
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
    """Permite editar uma Turma existente."""
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
    """Permite excluir uma Turma."""
    turma = get_object_or_404(Turma, pk=pk)
    if request.method == 'POST':
        turma.delete()
        return redirect('listar_turmas')
    return render(request, 'core/turmas/excluir_turma.html', {'turma': turma})

# ====================================================================
# Views para o CRUD e Consulta de Horários
# ====================================================================

@login_required
def listar_horarios(request):
    """Lista e filtra os Horários cadastrados (gestão)."""
    horarios_list = Horario.objects.all().order_by('turma', 'dia_semana', 'periodo')
    
    # Filtros de gestão
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    dia_semana = request.GET.get('dia_semana')
    periodo = request.GET.get('periodo')
    
    if turma_id:
        horarios_list = horarios_list.filter(turma__pk=turma_id)
    
    if disciplina_id:
        horarios_list = horarios_list.filter(disciplina__pk=disciplina_id)
    
    if dia_semana:
        horarios_list = horarios_list.filter(dia_semana=dia_semana)

    if periodo:
        horarios_list = horarios_list.filter(periodo=periodo)

    turmas_disponiveis = Turma.objects.all()
    disciplinas_disponiveis = Disciplinas.objects.all()
    
    # Configuração da paginação
    paginator = Paginator(horarios_list, 20)
    page = request.GET.get('page')
    try:
        horarios = paginator.page(page)
    except PageNotAnInteger:
        horarios = paginator.page(1)
    except EmptyPage:
        horarios = paginator.page(paginator.num_pages)
        
    return render(request, 'core/horarios/listar_horarios.html', {
        'horarios': horarios,
        'turmas_disponiveis': turmas_disponiveis,
        'disciplinas_disponiveis': disciplinas_disponiveis,
        'dia_semana_choices': Horario.DIA_CHOICES,
        'periodo_choices': Horario.PERIODO_CHOICES,
    })

@login_required
def adicionar_horario(request):
    """Permite adicionar um novo Horário."""
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
    """Permite editar um Horário existente."""
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
    """Permite excluir um Horário."""
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        horario.delete()
        return redirect('listar_horarios')
    return render(request, 'core/horarios/excluir_horario.html', {'horario': horario})

@login_required
def consultar_horarios(request):
    """
    Exibe a grade de horários consolidada com filtros por Curso e Ano de Ingresso (Turma).
    """
    horarios_list = Horario.objects.all()
    
    curso = request.GET.get('curso')
    ano_ingresso = request.GET.get('ano')

    if curso:
        # Filtra horários com base no curso da Matriz Curricular da Turma
        horarios_list = horarios_list.filter(turma__matriz_curricular__curso=curso)
    
    if ano_ingresso:
        # Filtra horários com base no ano de ingresso da Turma
        horarios_list = horarios_list.filter(turma__ano_ingresso=ano_ingresso)

    # Inicializa a estrutura da grade de horários (dicionário aninhado)
    grade_horarios = {}
    dias_semana = Horario.DIA_CHOICES
    periodos = Horario.PERIODO_CHOICES
    
    # Cria a estrutura vazia
    for dia_sigla, _ in dias_semana:
        grade_horarios[dia_sigla] = {periodo_sigla: None for periodo_sigla, _ in periodos}

    # Preenche a grade com as siglas das disciplinas
    for horario in horarios_list:
        grade_horarios[horario.dia_semana][horario.periodo] = horario.disciplina.sigla

    cursos = MatrizCurricular.objects.values_list('curso', flat=True).distinct()
    anos_turma = Turma.objects.values_list('ano_ingresso', flat=True).distinct()
    
    return render(request, 'core/horarios/consultar_horarios.html', {
        'grade': grade_horarios,
        'dias_semana': [dia[0] for dia in dias_semana], # Passa apenas as siglas
        'periodos': [periodo[0] for periodo in periodos], # Passa apenas as siglas
        'cursos': cursos,
        'anos': anos_turma
    })

# ====================================================================
# Views de Dados para o Dashboard
# ====================================================================

@login_required
def chart_data_view(request):
    """
    Retorna dados estatísticos em formato JSON para alimentar os gráficos do painel.
    Estes dados são atualmente estáticos e devem ser substituídos por lógica de BI/analytics.
    """
    # --- Dados de Exemplo Estáticos (A ser substituído na V2) ---
    disciplinas_data = {
        'labels': ['Matemática', 'Física', 'Sistemas da Informação', 'Gastronomia'],
        'datasets': [{'label': 'Disciplinas por Matriz', 'data': [15, 12, 20, 18]}]
    }

    historicos_data = {
        'labels': ['Alunos com Histórico', 'Alunos sem Histórico'],
        'datasets': [{'label': 'Históricos no Sistema', 'data': [50, 10]}]
    }

    reprovacao_data = {
        'labels': ['Lab. BD', 'Estrutura de Dados', 'Redes de Comp.'],
        'datasets': [{'label': 'Reprovação (%)', 'data': [25, 45, 15]}]
    }
    
    rematriculas_data = {
        'labels': ['Aprovadas', 'Pendentes', 'Canceladas'],
        'datasets': [{'label': 'Status de Rematrículas', 'data': [35, 15, 5]}]
    }

    return JsonResponse({
        'disciplinas': disciplinas_data,
        'historicos': historicos_data,
        'reprovacao': reprovacao_data,
        'rematriculas': rematriculas_data
    })

@login_required
def consultar_analise(request):
    """Renderiza a tela de consulta da análise de matrícula (IA)."""
    return render(request, 'core/historicos/consultar_analise.html', {})

# ====================================================================
# Views de Histórico (Stubs de redirecionamento - Serão removidas na V2)
# Essas views serão implementadas na aplicação 'upload' e 'analise'.
# Removendo a lógica de CRUD e de Processamento, mas mantendo os stubs
# temporariamente para evitar erros nas URLs do template base.
# ====================================================================

# Estas views (consultar_historico, editar_historico, excluir_historico)
# seriam movidas para 'upload/views.py' na V2, mas são removidas daqui
# temporariamente, pois a rota foi removida em core/urls.py (próximo passo).

# Removendo todos os stubs de Histórico para garantir que o 'core' fique limpo.
# O novo código do Histórico será gerado na aplicação 'upload' em seguida.
