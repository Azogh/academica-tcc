import os
import google.generativeai as genai
import json
import re 
from django.conf import settings

# Configura a API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("AVISO: GOOGLE_API_KEY não encontrada nas variáveis de ambiente.")

genai.configure(api_key=api_key)

def gerar_analise_grade(historico_json, matriz_json, horarios_json, tipo_analise, dias_excluidos):
    """
    Chama o Gemini para analisar o histórico do aluno e sugerir uma grade.
    """
    
    # 1. Monta o prompt
    prompt = f"""
    VOCÊ É UM COORDENADOR ACADÊMICO ESPECIALISTA.
    Sua tarefa é analisar três conjuntos de dados JSON e gerar uma sugestão de 
    matrícula para um aluno, com base em um método de análise.

    DADOS FORNECIDOS:
    1. historico_aluno: O que o aluno JÁ CURSOU (sigla, status, semestre).
    {historico_json}

    2. matriz_curricular: TODAS as disciplinas do curso, com seus pré-requisitos.
    {matriz_json}

    3. horarios_disponiveis: A oferta de turmas para o próximo semestre. 
       (id, sigla_disciplina, dia_semana, periodo).
    {horarios_json}

    OPÇÕES DA ANÁLISE:
    - Tipo de Análise: "{tipo_analise}"
    - Dias a Excluir: {dias_excluidos}

    REGRAS OBRIGATÓRIAS (CONSTRAINTS):
    1. NÃO PODE sugerir uma disciplina que já está no 'historico_aluno' com status 'APR' (Aprovado), 'CUMP' (Cumprido) ou 'DISP' (Dispensado).
    2. NÃO PODE sugerir uma disciplina se o aluno NÃO CUMPRIU TODOS os seus pré-requisitos (definidos na 'matriz_curricular').
    3. NÃO PODE sugerir disciplinas em 'horarios_disponiveis' que ocorram em um 'dia_semana' listado em 'Dias a Excluir'.
    4. NÃO PODE sugerir duas disciplinas que tenham CONFLITO DE HORÁRIO (mesmo 'dia_semana' e 'periodo').

    LÓGICA DE ANÁLISE (O que fazer com as regras acima):
    - Se "tipo_analise" == "padrao":
      Siga o 'semestre' da 'matriz_curricular'. Tente sugerir disciplinas do semestre mais baixo que ainda não foram cursadas, respeitando as REGRAS.
    
    - Se "tipo_analise" == "soft":
      Priorize disciplinas com baixa carga horária, alta taxa de aprovação (inferida, se não houver dados), ou que sejam de semestres iniciais. 
      Crie uma grade mais leve.
    
    - Se "tipo_analise" == "hardcore":
      Priorize disciplinas que são pré-requisitos para muitas outras. Tente preencher o máximo de horários vagos possível, 
      maximizando a quantidade de disciplinas (respeitando TODAS as REGRAS).

    FORMATO DA RESPOSTA:
    Responda APENAS com um JSON contendo uma única chave "sugestoes".
    O valor deve ser uma lista de IDs (números inteiros) retirados da chave "id" do JSON 'horarios_disponiveis'.
    NÃO ADICIONE TEXTO EXPLICATIVO ANTES OU DEPOIS. APENAS O JSON.
    
    Exemplo de resposta:
    {{"sugestoes": [10, 15, 22]}}
    """
    
    # 2. Configura e chama o modelo
    try:
        # Use o modelo que estiver funcionando para você (2.5 ou 1.5)
        model = genai.GenerativeModel("gemini-2.5-flash") 
        
        response = model.generate_content(prompt)
        texto_resposta = response.text
        
        # 3. Limpeza Robusta com Regex
        # Procura por um bloco ```json ... ``` ou apenas {...}
        json_str = ""
        
        # Tenta achar bloco de código markdown primeiro
        match = re.search(r"```json\s*(\{.*?\})\s*```", texto_resposta, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            # Se não achar bloco, tenta achar o primeiro '{' e o último '}'
            start = texto_resposta.find('{')
            end = texto_resposta.rfind('}')
            if start != -1 and end != -1:
                json_str = texto_resposta[start:end+1]
        
        if not json_str:
            raise ValueError("Não foi possível encontrar um JSON válido na resposta da IA.")

        # 4. Processa a resposta
        data = json.loads(json_str)
        
        return data.get("sugestoes", [])

    except json.JSONDecodeError as e:
        print(f"Erro de JSON na resposta do Gemini: {e}")
        print(f"Resposta recebida (trecho): {texto_resposta[:200]}...") # Loga o início para debug
        return None
    except Exception as e:
        print(f"Erro ao chamar o Gemini: {e}")
        return None