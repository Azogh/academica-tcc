from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction 
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

# Modelos que vamos consultar
from upload.models import Historico, HistoricoItens
from core.models import Disciplinas, MatrizCurricular, Horario
# Modelos que vamos salvar
from .models import Analise, AnaliseItens

# O "Cérebro" (IA)
from . import gemini_analytics 

# --- FUNÇÕES HELPER (MANTIDAS IGUAIS) ---
def serializar_historico(historico_obj):
    itens = HistoricoItens.objects.filter(historico=historico_obj)
    return json.dumps([
        {
            "sigla": item.disciplina_sigla,
            "status": item.status_disciplina,
            "semestre_cursado": item.semestre_cursado
        }
        for item in itens if item.status_disciplina in ['APR', 'CUMP', 'DISP', 'REP', 'REPF']
    ])

def serializar_matriz(curso_nome):
    try:
        matriz = MatrizCurricular.objects.filter(curso=curso_nome).first()
        if not matriz: return "[]"
        disciplinas = Disciplinas.objects.filter(matriz_curricular=matriz).prefetch_related('pre_requisitos')
        return json.dumps([
            {
                "id": d.pk,
                "sigla": d.sigla,
                "nome": d.nome,
                "semestre_ideal": d.semestre,
                "pre_requisitos": [pr.sigla for pr in d.pre_requisitos.all()] 
            }
            for d in disciplinas
        ])
    except Exception:
        return "[]"

def serializar_horarios():
    horarios = Horario.objects.select_related('disciplina').all()
    return json.dumps([
        {
            "id": h.pk,
            "sigla_disciplina": h.disciplina.sigla,
            "dia_semana": h.dia_semana,
            "periodo": h.periodo
        }
        for h in horarios
    ])

# -------------------------------------------------------------------
# VIEWS
# -------------------------------------------------------------------

@login_required
def analisar_historico(request, historico_pk):
    historico = get_object_or_404(Historico.objects.select_related('aluno'), pk=historico_pk)
    
    if request.method == 'POST':
        tipo_analise = request.POST.get('tipo_analise')
        dias_excluidos_lista = request.POST.getlist('dias_excluidos') 
        dias_excluidos_str = ",".join(dias_excluidos_lista)
        
        analise = Analise.objects.create(
            historico=historico,
            coordenador=request.user,
            tipo_analise=tipo_analise,
            dias_excluidos=dias_excluidos_str,
            status='PENDENTE'
        )

        try:
            historico_json = serializar_historico(historico)
            matriz_json = serializar_matriz(historico.aluno.curso)
            horarios_json = serializar_horarios()

            lista_ids_horarios = gemini_analytics.gerar_analise_grade(
                historico_json,
                matriz_json,
                horarios_json,
                tipo_analise,
                dias_excluidos_lista
            )

            if lista_ids_horarios is None:
                raise Exception("Gemini não retornou sugestões.")

            with transaction.atomic():
                horarios_sugeridos = Horario.objects.filter(pk__in=lista_ids_horarios)
                
                # (Opcional: Se quiser permitir salvar vazio, remova a validação abaixo)
                # if not horarios_sugeridos.exists() and lista_ids_horarios:
                #    raise Exception("IDs inválidos.")

                for horario_obj in horarios_sugeridos:
                    AnaliseItens.objects.create(
                        analise=analise,
                        disciplina=horario_obj.disciplina,
                        dia_semana=horario_obj.dia_semana,
                        periodo=horario_obj.periodo 
                    )
            
            analise.status = 'CONCLUIDO'
            analise.save()
            messages.success(request, "Análise realizada com sucesso! Confira a sugestão abaixo.")
            return redirect('analytics:consultar_analise', analise_pk=analise.pk)

        except Exception as e:
            print(f"Erro durante a análise: {e}")
            analise.status = 'ERRO'
            analise.save()
            msg_erro = f"Ocorreu um erro: {str(e)}"
            if "404" in str(e) and "models" in str(e):
                msg_erro = "Erro de Configuração: Modelo Gemini não encontrado."
            messages.error(request, msg_erro)
            return redirect('analytics:analisar_historico', historico_pk=historico_pk)

    return render(request, 'analytics/analisar_historico.html', {'historico': historico})


