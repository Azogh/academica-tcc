from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.db import transaction
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import PyPDF2
import io
import re

from .models import Aluno, Historico, HistoricoItens
from .forms import HistoricoUploadForm
# Modelos necessários do core (ou da aplicação de Estrutura Curricular)
from core.models import Disciplinas 


# ====================================================================
# LÓGICA AUXILIAR DE PROCESSAMENTO DE PDF (AJUSTADA PARA O FORMATO SIGAA/IFFAR)
# ====================================================================

def processar_historico_pdf(pdf_file: io.BytesIO, aluno_obj: Aluno):
    """
    Função auxiliar que recebe o arquivo PDF e o objeto Aluno já persistido.
    Foca na extração e retorno dos dados da tabela de disciplinas do PDF.
    
    A expressão regular é otimizada para capturar os dados do histórico
    do IFFar, que segue um formato tabular de várias colunas.
    """
    dados_disciplinas = []
    
    # 1. Cria o objeto Histórico (Status Pendente) para vincular os itens
    historico = Historico.objects.create(
        aluno=aluno_obj,
        usuario=aluno_obj.usuario, 
        status='PENDENTE',
        arquivo_original=pdf_file 
    )

    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        full_text = ""
        # Itera sobre as páginas para extrair todo o texto
        for page in pdf_reader.pages:
            full_text += page.extract_text() or ""
            
        # 2. Extração dos Dados das Disciplinas
        
        # O histórico real do SIGAA tem linhas que começam com "Ano/Periodo Letivo" ou um CÓDIGO
        # Precisamos de um RegEx que capture a linha completa:
        
        # Padrão de Início da Linha: (Ano/Periodo Letivo Opcional) (Código 8d)
        # O corpo do texto (Componente Curricular) é o mais variável.
        # Captura: (1) Período | (2) Código | (3) Nome/Bruto | (4) CH | (5) Freq % | (6) Média | (7) Situação
        
        # Padrão ajustado para o formato SIGAA (Baseado nas páginas 2 e 3)
        # Notas: A vírgula (,) na nota precisa ser tratada; o CH é capturado duas vezes (Aula e Efetiva).
        disciplina_regex = re.compile(
            r'(\d{4}\.\d{1,2}|\s*)\n*(\d{8}|\#|\-)\n*(.+?)\n*(\d{2,4})\n*(\d{2,4})\n*(\d{1,2})\n*([\d\.\,]+\s*|\s*)\n*([\d\.\,]+\s*|\s*)\n*([\d\.\,]+\s*|\s*)\n*(APR|REP|REPMF|CANC|DISP|MATR|CUMP|REPF)',
            re.DOTALL | re.MULTILINE
        )
        
        # O texto bruto é muito inconsistente. Vamos focar apenas na seção de COMPONENTES CURRICULARES CURSADOS/CURSANDO
        # E remover linhas vazias para melhorar a consistência.
        
        start_key = "Componentes Curriculares Cursados/Cursando"
        end_key = "Legenda"
        start_index = full_text.find(start_key)
        end_index = full_text.find(end_key)
        
        if start_index != -1 and end_index != -1:
            # Pega o texto da tabela e remove as quebras de linha que a extração do PDF criou
            tabela_text = full_text[start_index + len(start_key):end_index]
            
            # Limpeza preliminar: remove cabeçalhos de coluna que se repetem e espaços excessivos
            tabela_text = re.sub(r'"Ano/Periodo\s*Letivo.+"Situação\s*"', '', tabela_text, flags=re.DOTALL)
            tabela_text = re.sub(r'(\d{4}\.\d{1,2})\s*e\n*', r'\1\n', tabela_text) # Trata linhas onde tem 'e'
            tabela_text = re.sub(r'\n+', '\n', tabela_text).strip()
            
            # Tenta um padrão mais simples e focado no final da linha (onde os dados são mais consistentes)
            # (1) Periodo/Ano (2) Código (3) Nome (4) CH Efetiva (5) Freq % (6) Média Final (7) Situação
            
            # Padrão final para a linha de dados:
            disciplina_regex_v2 = re.compile(
                # (1) Ano/Periodo Letivo (Pode estar vazio se for linha subsequente)
                r'(\d{4}\.\d{1,2}|)\s*' 
                # (2) Código (8 dígitos, #, ou -)
                r'(\d{8}|\#|\-)\s*'
                # (3) Nome do Componente (Captura até a CH)
                r'(.+?)\s*' 
                # (4) CH/Hora Aula (Vários dígitos, seguidos por Turma e Freq)
                r'\d{1,4}\s*' # Hora Aula
                r'(\d{1,4})\s*' # CH Efetiva (o que nos interessa) -> Grupo 4
                r'(\d{1,2}|\s*)\s*' # Turma
                r'([\d\.\,]+\s*|\s*)\s*' # Freq % (Grupo 6)
                r'([\d\.\,]+\s*|\s*)\s*' # Nota Min
                r'([\d\.\,]+\s*|\s*)\s*' # Média Final (Grupo 8)
                # (9) Situação (APR|REP|CANC...) -> Grupo 9
                r'(APR|REP|REPMF|CANC|DISP|MATR|CUMP|REPF|TRANC)', 
                re.DOTALL | re.MULTILINE | re.IGNORECASE
            )
            
            # Remove o texto dos professores/parenteses para limpar o nome
            tabela_text_limpa = re.sub(r'\s*\([^\)]*?\)\s*', '', tabela_text)
            
            
            for match in disciplina_regex_v2.finditer(tabela_text_limpa):
                periodo_ano = match.group(1).strip()
                codigo = match.group(2).strip()
                nome_bruto = match.group(3).strip()
                ch_efetiva = match.group(4).strip()
                freq = match.group(6).strip()
                media = match.group(8).strip()
                situacao = match.group(9).strip()
                
                # Limpeza final no Nome (Removendo quebras de linha e siglas de professor, se sobrar)
                nome = re.sub(r'\s{2,}', ' ', nome_bruto).strip()
                
                if nome and len(nome) > 5 and 'Componente Curricular' not in nome:
                    
                    # 3. Cria o HistoricoItem
                    HistoricoItens.objects.create(
                        historico=historico,
                        disciplina_nome=nome,
                        disciplina_sigla=codigo, 
                        ch=int(ch_efetiva) if ch_efetiva.isdigit() else 0,
                        # Trata a vírgula e converte para Decimal/Float
                        nota=media.replace(',', '.') if media and media.replace(',', '.').replace('.', '').isdigit() else None, 
                        frequencia=int(freq.replace(',', '.')) if freq and freq.replace(',', '.').replace('.', '').isdigit() else None,
                        status_disciplina=situacao,
                        semestre_cursado=periodo_ano if periodo_ano else 'N/A' # Usa o periodo do RegEx
                    )
                    dados_disciplinas.append({'nome': nome, 'status': situacao})
        
        # 4. Atualiza o status do Histórico para CONCLUIDO
        historico.status = 'CONCLUIDO'
        historico.save()
        
    except PyPDF2.errors.PdfReadError as e:
        print(f"!!! ERRO FATAL: PDF corrompido ou protegido: {e} !!!")
        historico.status = 'ERRO'
        historico.save()
        return None
    except Exception as e:
        print(f"!!! ERRO INESPERADO DURANTE O PROCESSAMENTO: {e} !!!")
        historico.status = 'ERRO'
        historico.save()
        return None
    
    return {'id': historico.pk, 'aluno_nome': aluno_obj.nome, 'disciplinas_processadas': len(dados_disciplinas)}


