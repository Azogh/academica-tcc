import os
import json
import google.generativeai as genai


# Inicializa Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def extrair_disciplinas_gemini(pdf_file):
    """
    Extrai disciplinas de um PDF de histórico usando o Gemini 2.5 Flash.
    Retorna uma lista de dicionários ou None em caso de erro.
    """

    try:
        pdf_bytes = pdf_file.read()

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
Você é um especialista em interpretar documentos acadêmicos.

Receberá um Histórico Escolar do IFFAR. Extraia APENAS a tabela 
“Componentes Curriculares Cursados/Cursando”.

O retorno deve ser EXCLUSIVAMENTE o JSON nesta estrutura:

[
  {
    "periodo": "2020.1",
    "nome": "...",
    "codigo": "08023001",
    "ch": 72,
    "frequencia": 100,
    "media": 8.5,
    "situacao": "APR"
  }
]

Regras:
- Se frequência não existir, usar null.
- Se média não existir, usar null.
- Situação deve obedecer: APR, REP, REPF, REPMF, CANC, MATR, CUMP, DISP.
- Código deve ter apenas números.
- Não inclua comentários fora do JSON.
"""

        pdf_part = {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }

        response = model.generate_content([prompt, pdf_part])

        try:
            # Garante que retorna JSON puro
            texto = response.text.strip()

            # Remove ```json ``` se houver
            if texto.startswith("```"):
                texto = texto.split("```")[1]
                texto = texto.replace("json", "").replace("```", "").strip()

            resultado = json.loads(texto)
            return resultado

        except Exception as e:
            print("Erro ao interpretar JSON:", e)
            print("Resposta da IA:", response.text)
            return None

    except Exception as e:
        print("Erro interno no Gemini:", e)
        return None