login_required
def consultar_analise(request, analise_pk):
    analise = get_object_or_404(Analise, pk=analise_pk)
    
    # Busca todos os itens sugeridos para esta análise
    itens = AnaliseItens.objects.filter(analise=analise).select_related('disciplina')
    
    # --- LÓGICA DE MONTAGEM DA GRADE ---
    
    # 1. Cria um "Mapa" rápido para achar disciplinas por (periodo, dia)
    # Chave: ('1-2', 'SEG') -> Valor: Objeto AnaliseItem
    itens_map = {(i.periodo, i.dia_semana): i for i in itens}
    
    # 2. Define a estrutura da tabela
    # (Se os seus periodos no banco forem diferentes de '1-2', ajuste aqui)
    periodos_definidos = ['1-2', '3-4', '5-6', '7-8', 'N1-N2', 'N3-N4'] 
    dias_semana = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
    
    grade_montada = []
    
    for p in periodos_definidos:
        # Para cada período (linha), criamos uma lista de células
        linha_dados = {'label': p, 'celulas': []}
        
        # Verifica se tem alguma aula nesse período em QUALQUER dia 
        # (pra não mostrar linhas vazias desnecessárias, opcional)
        tem_aula_neste_periodo = False
        
        for d in dias_semana:
            item = itens_map.get((p, d)) # Tenta pegar a aula desse dia/hora
            linha_dados['celulas'].append(item)
            if item:
                tem_aula_neste_periodo = True
        
        # Só adiciona a linha na visualização se tiver pelo menos uma aula
        # OU se forem os periodos principais (1-2 e 3-4) para não ficar muito vazio
        if tem_aula_neste_periodo or p in ['1-2', '3-4']:
            grade_montada.append(linha_dados)

    return render(request, 'analytics/consultar_analise.html', {
        'analise': analise,
        'grade_montada': grade_montada,
        'dias_semana': dias_semana
    })



@login_required
def editar_analise(request, analise_pk):
    """
    View 3: Permite editar a grade sugerida manualmente.
    """
    analise = get_object_or_404(Analise, pk=analise_pk)

    if request.method == 'POST':
        # 1. Pega a lista de IDs de horários que o usuário marcou no checkbox
        horarios_selecionados_ids = request.POST.getlist('horarios_selecionados')
        
        try:
            with transaction.atomic():
                # 2. Apaga TODAS as sugestões antigas dessa análise
                AnaliseItens.objects.filter(analise=analise).delete()
                
                # 3. Cria as novas baseadas no que o usuário marcou
                novos_horarios = Horario.objects.filter(pk__in=horarios_selecionados_ids)
                
                for h in novos_horarios:
                    AnaliseItens.objects.create(
                        analise=analise,
                        disciplina=h.disciplina,
                        dia_semana=h.dia_semana,
                        periodo=h.periodo
                    )
            
            messages.success(request, "Grade atualizada com sucesso!")
            return redirect('analytics:consultar_analise', analise_pk=analise.pk)
            
        except Exception as e:
            messages.error(request, f"Erro ao salvar alterações: {e}")
    
    # --- PREPARAÇÃO PARA O GET (Exibir o formulário) ---
    
    # 1. Pega todos os horários disponíveis no sistema (para o usuário poder escolher)
    # TODO: Idealmente filtrar pelo curso do aluno
    todos_horarios = Horario.objects.select_related('disciplina').order_by('dia_semana', 'periodo')
    
    # 2. Descobre quais já estão na análise (para marcar o checkbox como 'checked')
    itens_atuais = AnaliseItens.objects.filter(analise=analise)
    
    # Cria um conjunto (set) de chaves unicas para identificar o que está marcado
    # Chave: (disciplina_id, dia, periodo)
    itens_marcados_signature = set()
    for item in itens_atuais:
        itens_marcados_signature.add((item.disciplina.id, item.dia_semana, item.periodo))
    
    # 3. Adiciona um atributo '.marcado' em cada horário para o template saber
    for h in todos_horarios:
        if (h.disciplina.id, h.dia_semana, h.periodo) in itens_marcados_signature:
            h.marcado = True
        else:
            h.marcado = False

    return render(request, 'analytics/editar_analise.html', {
        'analise': analise,
        'todos_horarios': todos_horarios
    })


@login_required
def listar_analises(request):
    analises = Analise.objects.select_related('historico__aluno').order_by('-data_criacao')
    return render(request, 'analytics/listar_analises.html', {'analises': analises})

@require_POST
@login_required
def excluir_analise(request, analise_pk):
    analise = get_object_or_404(Analise, pk=analise_pk, coordenador=request.user)
    analise.delete()
    return redirect('analytics:listar_analises')