from django.db import transaction
from .models import HistoricoItens
from .gemini_pdf import extrair_disciplinas_gemini  # Sua função existente

def processar_historico_pdf(historico):
    """
    Lê o PDF do histórico, extrai dados com Gemini e salva no banco.
    """
    try:
        # 1. Abre o arquivo PDF que foi salvo no modelo
        # O 'rb' é importante para leitura binária
        with historico.arquivo_original.open('rb') as pdf_file:
            # Chama sua função do Gemini (que retorna apenas a lista de dados)
            dados_extraidos = extrair_disciplinas_gemini(pdf_file)

        # 2. Validações
        if dados_extraidos is None:
            return False, "Erro na leitura com IA. O PDF pode estar ilegível ou a API falhou."

        if not dados_extraidos: 
            return False, "O PDF foi lido, mas nenhuma disciplina foi encontrada no padrão esperado."

        # 3. Salva no Banco de Dados (Transação Atômica)
        with transaction.atomic():
            # Limpa itens antigos se for um reprocessamento
            HistoricoItens.objects.filter(historico=historico).delete()

            for item in dados_extraidos:
                # Tratamento básico de nota (trocar vírgula por ponto se necessário)
                nota_valor = item.get('media')
                if isinstance(nota_valor, str):
                    nota_valor = nota_valor.replace(',', '.')
                if nota_valor == 'null' or nota_valor == '':
                    nota_valor = None

                # Cria o item no banco
                HistoricoItens.objects.create(
                    historico=historico,
                    disciplina_nome=item.get('nome', 'NOME DESCONHECIDO'),
                    disciplina_sigla=item.get('codigo', '---'),
                    ch=item.get('ch', 0) or 0,
                    nota=nota_valor,
                    frequencia=item.get('frequencia'),
                    status_disciplina=item.get('situacao', 'N/A'),
                    semestre_cursado=item.get('periodo', '-')
                )

        return True, f"Processamento concluído! {len(dados_extraidos)} disciplinas importadas."

    except Exception as e:
        print(f"Erro crítico no utils: {e}")
        return False, f"Erro interno ao salvar dados: {str(e)}"