# 🎓 Acadêmica: Sistema Inteligente de Apoio à Matrícula

> **Trabalho de Conclusão de Curso (TCC)**
> Um sistema web para auxiliar coordenadores de curso na análise de históricos escolares e sugestão de grades horárias utilizando Inteligência Artificial.

## 🚀 Sobre o Projeto

O **Acadêmica** é uma plataforma desenvolvida para otimizar o processo de rematrícula e gestão acadêmica. O sistema permite que o coordenador cadastre a estrutura curricular, importe históricos escolares (PDF) e utilize a IA (Google Gemini) para gerar sugestões de matrícula personalizadas, respeitando pré-requisitos, choques de horário e preferências do aluno.

### ✨ Principais Funcionalidades

#### 1. 🔐 Módulo Administrativo (Core)
* **Autenticação Segura:** Login, Logout e Recuperação de Senha.
* **Dashboard Interativo:** Gráficos (Chart.js) com dados reais sobre disciplinas, turmas e índices de ocupação.
* **Gestão Acadêmica (CRUDs):**
    * **Matrizes Curriculares:** Cadastro com versionamento (Ex: Matriz Nova 2023 vs Matriz Antiga).
    * **Disciplinas:** Vínculo com matrizes e sistema de **Pré-requisitos Inteligente** (Select2).
    * **Turmas & Horários:** Cadastro de ofertas com **validação automática de conflitos** e suporte a disciplinas de 4 créditos (cadastro duplo automático).

#### 2. 📂 Módulo de Processamento (Upload)
* **Leitura de PDF:** Extração automática de dados de alunos e notas a partir de históricos escolares em formato PDF.
* **Parser Inteligente:** Identificação de disciplinas cursadas, aprovadas e pendentes.

#### 3. 🧠 Módulo de Inteligência (Analytics)
* **IA Generativa (Gemini 1.5/2.5):** Analisa o perfil do aluno e sugere a grade ideal.
* **Modos de Análise:**
    * ⚖️ **Padrão:** Segue o fluxo regular da matriz.
    * 🪶 **Soft:** Prioriza disciplinas com menor carga/maior aprovação.
    * 🔥 **Hardcore:** Maximiza o número de créditos para adiantar o curso.
* **Edição de Grade com UX Avançada:**
    * Bloqueio visual automático de horários conflitantes ("Lógica Contagiosa").
    * Seleção inteligente de disciplinas de 4 créditos (marcação em bloco).

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.12, Django 5.2.
* **Banco de Dados:** SQLite (Dev).
* **Frontend:** HTML5, CSS3 (Glassmorphism UI), Bootstrap, JavaScript.
* **Bibliotecas JS:** Chart.js (Dashboards), Select2 (Inputs avançados).
* **IA:** Google Generative AI SDK (Gemini).
* **PDF:** PyPDF2 / PDFPlumber (para extração de dados).

---

## ⚙️ Instalação e Configuração

### Pré-requisitos
* Python 3.10+ instalado.
* Git.
* Cliente SQLite3 (para popular dados de teste).

### Passo a Passo

1.  **Clone o repositório**
    ```bash
    git clone [https://github.com/seu-usuario/academica-tcc.git](https://github.com/seu-usuario/academica-tcc.git)
    cd academica-tcc
    ```

2.  **Crie e ative o ambiente virtual**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente**
    Crie um arquivo `.env` na raiz do projeto e adicione sua chave da API do Google:
    ```env
    GOOGLE_API_KEY="sua-chave-aqui"
    DEBUG=True
    SECRET_KEY="sua-chave-secreta-django"
    ```

5.  **Prepare o Banco de Dados**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **🧪 Populando com Dados Reais/Simulados (Importante)**
    O projeto inclui um script SQL (`popular_banco.sql`) contendo a estrutura real do curso (PPCs Antigo e Novo, Disciplinas) e dados simulados de turmas e alunos para teste imediato.

    **Linux (Ubuntu/Debian):**
    ```bash
    # Instale o cliente sqlite se não tiver
    sudo apt install sqlite3 
    
    # Importe os dados
    sqlite3 db.sqlite3 < popular_banco.sql
    ```

    **Windows:**
    Utilize o *DB Browser for SQLite* ou o terminal se tiver o sqlite3 configurado no PATH.

7.  **Crie um Superusuário**
    Para acessar o sistema e o painel administrativo (/admin):
    ```bash
    python manage.py createsuperuser
    ```

8.  **Execute o Projeto**
    ```bash
    python manage.py runserver
    ```
    Acesse em: `http://127.0.0.1:8000`

---

## 📸 Screenshots

*(Coloque aqui prints das telas principais: Dashboard, Edição de Análise e Cadastro de Horários)*

---

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos.