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

def serializar_horarios(dias_excluidos_lista=None):
    """
    Retorna os horários disponíveis, mas com uma regra de ouro:
    Se uma disciplina de 4 créditos tem aulas em dias diferentes,
    e UM desses dias está excluído, a disciplina INTEIRA é removida.
    """
    if dias_excluidos_lista is None:
        dias_excluidos_lista = []
        
    # Busca todos os horários
    horarios = Horario.objects.select_related('disciplina', 'turma').all()
    
    # 1. Agrupa por (Turma, Disciplina) para identificar os "pacotes"
    # Chave: (turma_id, disciplina_id) -> Valor: Lista de objetos Horario
    grupos_disciplinas = {}
    for h in horarios:
        chave = (h.turma.id, h.disciplina.id)
        if chave not in grupos_disciplinas:
            grupos_disciplinas[chave] = []
        grupos_disciplinas[chave].append(h)
    
    horarios_validos = []
    
    # 2. Valida cada grupo
    for chave, lista_horarios in grupos_disciplinas.items():
        # Verifica se ALGUM horário desse grupo cai num dia excluído
        grupo_condenado = False
        for h in lista_horarios:
            if h.dia_semana in dias_excluidos_lista:
                grupo_condenado = True
                break
        
        # Se o grupo não foi condenado, adiciona TODOS os horários dele na lista final
        if not grupo_condenado:
            for h in lista_horarios:
                horarios_validos.append({
                    "id": h.pk,
                    "sigla_disciplina": h.disciplina.sigla,
                    "dia_semana": h.dia_semana,
                    "periodo": h.periodo,
                    # Passamos o ID do grupo para a IA saber que devem ir juntos (opcional, mas ajuda)
                    "grupo_id": f"T{h.turma.id}_D{h.disciplina.id}" 
                })

    return json.dumps(horarios_validos)

# -------------------------------------------------------------------
# VIEWS
# -------------------------------------------------------------------

@login_required
def analisar_historico(request, historico_pk):
    # O select_related('aluno') puxa os dados do aluno numa única query (otimização)
    historico = get_object_or_404(Historico.objects.select_related('aluno'), pk=historico_pk)
    
    if request.method == 'POST':
        tipo_analise = request.POST.get('tipo_analise')
        # getlist pega todos os checkboxes marcados com o mesmo nome
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
            
            # ATENÇÃO: Aqui assume que historico.aluno tem um campo 'curso'. 
            # Se der erro, verifique se o modelo Usuario tem 'curso'.
            curso_aluno = getattr(historico.aluno, 'curso', None) 
            # Se não achar no aluno, tenta achar no próprio histórico (depende do seu model)
            if not curso_aluno and hasattr(historico, 'curso'):
                curso_aluno = historico.curso
                
            matriz_json = serializar_matriz(curso_aluno)
            horarios_json = serializar_horarios(dias_excluidos_lista)

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


@login_required  # <--- CORREÇÃO AQUI: ADICIONADO O @
def consultar_analise(request, analise_pk):
    analise = get_object_or_404(Analise, pk=analise_pk)
    
    # Busca todos os itens sugeridos para esta análise
    itens = AnaliseItens.objects.filter(analise=analise).select_related('disciplina')
    
    # --- LÓGICA DE MONTAGEM DA GRADE ---
    itens_map = {(i.periodo, i.dia_semana): i for i in itens}
    
    periodos_definidos = ['1-2', '3-4', '5-6', '7-8', 'N1-N2', 'N3-N4'] 
    dias_semana = ['SEG', 'TER', 'QUA', 'QUI', 'SEX']
    
    grade_montada = []
    
    for p in periodos_definidos:
        linha_dados = {'label': p, 'celulas': []}
        tem_aula_neste_periodo = False
        
        for d in dias_semana:
            item = itens_map.get((p, d)) 
            linha_dados['celulas'].append(item)
            if item:
                tem_aula_neste_periodo = True
        
        if tem_aula_neste_periodo or p in ['1-2', '3-4']:
            grade_montada.append(linha_dados)

    return render(request, 'analytics/consultar_analise.html', {
        'analise': analise,
        'grade_montada': grade_montada,
        'dias_semana': dias_semana
    })


@login_required
def editar_analise(request, analise_pk):
    analise = get_object_or_404(Analise, pk=analise_pk)

    if request.method == 'POST':
        horarios_selecionados_ids = request.POST.getlist('horarios_selecionados')
        
        try:
            with transaction.atomic():
                # --- NOVA VALIDAÇÃO DE CONFLITOS ---
                novos_horarios = Horario.objects.filter(pk__in=horarios_selecionados_ids)
                
                # Verifica duplicidade de (dia, periodo)
                slots_ocupados = set()
                for h in novos_horarios:
                    slot_signature = (h.dia_semana, h.periodo)
                    
                    if slot_signature in slots_ocupados:
                        # Achou conflito!
                        raise Exception(f"Conflito detectado: Você selecionou duas disciplinas para {h.dia_semana} no período {h.periodo}.")
                    
                    slots_ocupados.add(slot_signature)
                # -----------------------------------

                # Se passou, salva tudo
                AnaliseItens.objects.filter(analise=analise).delete()
                
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
            messages.error(request, f"Erro ao salvar: {e}")
    
    todos_horarios = Horario.objects.select_related('disciplina').order_by('dia_semana', 'periodo')
    itens_atuais = AnaliseItens.objects.filter(analise=analise)
    
    itens_marcados_signature = set()
    for item in itens_atuais:
        itens_marcados_signature.add((item.disciplina.id, item.dia_semana, item.periodo))
    
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