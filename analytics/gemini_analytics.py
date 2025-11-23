import os
import json
import sys
import traceback
from google import genai
from google.genai import types

# Tenta pegar a chave do ambiente
api_key = os.getenv("GOOGLE_API_KEY")

def normalizar_entrada(dados):
    if isinstance(dados, str):
        try:
            return json.loads(dados)
        except json.JSONDecodeError:
            return []
    return dados

def gerar_analise_grade(historico_json, matriz_json, horarios_json, tipo_analise, dias_excluidos):
    # Força saída imediata no terminal (sem buffer)
    sys.stdout.reconfigure(line_buffering=True)

    if not api_key:
        print("❌ ERRO: GOOGLE_API_KEY não encontrada.")
        return []

    try:
        print(f"\n--- 🤖 DEBUG INICIADO ({tipo_analise}) ---")
        
        # 1. Normalização
        historico_obj = normalizar_entrada(historico_json)
        matriz_obj = normalizar_entrada(matriz_json)
        horarios_obj = normalizar_entrada(horarios_json)

        qtd_turmas = len(horarios_obj) if horarios_obj else 0
        print(f"📊 Dados Recebidos: {qtd_turmas} turmas na oferta.")
        
        if qtd_turmas == 0:
            print("⚠️ AVISO: Nenhuma turma disponível para análise.")
            return []

        # 2. Preparação
        client = genai.Client(api_key=api_key)
        
        hist_str = json.dumps(historico_obj, separators=(',', ':'), ensure_ascii=False)
        matriz_str = json.dumps(matriz_obj, separators=(',', ':'), ensure_ascii=False)
        horarios_str = json.dumps(horarios_obj, separators=(',', ':'), ensure_ascii=False)

        schema = {
            "type": "OBJECT",
            "properties": {
                "sugestoes": {"type": "ARRAY", "items": {"type": "INTEGER"}},
                "raciocinio": {"type": "STRING"}
            },
            "required": ["sugestoes"]
        }

        # Prompt Reforçado com Lógica Anti-Choque
        prompt = f"""
        Você é um Coordenador Acadêmico RÍGIDO. Sua tarefa é montar a grade SEMESTRAL perfeita e SEM CONFLITOS.
        
        --- DADOS ---
        [HISTÓRICO]: {hist_str}
        [MATRIZ CURRICULAR]: {matriz_str}
        [OFERTA DE HORÁRIOS]: {horarios_str}
        [DIAS PROIBIDOS]: {dias_excluidos}

        --- REGRAS DE OURO (Falha = Zero) ---
        1. **ZERO CHOQUES DE HORÁRIO**: É fisicamente impossível o aluno estar em dois lugares ao mesmo tempo.
           - Verifique o campo 'dia_semana' e 'periodo' de cada escolha.
           - Se Turma A e Turma B são no mesmo dia e período (ex: SEG 1-2), **ESCOLHA APENAS UMA**.
           - Critério de desempate: Priorize a turma que o aluno REPROVOU anteriormente. Se ambas forem novas, priorize a do semestre mais baixo.

        2. **VÍNCULO DE 4 CRÉDITOS (PAR OBRIGATÓRIO)**:
           - Se uma disciplina tem o MESMO NOME mas ocorre em dias diferentes (ex: ID 10 na Terça e ID 20 na Quinta), você DEVE pegar AMBOS.
           - Se um dos horários tiver conflito, NÃO PEGUE NENHUM DOS DOIS. A disciplina deve ser cursada integralmente.

        3. **FILTRO DE STATUS**:
           - Jamais sugira disciplinas com status "APR" (Aprovado), "DISP" (Dispensado) ou "CUMP" (Cumprido).

        4. **PRÉ-REQUISITOS**:
           - Verifique a matriz. O aluno tem o pré-requisito cumprido? Se não, ignore a disciplina.

        --- INSTRUÇÃO FINAL ---
        Analise a lista de oferta. Identifique pares de conflito. Elimine o menos importante. Retorne a lista final limpa.
        
        SAÍDA JSON ESPERADA: {{ "sugestoes": [lista_de_ids_numericos], "raciocinio": "Texto explicativo curto" }}
        """

        # LISTA ATUALIZADA (Incluindo 2.0 Experimental e Flash padrão)
        modelos_para_tentar = [       # Mais robusto para lógica complexa
            "gemini-2.5-flash"   # Fallback legado
        ]
        
        response = None
        
        for modelo in modelos_para_tentar:
            try:
                print(f"📡 Tentando modelo: {modelo}...")
                response = client.models.generate_content(
                    model=modelo, 
                    contents=[types.Content(parts=[types.Part.from_text(text=prompt)])],
                    config=types.GenerateContentConfig(
                        temperature=0.0, # Zero criatividade para máxima precisão lógica
                        response_mime_type="application/json",
                        response_schema=schema
                    )
                )
                print(f"✅ Sucesso com o modelo: {modelo}")
                break
            except Exception as e:
                print(f"⚠️ Falha no modelo {modelo}: {e}")
                continue

        if not response or not response.text:
            print("❌ ERRO: Todos os modelos falharam.")
            return []

        data = json.loads(response.text)
        sugestoes_ia = data.get("sugestoes", [])
        raciocinio = data.get("raciocinio", "Sem info")

        print(f"🧠 Sugestão IA: {sugestoes_ia}")
        print(f"📝 Raciocínio: {raciocinio}")

        # 3. Validação de IDs e Tipos
        ids_validos = {}
        for h in horarios_obj:
            chave = h.get('id') or h.get('pk') or h.get('codigo')
            if chave:
                ids_validos[str(chave)] = chave

        final = []
        for sid in sugestoes_ia:
            if str(sid) in ids_validos:
                final.append(ids_validos[str(sid)])

        print(f"✅ IDs Finais: {final}")
        sys.stdout.flush()
        return final

    except Exception as e:
        print("\n❌ ERRO CRÍTICO NO SCRIPT:")
        traceback.print_exc()
        sys.stdout.flush()
        return []