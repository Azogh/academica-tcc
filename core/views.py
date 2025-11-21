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

<<<<<<< HEAD
=======
# Lógica de processamento do histórico em PDF (Foco APENAS em Disciplinas)
def processar_historico_pdf(pdf_file, nome_aluno, matricula, curso):
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
        # Itera sobre as páginas para extrair todo o texto
        for page in pdf_reader.pages:
            full_text += page.extract_text() or ""
            
        print(f"--- DEBUG: 2. Extração de texto concluída. Tamanho total: {len(full_text)} ---")
        
<<<<<<< HEAD
        # 3. Extração dos Dados das Disciplinas (Foco no RegEx)
        
        # 2. Extração dos Dados do Aluno e Curso (Página 1)
        
        # Nome do Aluno
        nome_match = re.search(r'Nome:\s*(.+?)\s*Data de Nascimento', full_text, re.DOTALL)
        if nome_match:
            dados_extraidos['nome_aluno'] = nome_match.group(1).strip()
            
        # Matrícula
        matricula_match = re.search(r'Matrícula:\s*(\d+)', full_text)
        if matricula_match:
            dados_extraidos['matricula'] = matricula_match.group(1).strip()
            
        # Curso
        # Captura o texto após 'Curso:' e antes de '/CCSSB' para evitar caracteres extras
        curso_match = re.search(r'Curso:\s*(.+?)/CCSSB', full_text, re.DOTALL)
        if curso_match:
            dados_extraidos['curso'] = curso_match.group(1).strip()


        # 3. Extração dos Dados das Disciplinas (Páginas 2 e 3)
        
        # Regex para encontrar a tabela de disciplinas. 
        # A tabela começa após "Componentes Curriculares Cursados/Cursando"
        # e termina antes de "Legenda" ou "Para verificar a autenticidade".
        # O padrão busca linhas que começam com "Ano/Periodo" (colunas) ou um Código de disciplina (8 dígitos)
        
        # O padrão busca linhas que se parecem com:
        # "2019.2 08023007 FUNDAMENTOS DE SISTEMAS DE INFORMAÇÃO Dr. CLAITON MARQUES CORREA (36h) 36 36 01 75.0 8,6 8.6 APR"
        
        # Busca todas as linhas que contenham um código de 8 dígitos seguido pelo nome da disciplina
        # e que tenham a coluna "Situação" (APR, REP, etc.) no final.
        # Este é um RegEx complexo e pode precisar de ajustes finos dependendo da saída do PyPDF2.
        
        # Padrão: Ano/Periodo (opcional) + Código (8 dígitos) + Nome da Disciplina + ... + Média + Situação (3-5 letras maiúsculas)
        
        # Nota: Como o PyPDF2 mescla as colunas, o mais seguro é buscar por padrões de linhas.
        
        # Exemplo de linha bruta:
        # "2019.2 08023007 FUNDAMENTOS DE SISTEMAS DE INFORMAÇÃO Dr. CLAITON MARQUES CORREA (36h) 36 36 01 75.0 8,6 8.6 APR"
        
        # Vamos usar um bloco de texto que contenha a tabela para iterar
        # Ele começa após 'Componentes Curriculares Cursados/Cursando'
        start_index = full_text.find("Componentes Curriculares Cursados/Cursando")
        end_index = full_text.find("Legenda") # A legenda está após as tabelas de notas
        
        if start_index != -1 and end_index != -1:
            # Captura apenas o bloco de texto da tabela de disciplinas
            tabela_text = full_text[start_index:end_index]
            
            # Padrão mais flexível: Ano/Período + Código + Nome da Disciplina + ... + Média + Situação
            # (\d{4}\.\d)\s* # Ano/Período (Ex: 2019.2) - Opcional, pois algumas linhas não têm
            # (\d{8}) # Código da Disciplina (Ex: 08023007)
            # (.+?) # Nome e Docente (Captura tudo que vier depois, non-greedy)
            # (\d{2,3})\s*(\d{2,3}) # CH e Carga Horária (duas colunas)
            # ([\d\.\,]+\s*) # Média (Ex: 8.6 ou 7,5)
            # (APR|REP|REPMF|CANC|DISP|MATR) # Situação (o mais importante)
            
            # Simplificação: Focar em Código, Nome e Situação no final
            # O PyPDF2 torna a extração de colunas muito difícil. Focaremos no código, nome e situação.
            # O bloco regex busca um código de disciplina, um nome (greedy) e uma situação conhecida no final.
            
            # Padrão: Código (8d) + Nome (tudo até...)+ CH/Carga Horária + ... + Situação
            disciplina_regex = re.compile(
                r'(\d{8})\s*(.+?)\s*' + SITUACOES, 
                re.DOTALL
            )
            
            for match in disciplina_regex.finditer(tabela_text):
                codigo = match.group(1).strip()
                nome_bruto_dados = match.group(2).strip()
                situacao = match.group(3).strip().upper()
                
                # O nome bruto contém o nome do professor. Precisamos separar:
                nome = re.sub(r'Dr\.\s*.+\(|\s*MSC\.\s*.+\(|\s*MSc\.\s*.+\(|\s*Professor\s*.+\(|\(\d{2,3}h\)|e\s*|\n', '', nome_bruto).strip()
                
                # 2. Remove notas, frequências, médias e a coluna da turma que foram mescladas (Sequências numéricas)
                nome = re.sub(r'[\d\.\,]+\s*(\d{2,3})?\s*$', '', nome).strip()
                
                # 3. Filtra e adiciona se for um nome de disciplina válido
                if nome and len(nome) > 5 and 'Componente Curricular' not in nome:
                    
                    # Vamos tentar extrair a carga horária da string bruta se existir
                    ch_match = re.search(r'(\d{2,3})h', nome_bruto)
                    ch = ch_match.group(1) if ch_match else ''
                    
                    dados_extraidos['disciplinas'].append({
                        'codigo': codigo,
                        'nome': nome,
                        'situacao': situacao
                    })