# ====================================================================
# VIEWS DA APLICAÇÃO UPLOAD
# ... (O restante das views permanece o mesmo)
# ====================================================================

@login_required
def importar_historico(request):
# ... (conteúdo da view omitido por brevidade)
    historicos_list = Historico.objects.all().order_by('-data_upload')
    
    # Lógica de Paginação
    paginator = Paginator(historicos_list, 10)
    page = request.GET.get('page')
    try:
        historicos = paginator.page(page)
    except PageNotAnInteger:
        historicos = paginator.page(1)
    except EmptyPage:
        historicos = paginator.page(paginator.num_pages)

    return render(request, 'upload/importar_historico.html', {
        'historicos': historicos,
        'form': HistoricoUploadForm(),
    })


@login_required
def importar_historico_action(request: HttpRequest):
# ... (conteúdo da view omitido por brevidade)
    if request.method != 'POST':
        return redirect('upload:importar_historico')
        
    form = HistoricoUploadForm(request.POST, request.FILES)
    
    if form.is_valid():
        pdf_file = request.FILES.get('pdf_file') 
        data = form.cleaned_data
        
        if not pdf_file:
            return JsonResponse({"erro": "Arquivo PDF é obrigatório."}, status=400)
        
        # 1. Cria ou Obtém o Aluno
        # Usa get_or_create para evitar duplicidade de matrícula (boa prática)
        aluno, created = Aluno.objects.get_or_create(
            matricula=data['matricula'],
            defaults={
                'nome': data['nome'],
                'curso': data['curso'],
                'ano_ingresso': data['ano_ingresso'],
            }
        )
        
        # Se o aluno já existe, apenas atualiza (opcional, mas bom para consistência)
        if not created:
             aluno.nome = data['nome']
             aluno.curso = data['curso']
             aluno.ano_ingresso = data['ano_ingresso']
             aluno.save()

        # Atribuir o usuário logado ao aluno/histórico
        aluno.usuario = request.user 

        # 2. Processa o PDF
        # Utilizamos transaction.atomic() para garantir que, se o PDF falhar,
        # o histórico e os itens não sejam criados incompletos.
        try:
            with transaction.atomic():
                dados_processados = processar_historico_pdf(pdf_file, aluno)
            
            if dados_processados and Historico.objects.filter(pk=dados_processados['id'], status='CONCLUIDO').exists():
                return JsonResponse({
                    "sucesso": True, 
                    "mensagem": f"Histórico de {dados_processados['aluno_nome']} processado com sucesso!",
                    "historico_id": dados_processados['id']
                }, status=200)
            else:
                # O processamento falhou, mas a função cuidou do status='ERRO'
                return JsonResponse({"erro": "Falha na leitura ou no RegEx do PDF. Verifique os logs."}, status=500)

        except Exception as e:
             # Erro de banco de dados ou exceção inesperada
            print(f"Erro na transação de upload: {e}")
            return JsonResponse({"erro": "Erro interno ao salvar os dados."}, status=500)

    else:
        # Erro de formulário (ex: campo não preenchido)
        return JsonResponse({"erro": "Dados inválidos no formulário.", "detalhes": form.errors.as_json()}, status=400)


