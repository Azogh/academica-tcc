import io
import json
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction 
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import FileResponse

# Imports para PDF (ReportLab)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

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
    if dias_excluidos_lista is None: dias_excluidos_lista = []
    
    query = Horario.objects.select_related('disciplina', 'turma', 'disciplina__matriz_curricular__curso')
    
    if curso_nome:
        query = query.filter(disciplina__matriz_curricular__curso__nome=curso_nome)
        
    horarios = query.all()
    
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
            curso_aluno = getattr(historico.aluno, 'curso', None) 
            matriz_json = serializar_matriz(curso_aluno)
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
    itens = AnaliseItens.objects.filter(analise=analise).select_related('disciplina')
    
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
                novos_horarios = Horario.objects.filter(pk__in=horarios_selecionados_ids)
                
                slots_ocupados = set()
                for h in novos_horarios:
                    slot_signature = (h.dia_semana, h.periodo)
                    
                    if slot_signature in slots_ocupados:
                        raise Exception(f"Conflito detectado: Você selecionou duas disciplinas para {h.dia_semana} no período {h.periodo}.")
                    
                    slots_ocupados.add(slot_signature)

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
    
    todos_horarios = Horario.objects.select_related('disciplina', 'turma', 'disciplina__matriz_curricular__curso')
    
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

@login_required
def gerar_pdf_solicitacao(request, analise_id):
    """
    Gera o PDF de solicitação de matrícula (Rematrícula) com texto formal.
    """
    # 1. Recuperar dados
    analise = get_object_or_404(Analise, pk=analise_id)
    aluno = analise.historico.aluno
    coordenador = request.user
    
    itens = AnaliseItens.objects.filter(analise=analise).select_related('disciplina')
    
    # Agrupando disciplinas únicas
    disciplinas_unicas = {}
    for item in itens:
        if item.disciplina.pk not in disciplinas_unicas:
            disciplinas_unicas[item.disciplina.pk] = item.disciplina

    # 2. Configurar Canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    
    # --- Título ---
    c.setTitle(f"Rematricula_{aluno.matricula}")
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(largura / 2, altura - 50, "REQUERIMENTO DE REMATRÍCULA")
    
    # Subtítulo com Semestre
    c.setFont("Helvetica", 12)
    semestre_atual = f"{datetime.now().year}/{'1' if datetime.now().month < 7 else '2'}"
    c.drawCentredString(largura / 2, altura - 70, f"Semestre Letivo {semestre_atual}")

    # Linha divisória
    c.setLineWidth(1)
    c.line(50, altura - 85, largura - 50, altura - 85)

    # --- TEXTO FORMAL (VERBOSO) ---
    # Configurações de posição
    inicio_texto_y = altura - 120
    espaco_entre_linhas = 18
    
    # Tratamento de dados
    ano_inicio = aluno.matricula[:4] if aluno.matricula and len(aluno.matricula) >= 4 else "____"
    nome_aluno = aluno.nome.upper() if aluno.nome else "ALUNO"
    
    # Linha 1: Identificação do Nome
    c.setFont("Helvetica", 12)
    c.drawString(50, inicio_texto_y, "Eu,")
    
    # Nome em Negrito
    c.setFont("Helvetica-Bold", 12)
    c.drawString(75, inicio_texto_y, f"{nome_aluno},")
    
    # Linha 2: Matrícula e Ano
    inicio_texto_y -= espaco_entre_linhas
    c.setFont("Helvetica", 12)
    texto_linha2 = f"regularmente matriculado(a) sob o nº {aluno.matricula}, com ingresso em {ano_inicio},"
    c.drawString(50, inicio_texto_y, texto_linha2)
    
    # Linha 3: Solicitação
    inicio_texto_y -= espaco_entre_linhas
    texto_linha3 = f"venho por meio deste solicitar a minha rematrícula para o semestre {semestre_atual},"
    c.drawString(50, inicio_texto_y, texto_linha3)
    
    # Linha 4: Conclusão
    inicio_texto_y -= espaco_entre_linhas
    c.drawString(50, inicio_texto_y, "nas disciplinas relacionadas a seguir:")

    # --- Tabela de Disciplinas ---
    # Ajusta o y_inicial da tabela baseando-se onde o texto terminou
    y_inicial = inicio_texto_y - 40
    
    # Cabeçalho da Tabela
    c.setFillColor(colors.lightgrey)
    c.rect(50, y_inicial - 5, largura - 100, 20, fill=True, stroke=False)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    
    c.drawString(60, y_inicial, "CÓDIGO")
    c.drawString(150, y_inicial, "DISCIPLINA")
    c.drawString(480, y_inicial, "CH")

    y = y_inicial - 25
    c.setFont("Helvetica", 10)

    for disc in disciplinas_unicas.values():
        if y < 150:
            c.showPage()
            y = altura - 50
            c.setFont("Helvetica", 10)

        # Dados da disciplina
        codigo = disc.codigo if disc.codigo else "---"
        nome = disc.nome
        val_ch = getattr(disc, 'carga_horaria', getattr(disc, 'ch', getattr(disc, 'horas', getattr(disc, 'creditos', '--'))))
        ch = f"{val_ch}h"

        c.drawString(60, y, str(codigo))
        c.drawString(150, y, nome)
        c.drawString(480, y, ch)
        
        c.setLineWidth(0.5)
        c.setStrokeColor(colors.lightgrey)
        c.line(50, y - 5, largura - 50, y - 5)
        
        y -= 20

    # --- Assinaturas ---
    y_assinaturas = 100
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)

    # Coordenador
    c.line(50, y_assinaturas, 250, y_assinaturas)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_assinaturas - 15, "Coordenador(a)")
    c.setFont("Helvetica", 9)
    coord_nome = coordenador.get_full_name() or coordenador.username
    c.drawString(50, y_assinaturas - 28, coord_nome.upper())

    # Aluno
    c.line(300, y_assinaturas, 500, y_assinaturas)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(300, y_assinaturas - 15, "Aluno(a) Solicitante")
    c.setFont("Helvetica", 9)
    c.drawString(300, y_assinaturas - 28, nome_aluno)

    # Rodapé
    c.setFont("Helvetica-Oblique", 8)
    data_hoje = datetime.now().strftime("%d/%m/%Y às %H:%M")
    c.drawCentredString(largura / 2, 30, f"Documento gerado pelo sistema Acadêmica em {data_hoje}")

    c.showPage()
    c.save()
    buffer.seek(0)

    filename = f"rematricula_{aluno.matricula}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=filename)