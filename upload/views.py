# Em upload/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from .forms import HistoricoUploadForm

# Importa os modelos do app 'historicos'
# Importa os modelos do app local (upload)
from .models import Aluno, Historico, HistoricoItens# from core.models import Disciplinas  

# Importa sua nova função do Gemini
from .gemini_pdf import extrair_disciplinas_gemini

# -------------------------------------------------------------------
# VIEW: Página de upload / listagem
# -------------------------------------------------------------------
@login_required
def importar_historico(request):
    # Lista apenas os históricos (uploads)
    historicos = Historico.objects.select_related('aluno').order_by('-data_upload')

    return render(request, 'upload/importar_historico.html', {
        'historicos': historicos,
        'form': HistoricoUploadForm(),
    })

# -------------------------------------------------------------------
# VIEW: Processamento do upload via Gemini (LÓGICA CORRIGIDA)
# -------------------------------------------------------------------
@login_required
def importar_historico_action(request):
    if request.method != 'POST':
        return redirect('upload:importar_historico')

    form = HistoricoUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse({"erro": "Formulário inválido", "detalhes": form.errors.as_json()}, status=400)

    pdf_file = request.FILES.get("pdf_file")

    if not pdf_file:
        return JsonResponse({"erro": "Arquivo PDF obrigatório"}, status=400)

    data = form.cleaned_data

    # --------------------------------------------
    # PASSO 1: Cria ou atualiza o ALUNO
    # --------------------------------------------
    aluno, created = Aluno.objects.get_or_create(
        matricula=data["matricula"],
        defaults={
            "nome": data["nome"],
            "curso": data["curso"],
            "ano_ingresso": data["ano_ingresso"],
        }
    )
    
    # Se o aluno já existia, apenas atualiza os dados
    if not created:
         aluno.nome = data["nome"]
         aluno.curso = data["curso"]
         aluno.ano_ingresso = data["ano_ingresso"]
         aluno.save()

    # --------------------------------------------
    # PASSO 2: Cria o HISTÓRICO (o upload)
    # --------------------------------------------
    historico = Historico.objects.create(
        aluno=aluno, # Linka ao aluno recém-criado/encontrado
        usuario=request.user, # Usuário que fez o upload
        status="PENDENTE",
        arquivo_original=pdf_file
    )

    # --------------------------------------------
    # PASSO 3: PROCESSA PDF COM GEMINI
    # --------------------------------------------
    try:
        # Usamos 'atomic' para garantir que, se o Gemini falhar, 
        # o 'historico' (status PENDENTE) ainda seja salvo, mas os itens não.
        with transaction.atomic():

            pdf_file.seek(0)
            # Chama sua função de extração
            dados = extrair_disciplinas_gemini(pdf_file)

            if not dados:
                historico.status = "ERRO_GEMINI"
                historico.save()
                return JsonResponse({"erro": "Falha ao extrair disciplinas com Gemini. Verifique os logs."}, status=500)

            # --------------------------------------------
            # PASSO 4: Salva os Itens do Histórico
            # --------------------------------------------
            for item in dados:
                HistoricoItens.objects.create(
                    historico=historico,
                    # Usar .get() é mais seguro caso o Gemini omita um campo
                    disciplina_nome=item.get("nome") or "N/A",
                    disciplina_sigla=item.get("codigo") or "N/A",
                    ch=item.get("ch") or 0,
                    nota=item.get("media"), # O Gemini já deve mandar 'null'
                    frequencia=item.get("frequencia"), # O Gemini já deve mandar 'null'
                    status_disciplina=item.get("situacao") or "N/A",
                    semestre_cursado=item.get("periodo") or "N/A"
                )

            # Se tudo deu certo, marca como CONCLUIDO
            historico.status = "CONCLUIDO"
            historico.save()

            return JsonResponse({
                "sucesso": True,
                "mensagem": f"Histórico de {aluno.nome} processado com sucesso!",
                "aluno_nome": aluno.nome,
                "disciplinas_salvas": len(dados),
                "historico_id": historico.pk
            })

    except Exception as e:
        historico.status = "ERRO_INTERNO"
        historico.save()
        print(f"Erro ao salvar histórico: {e}")
        return JsonResponse({"erro": "Erro interno no servidor"}, status=500)

# -------------------------------------------------------------------
# VIEW: Lista geral (Provavelmente redundante, 'importar_historico' já faz)
# -------------------------------------------------------------------
@login_required
def consultar_historicos(request):
    historicos = Historico.objects.select_related('aluno').order_by('-data_upload')
    return render(request, 'upload/consultar_historicos.html', {
        'historicos': historicos
    })

# -------------------------------------------------------------------
# VIEW: Detalhe
# -------------------------------------------------------------------
@login_required
def consultar_historico_detalhe(request, pk):
    historico = get_object_or_404(Historico.objects.select_related('aluno'), pk=pk)
    # Pega os itens ordenados pelo semestre
    itens = HistoricoItens.objects.filter(historico=historico).order_by('semestre_cursado', 'disciplina_nome')

    return render(request, 'upload/consultar_historico_detalhe.html', {
        'historico': historico,
        'itens': itens
    })

# -------------------------------------------------------------------
# VIEW: Remoção
# -------------------------------------------------------------------
@login_required
def excluir_historico(request, pk):
    # Apenas POST para segurança
    if request.method == 'POST':
        historico = get_object_or_404(Historico, pk=pk)
        historico.delete()
    return redirect('upload:consultar_historicos')