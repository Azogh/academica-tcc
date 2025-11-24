import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.db.models import Q

# Certifique-se de que o forms.py existe com esse formulário
from .forms import UploadHistoricoForm
from .models import Aluno, Historico, HistoricoItens

# Sua função de extração via Gemini
from .gemini_pdf import extrair_disciplinas_gemini

@login_required
def importar_historico(request):
    if request.method == 'POST':
        form = UploadHistoricoForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # 1. Salva o Aluno
                aluno = form.save()
                
                # 2. Cria o Histórico
                arquivo_pdf = form.cleaned_data['arquivo']
                historico = Historico.objects.create(
                    aluno=aluno,
                    usuario=request.user,
                    arquivo_original=arquivo_pdf,
                    status='PENDENTE'
                )
                
                # 3. CHAMA A IA IMEDIATAMENTE
                # Garante ponteiro no início do arquivo
                arquivo_pdf.seek(0)
                
                # Chama o Gemini
                dados_extraidos = extrair_disciplinas_gemini(arquivo_pdf)

                if dados_extraidos:
                    # 4. Salva no Banco
                    with transaction.atomic():
                        # Limpa itens antigos se houver (para evitar duplicidade em reprocessamento)
                        HistoricoItens.objects.filter(historico=historico).delete()

                        count = 0
                        for item in dados_extraidos:
                            # Tratamento de nota
                            nota = item.get('media')
                            if isinstance(nota, str): nota = nota.replace(',', '.')
                            if nota == 'null' or nota == '': nota = None
                            
                            # Tratamento de frequencia
                            freq = item.get('frequencia')
                            if freq == 'null' or freq == '': freq = None

                            # --- CORREÇÃO DO ERRO NOT NULL (Semestre) ---
                            semestre = item.get('periodo')
                            # Se for None, string vazia ou 'null', força um valor padrão '-'
                            if not semestre or semestre == 'null': 
                                semestre = '-'

                            HistoricoItens.objects.create(
                                historico=historico,
                                disciplina_nome=item.get('nome', 'N/A'),
                                disciplina_sigla=item.get('codigo', '---'),
                                ch=item.get('ch', 0) or 0,
                                nota=nota,
                                frequencia=freq,
                                status_disciplina=item.get('situacao', 'N/A'),
                                semestre_cursado=semestre # Agora blindado contra None
                            )
                            count += 1

                    historico.status = 'CONCLUIDO'
                    historico.save()
                    messages.success(request, f"Sucesso! {count} disciplinas importadas.")
                
                else:
                    historico.status = 'ERRO'
                    historico.save()
                    messages.error(request, "Falha: A IA não conseguiu ler os dados. Tente novamente em alguns minutos.")

            except Exception as e:
                # Se a variável 'historico' foi criada, marca como erro
                if 'historico' in locals():
                    historico.status = 'ERRO'
                    historico.save()
                print(f"Erro interno na view: {e}")
                messages.error(request, f"Erro interno no processamento: {e}")
            
            return redirect('upload:importar_historico')
            
    else:
        form = UploadHistoricoForm()

    ultimo_historico = Historico.objects.filter(
        usuario=request.user
    ).order_by('-data_upload').first()

    return render(request, 'upload/importar_historico.html', {
        'form': form,
        'ultimo_historico': ultimo_historico
    })

# --- Outras Views (Consulta, Detalhe, Exclusão) ---

@login_required
def consultar_historicos(request):
    query = request.GET.get('q', '') 
    historicos_list = Historico.objects.select_related('aluno').order_by('-data_upload')
    if query:
        historicos_list = historicos_list.filter(
            Q(aluno__nome__icontains=query) | Q(aluno__matricula__icontains=query)
        )
    return render(request, 'upload/consultar_historicos.html', {'historicos': historicos_list, 'query': query})

@login_required
def consultar_historico_detalhe(request, pk):
    historico = get_object_or_404(Historico.objects.select_related('aluno'), pk=pk)
    itens = HistoricoItens.objects.filter(historico=historico).order_by('semestre_cursado', 'disciplina_nome')
    return render(request, 'upload/consultar_historico_detalhe.html', {'historico': historico, 'itens': itens})

@login_required
def excluir_historico(request, pk):
    if request.method == 'POST':
        historico = get_object_or_404(Historico, pk=pk)
        historico.delete()
    return redirect('upload:consultar_historicos')