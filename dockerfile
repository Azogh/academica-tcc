# 1. IMAGEM BASE
# Alterado de 3.9-slim-buster para 3.12-slim, que é compatível com Django 5.2.6.
FROM python:3.12-slim 

# 2. VARIÁVEIS DE AMBIENTE
ENV PYTHONUNBUFFERED 1

# 3. DIRETÓRIO DE TRABALHO
WORKDIR /app

# 4. INSTALAÇÃO DE DEPENDÊNCIAS
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPIAR CÓDIGO E ARQUIVOS ESSENCIAIS
COPY . /app/

# 6. EXPOR PORTA
EXPOSE 8000

# 7. COMANDO DE INICIALIZAÇÃO
# Corrigido: Usamos a forma de Array JSON, que é mais robusta, e removemos
# temporariamente o migrate para garantir que o servidor suba.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]