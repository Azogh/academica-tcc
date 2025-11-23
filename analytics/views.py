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

# --- FUNÇÕES HELPER ---

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
        # AJUSTE 1: Como 'curso' agora é ForeignKey, usamos curso__nome
        matriz = MatrizCurricular.objects.filter(curso__nome=curso_nome).first()
        
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

def serializar_horarios(dias_excluidos_lista=None, curso_nome=None):
    """
    Retorna os horários disponíveis filtrados por curso e dias excluídos.
    """
    if dias_excluidos_lista is None: dias_excluidos_lista = []
    
    # Busca todos os horários trazendo as relações necessárias
    # AJUSTE 2: Trazemos também o curso da matriz para poder filtrar
    query = Horario.objects.select_related('disciplina', 'turma', 'disciplina__matriz_curricular__curso')
    
    if curso_nome:
        # AJUSTE 3: Filtra apenas horários de disciplinas que pertencem ao curso do aluno
        query = query.filter(disciplina__matriz_curricular__curso__nome=curso_nome)
        
    horarios = query.all()
    
    # Lógica de agrupar horários (para disciplinas de 4 créditos)
    grupos_disciplinas = {}
    for h in horarios:
        chave = (h.turma.id, h.disciplina.id)
        if chave not in grupos_disciplinas:
            grupos_disciplinas[chave] = []
        grupos_disciplinas[chave].append(h)
    
    horarios_validos = []
    
    for chave, lista_horarios in grupos_disciplinas.items():
        grupo_condenado = False
        for h in lista_horarios:
            if h.dia_semana in dias_excluidos_lista:
                grupo_condenado = True
                break
        
        if not grupo_condenado:
            for h in lista_horarios:
                horarios_validos.append({
                    "id": h.pk,
                    "sigla_disciplina": h.disciplina.sigla,
                    "dia_semana": h.dia_semana,
                    "periodo": h.periodo,
                    "grupo_id": f"T{h.turma.id}_D{h.disciplina.id}" 
                })

    return json.dumps(horarios_validos)

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
            
            # Tenta obter o curso do aluno
            curso_aluno = getattr(historico.aluno, 'curso', None) 
            
            matriz_json = serializar_matriz(curso_aluno)
            
            # AJUSTE 4: Passamos o curso_aluno para filtrar os horários
            horarios_json = serializar_horarios(dias_excluidos_lista, curso_aluno)

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


@login_required
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
                
                slots_ocupados = set()
                for h in novos_horarios:
                    slot_signature = (h.dia_semana, h.periodo)
                    
                    if slot_signature in slots_ocupados:
                        raise Exception(f"Conflito detectado: Você selecionou duas disciplinas para {h.dia_semana} no período {h.periodo}.")
                    
                    slots_ocupados.add(slot_signature)
                # -----------------------------------

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
    
    # AJUSTE 5: Filtra os horários disponíveis para edição também pelo curso
    todos_horarios = Horario.objects.select_related('disciplina', 'turma', 'disciplina__matriz_curricular__curso')
    
    # Tenta filtrar pelo curso do aluno da análise, se possível
    curso_aluno = getattr(analise.historico.aluno, 'curso', None)
    if curso_aluno:
        todos_horarios = todos_horarios.filter(disciplina__matriz_curricular__curso__nome=curso_aluno)
        
    todos_horarios = todos_horarios.order_by('dia_semana', 'periodo')
    
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