@login_required
def consultar_historicos(request):
# ... (conteúdo da view omitido por brevidade)
    historicos_list = Historico.objects.all().order_by('-data_upload')
    
    # Implementação de filtro básico
    matricula = request.GET.get('matricula')
    if matricula:
        historicos_list = historicos_list.filter(aluno__matricula__icontains=matricula)

    # Lógica de Paginação
    paginator = Paginator(historicos_list, 10)
    page = request.GET.get('page')
    try:
        historicos = paginator.page(page)
    except PageNotAnInteger:
        historicos = paginator.page(1)
    except EmptyPage:
        historicos = paginator.page(paginator.num_pages)

    return render(request, 'upload/consultar_historicos.html', {
        'historicos': historicos
    })


@login_required
def consultar_historico_detalhe(request, pk):
# ... (conteúdo da view omitido por brevidade)
    historico = get_object_or_404(Historico.objects.select_related('aluno'), pk=pk)
    itens = HistoricoItens.objects.filter(historico=historico)
    
    # A próxima funcionalidade (IA) usará este ponto
    # disciplinas_pendentes = logica_ia(historico) 

    return render(request, 'upload/consultar_historico_detalhe.html', {
        'historico': historico,
        'itens': itens,
        # 'disciplinas_pendentes': disciplinas_pendentes, # Futura implementação
    })


@login_required
def excluir_historico(request, pk):
# ... (conteúdo da view omitido por brevidade)
    historico = get_object_or_404(Historico, pk=pk)
    if request.method == 'POST':
        # Ao deletar o Historico, todos os HistoricoItens relacionados são 
        # deletados automaticamente devido ao models.CASCADE
        historico.delete() 
        return redirect('upload:consultar_historicos')
        
    # Renderiza um template de confirmação (se você for criar um)
    # Por enquanto, redireciona para a lista
    return redirect('upload:consultar_historicos') 
    
# Implementações futuras:
# @login_required
# def editar_historico(request, pk):
#     pass
#
# @login_required
# def consultar_analise_ia(request, pk):
#     pass
