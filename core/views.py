from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # <--- 1. IMPORTAÇÃO NOVA AQUI
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Count
from django.contrib.auth import logout

# Importações de Modelos e Formulários
from .models import (
    Usuario, MatrizCurricular, Disciplinas, Turma, Horario
)
from .forms import (
    CoordenadorCadastroForm, MatrizCurricularForm, DisciplinaForm,
    TurmaForm, HorarioForm
)
from .templatetags.dict_filters import get_item

# ====================================================================
# Views de Páginas e Autenticação
# ====================================================================

def landing_page(request):
    """Renderiza a página inicial (Landing Page) do sistema."""
    return render(request, 'core/landing_page.html', {})

def autocadastro_coordenador(request):
    """
    Permite que um novo coordenador se cadastre no sistema.
    Após o cadastro, exibe mensagem de sucesso e redireciona para login.
    """
    if request.method == 'POST':
        form = CoordenadorCadastroForm(request.POST)
        if form.is_valid():
            form.save() # Salva o usuário, mas NÃO loga automaticamente
            
            # 2. MENSAGEM DE SUCESSO ADICIONADA
            messages.success(request, 'Cadastro realizado com sucesso! Por favor, faça seu login.')
            
            return redirect('login')
    else:
        form = CoordenadorCadastroForm()
    
    return render(request, 'core/autocadastro.html', {'form': form})

def login_view(request):
    """Gerencia o processo de login do usuário."""
    # Se o usuário já estiver logado, redireciona direto para o painel
    if request.user.is_authenticated:
        return redirect('painel')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('painel')
        else:
            # Opcional: Mensagem de erro se login falhar
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

@login_required
def painel_coordenador(request):
    """Renderiza o painel de controle principal do coordenador (dashboard)."""
    return render(request, 'core/painel.html', {})

# ====================================================================
# O RESTANTE DO ARQUIVO PERMANECE IDÊNTICO AO QUE VOCÊ MANDOU
# (CRUD de Matriz, Disciplinas, Turmas, Horários e JSON)
# ====================================================================
@login_required
def listar_matrizes(request):
    # ... (seu código original)
    matrizes_list = MatrizCurricular.objects.all().order_by('-ano_referencia')
    ano = request.GET.get('ano')
    if ano:
        matrizes_list = matrizes_list.filter(ano_referencia=ano)
    anos_disponiveis = MatrizCurricular.objects.values_list('ano_referencia', flat=True).distinct().order_by('-ano_referencia')
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

@login_required
def listar_disciplinas(request):
    disciplinas_list = Disciplinas.objects.all().order_by('semestre', 'nome')
    matriz_id = request.GET.get('matriz')
    semestre = request.GET.get('semestre')
    if matriz_id:
        disciplinas_list = disciplinas_list.filter(matriz_curricular__pk=matriz_id)
    if semestre:
        disciplinas_list = disciplinas_list.filter(semestre=semestre)
    matrizes_disponiveis = MatrizCurricular.objects.all()
    semestres_disponiveis = Disciplinas.objects.values_list('semestre', flat=True).distinct().order_by('semestre')
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

@login_required
def listar_turmas(request):
    turmas_list = Turma.objects.all().order_by('-ano_ingresso')
    ano = request.GET.get('ano')
    if ano:
        turmas_list = turmas_list.filter(ano_ingresso=ano)
    anos_disponiveis = Turma.objects.values_list('ano_ingresso', flat=True).distinct().order_by('-ano_ingresso')
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

@login_required
def listar_horarios(request):
    horarios_list = Horario.objects.all().order_by('turma', 'dia_semana', 'periodo')
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
    """Permite adicionar um novo Horário (com suporte a 4 créditos)."""
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        
        if form.is_valid():
            # 1. Salva o Primeiro Horário (Padrão do ModelForm)
            horario1 = form.save(commit=False)
            horario1.usuario = request.user
            horario1.save()
            
            # 2. LÓGICA MANUAL: Verifica se era 4 créditos para salvar o segundo
            # É aqui que o sistema estava "esquecendo" de salvar a quarta-feira
            if form.cleaned_data.get('creditos') == '4':
                
                # Cria um NOVO registro no banco para o segundo encontro
                Horario.objects.create(
                    turma=horario1.turma,                   # Mesma turma
                    disciplina=horario1.disciplina,         # Mesma disciplina
                    dia_semana=form.cleaned_data['dia_semana_2'], # Pega do campo extra do form
                    periodo=form.cleaned_data['periodo_2'],       # Pega do campo extra do form
                    usuario=request.user
                )
                messages.success(request, "Disciplina de 4 créditos salva (2 horários criados)!")
            else:
                messages.success(request, "Horário cadastrado com sucesso!")

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

# core/views.py

@login_required
def consultar_horarios(request):
    """
    Exibe a grade de horários filtrada por Turma para evitar conflitos visuais.
    """
    # 1. Captura os filtros da URL (GET)
    curso_selecionado = request.GET.get('curso')
    turma_id_selecionada = request.GET.get('turma')

    # 2. Dados para popular os Selects (Dropdowns)
    # Buscamos cursos distintos nas Matrizes
    cursos_disponiveis = MatrizCurricular.objects.values_list('curso', flat=True).distinct().order_by('curso')
    
    # Buscamos Turmas. 
    # Se um curso foi selecionado, filtramos as turmas que têm aulas nesse curso 
    # (via Horario -> Disciplina -> Matriz -> Curso) para facilitar a vida do usuário.
    if curso_selecionado:
        turmas_disponiveis = Turma.objects.filter(
            horario__disciplina__matriz_curricular__curso=curso_selecionado
        ).distinct().order_by('-ano_ingresso')
    else:
        turmas_disponiveis = Turma.objects.all().order_by('-ano_ingresso')

    # 3. Construção da Grade
    # A grade começa vazia ou zerada
    grade_horarios = {}
    dias_semana = Horario.DIA_CHOICES      # [('SEG', 'Segunda'), ...]
    periodos = Horario.PERIODO_CHOICES     # [('1-2', 'Período 1 e 2'), ...]

    # Inicializa a estrutura vazia da grade
    for dia_sigla, _ in dias_semana:
        grade_horarios[dia_sigla] = {periodo_sigla: None for periodo_sigla, _ in periodos}

    # Só preenchemos a grade se uma TURMA específica for selecionada
    horarios_filtrados = []
    
    if turma_id_selecionada:
        horarios_filtrados = Horario.objects.filter(turma__id=turma_id_selecionada)
        
        for h in horarios_filtrados:
            # Preenche a célula: [Dia][Periodo] = "Sigla Disciplina (Nome Professor/Sala se tivesse)"
            # Aqui estamos colocando a Sigla + Nome da disciplina para ficar claro
            conteudo_celula = {
                'disciplina': f"{h.disciplina.sigla}",
                'nome_completo': h.disciplina.nome,
                'codigo': h.disciplina.codigo
            }
            grade_horarios[h.dia_semana][h.periodo] = conteudo_celula

    return render(request, 'core/horarios/consultar_horarios.html', {
        'grade': grade_horarios,
        'dias_semana': dias_semana,
        'periodos': periodos,
        'cursos_disponiveis': cursos_disponiveis,
        'turmas_disponiveis': turmas_disponiveis,
        'curso_selecionado': curso_selecionado,
        'turma_selecionada': turma_id_selecionada and int(turma_id_selecionada),
    })

@login_required
def chart_data_view(request):
    """
    Retorna dados REAIS do banco de dados para os gráficos.
    """
    
    # ---------------------------------------------------------
    # 1. GRÁFICO DE DISCIPLINAS (Real)
    # Busca todas as matrizes e conta quantas disciplinas cada uma tem
    # ---------------------------------------------------------
    matrizes_data = MatrizCurricular.objects.annotate(total_disciplinas=Count('disciplinas')).order_by('curso')
    
    # Cria as listas para o Chart.js
    disc_labels = [m.curso for m in matrizes_data] # Ex: ['Sistemas de Informação', 'Direito']
    disc_values = [m.total_disciplinas for m in matrizes_data] # Ex: [45, 50]

    # Tratamento caso não tenha nada cadastrado ainda
    if not disc_labels:
        disc_labels = ['Sem Matrizes']
        disc_values = [0]

    disciplinas_data = {
        'labels': disc_labels,
        'datasets': [{'label': 'Qtd. Disciplinas', 'data': disc_values}]
    }

    # ---------------------------------------------------------
    # 2. GRÁFICO DE TURMAS (Real - Substituindo "Rematrículas" por enquanto)
    # Mostra quantas turmas foram abertas por ano
    # ---------------------------------------------------------
    turmas_data = Turma.objects.values('ano_ingresso').annotate(total=Count('id')).order_by('ano_ingresso')
    
    turma_labels = [str(t['ano_ingresso']) for t in turmas_data]
    turma_values = [t['total'] for t in turmas_data]

    rematriculas_data = {
        'labels': turma_labels if turma_labels else ['Sem Turmas'],
        'datasets': [{'label': 'Turmas por Ano', 'data': turma_values if turma_values else [0]}]
    }

    # ---------------------------------------------------------
    # 3. OUTROS GRÁFICOS (Placeholders Limpos)
    # Como os modelos de Histórico e Análise estão em outros apps (upload/analytics),
    # vamos deixá-los zerados para não mentir para o usuário.
    # Futuramente, você importará: from upload.models import Historico
    # ---------------------------------------------------------
    
    historicos_data = {
        'labels': ['Com Histórico', 'Sem Histórico'],
        'datasets': [{'label': 'Total', 'data': [0, 0]}] # Zerado por enquanto
    }

    reprovacao_data = {
        'labels': ['Aguardando Dados'],
        'datasets': [{'label': 'Índice (%)', 'data': [0]}] # Zerado por enquanto
    }
    
    return JsonResponse({
        'disciplinas': disciplinas_data,
        'historicos': historicos_data,
        'reprovacao': reprovacao_data,
        'rematriculas': rematriculas_data
    })

@login_required
def consultar_analise(request):
    return render(request, 'core/historicos/consultar_analise.html', {})


def logout_view(request):
    """Faz o logout do usuário e redireciona para o login."""
    logout(request)
    messages.info(request, "Você saiu do sistema com sucesso.")
    return redirect('login')