from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
import PyPDF2
import io
import re

from .models import (
    Usuario, MatrizCurricular, Disciplinas, Aluno, Historico,
    Ajuste, Turma, Horario, AjusteItens
)
from .forms import (
    CoordenadorCadastroForm, MatrizCurricularForm, DisciplinaForm,
    TurmaForm, HorarioForm, HistoricoUploadForm
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

# Views para o CRUD de Disciplinas
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

# Views para o CRUD de Turmas
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

# Views para o CRUD de Horários
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

# Lógica de processamento do histórico em PDF (Início da implementação)
def processar_historico_pdf(pdf_file):
    """
    Função auxiliar para ler o PDF e extrair dados do histórico.
    """
    dados_extraidos = {
        'nome_aluno': '',
        'matricula': '',
        'curso': '',
        'disciplinas': []
    }

    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() or ""
        
        # TODO: Adicionar a lógica de extração do texto
        # Usar expressões regulares para encontrar os dados do aluno, curso e a tabela de disciplinas.
        # Exemplo (pseudocódigo):
        # nome_match = re.search(r'Nome:\s*(.*)', full_text)
        # if nome_match:
        #     dados_extraidos['nome_aluno'] = nome_match.group(1).strip()
        
    except Exception as e:
        print(f"Erro ao processar PDF: {e}")
        return None
    
    return dados_extraidos


# View para lidar com o upload e o processamento
@login_required
def importar_historico(request):
    historicos_importados = Historico.objects.all().order_by('-data_upload')
    
    paginator = Paginator(historicos_importados, 10)
    page = request.GET.get('page')
    try:
        historicos = paginator.page(page)
    except PageNotAnInteger:
        historicos = paginator.page(1)
    except EmptyPage:
        historicos = paginator.page(paginator.num_pages)

    # Passa as listas para os filtros
    cursos_disponiveis = MatrizCurricular.objects.values_list('curso', flat=True).distinct()
    anos_disponiveis = Turma.objects.values_list('ano_ingresso', flat=True).distinct()
    
    return render(request, 'core/historicos/importar_historico.html', {
        'historicos': historicos,
        'cursos_disponiveis': cursos_disponiveis,
        'anos_disponiveis': anos_disponiveis,
        'form': HistoricoUploadForm(),
    })

@login_required
def importar_historico_action(request):
    if request.method == 'POST':
        form = HistoricoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            
            # Chama a nova função de processamento
            dados = processar_historico_pdf(pdf_file)
            
            if dados:
                # TODO: Implementar a lógica para salvar os dados no banco (próximo passo após a extração)
                # Por enquanto, vamos apenas exibir os dados para teste
                return JsonResponse(dados)
            else:
                # Mensagem de erro para o usuário
                return render(request, 'core/historicos/importar_historico.html', {'form': form, 'error_message': 'Falha ao processar o arquivo PDF.'})
    
    return redirect('importar_historico')

@login_required
def consultar_historico(request, pk):
    historico = get_object_or_404(Historico, pk=pk)
    disciplinas_cursadas = Historico.objects.filter(aluno=historico.aluno)
    
    disciplinas_pendentes = [
        {'nome': 'Estrutura de Dados II', 'sigla': 'ED2'},
        {'nome': 'Sistemas Distribuídos', 'sigla': 'SD'},
    ]

    return render(request, 'core/historicos/consultar_historico.html', {
        'historico': historico,
        'disciplinas_cursadas': disciplinas_cursadas,
        'disciplinas_pendentes': disciplinas_pendentes,
    })

@login_required
def editar_historico(request, pk):
    # Lógica de edição (placeholder)
    historico = get_object_or_404(Historico, pk=pk)
    return render(request, 'core/historicos/editar_historico.html', {'historico': historico})

@login_required
def excluir_historico(request, pk):
    # Lógica de exclusão (placeholder)
    historico = get_object_or_404(Historico, pk=pk)
    return render(request, 'core/historicos/excluir_historico.html', {'historico': historico})

@login_required
def consultar_analise(request):
    # Lógica de análise (placeholder)
    return render(request, 'core/historicos/consultar_analise.html', {})


# Nova view para consulta de horários
@login_required
def consultar_horarios(request):
    horarios_list = Horario.objects.all()
    
    curso = request.GET.get('curso')
    ano_ingresso = request.GET.get('ano')

    if curso:
        horarios_list = horarios_list.filter(turma__matriz_curricular__curso=curso)
    
    if ano_ingresso:
        horarios_list = horarios_list.filter(turma__ano_ingresso=ano_ingresso)

    grade_horarios = {}
    dias_semana = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
    periodos = ['1-2', '3-4']
    
    for dia in dias_semana:
        grade_horarios[dia] = {'1-2': None, '3-4': None}

    for horario in horarios_list:
        grade_horarios[horario.dia_semana][horario.periodo] = horario.disciplina.sigla

    cursos = MatrizCurricular.objects.values_list('curso', flat=True).distinct()
    anos_turma = Turma.objects.values_list('ano_ingresso', flat=True).distinct()
    
    return render(request, 'core/horarios/consultar_horarios.html', {
        'grade': grade_horarios,
        'dias_semana': dias_semana,
        'periodos': periodos,
        'cursos': cursos,
        'anos': anos_turma
    })

# Views de dados para o painel de controle
@login_required
def chart_data_view(request):
    # Dados de exemplo (substituir por lógica de banco de dados)
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