<<<<<<< HEAD
            
            print(f"--- DEBUG: 3. Disciplinas extraídas: {len(dados_extraidos['disciplinas'])} ---")

    except PyPDF2.errors.PdfReadError:
        print("!!! ERRO FATAL: O arquivo PDF está corrompido ou protegido por senha. !!!")
        return None
    except Exception as e:
        print(f"!!! ERRO INESPERADO DURANTE O PROCESSAMENTO DO PDF: {e} !!!")
=======

    except PyPDF2.errors.PdfReadError:
        print("Erro: O arquivo PDF está corrompido ou protegido por senha.")
        return None
    except Exception as e:
        print(f"Erro inesperado durante o processamento do PDF: {e}")
>>>>>>> 702790a (atualização)
        return None
    
    print("--- DEBUG: 4. FIM DO PROCESSAMENTO DE DISC. ---")
    return dados_extraidos


# View para lidar com o upload e o processamento (Atualizada para aceitar input manual)
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
def importar_historico_action(request: HttpRequest):
    print("\n--- INÍCIO DA REQUISIÇÃO IMPORTAR_HISTORICO_ACTION ---")
    if request.method == 'POST':
<<<<<<< HEAD
        # Instancia o formulário, assumindo que ele já inclui os campos de texto
        form = HistoricoUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Captura dados do formulário
            pdf_file = request.FILES.get('pdf_file') 
            nome_aluno = form.cleaned_data.get('nome_completo')
            matricula = form.cleaned_data.get('matricula')
            curso = form.cleaned_data.get('curso')
            
            # Validação: Garante que todos os campos obrigatórios foram preenchidos
            if not pdf_file or not nome_aluno or not matricula or not curso:
                print("!!! ERRO: Arquivo PDF ou campos de texto obrigatórios faltando !!!")
                return JsonResponse({"erro": "Nenhum arquivo ou dados obrigatórios (Nome, Matrícula, Curso) foram enviados."}, status=400)
            
            # Chama a função de processamento, passando os metadados chave
            dados = processar_historico_pdf(pdf_file, nome_aluno, matricula, curso)
            
            if dados is not None:
                print("--- SUCESSO: Dados processados e retornando JsonResponse ---")
                return JsonResponse(dados, status=200)
            else:
                print("!!! FALHA: processar_historico_pdf retornou None (erro interno) !!!")
                return JsonResponse({"erro": "Falha ao processar o arquivo PDF. Consulte logs no terminal."}, status=500)
        else:
            erros = form.errors.as_json()
            print(f"!!! ERRO DE FORMULÁRIO: {erros} !!!")
            return JsonResponse({"erro": "Dados inválidos", "detalhes": erros}, status=400)
            
    print("--- REDIRECIONANDO: Não é POST ---")
=======
        # Instancia o formulário, passando POST data E ARQUIVOS (request.FILES)
        form = HistoricoUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Capturando os dados do formulário
            nome_aluno = form.cleaned_data['nome_aluno']
            matricula = form.cleaned_data['matricula']
            curso = form.cleaned_data['curso']
            pdf_file = form.cleaned_data['pdf_file'] 
            
            if not pdf_file:
                return JsonResponse({"erro": "Nenhum arquivo 'pdf_file' encontrado na requisição."}, status=400)
            
            # TODO: O próximo passo será criar ou obter o objeto Aluno aqui
            # Exemplo de lógica para o futuro:
            # aluno, created = Aluno.objects.get_or_create(
            #     matricula=matricula,
            #     defaults={'nome': nome_aluno, 'curso': curso}
            # )
            
            # Chama a função de processamento
            dados = processar_historico_pdf(pdf_file)
            
            if dados is not None:
                # Adiciona os dados do aluno fornecidos no form ao resultado para referência
                dados['nome_aluno_input'] = nome_aluno
                dados['matricula_input'] = matricula
                dados['curso_input'] = curso
                
                # TODO: Aqui deve vir a lógica de salvar o Historico, Disciplinas, etc.
                
                # Por enquanto, retorna os dados processados + os dados de input
                return JsonResponse(dados, status=200)
            else:
                return JsonResponse({"erro": "Falha ao processar o arquivo PDF. Verifique o console para mais detalhes."}, status=500)
        else:
            # Se o formulário não for válido, retorna um erro JSON (assumindo chamada AJAX)
            erros = form.errors.as_json()
            return JsonResponse({"erro": "Dados inválidos", "detalhes": erros}, status=400)
            
    # Se não for POST, redireciona para a página de importação
>>>>>>> 702790a (atualização)
    return redirect('importar_historico')

# Views para o CRUD de Horários
>>>>>>> 928ea7b5e7244cd38faaea9f4c500a753caba395
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
