BEGIN TRANSACTION;

-- ============================================================
-- 1. LIMPEZA PRÉVIA (OPCIONAL - RECOMENDADO PARA EVITAR DUPLICIDADE)
-- Descomente as linhas abaixo se quiser limpar as tabelas antes de rodar
-- DELETE FROM HORARIO;
-- DELETE FROM HISTORICO_ITENS;
-- DELETE FROM HISTORICO;
-- DELETE FROM ALUNO;
-- DELETE FROM TURMA;
-- DELETE FROM DISCIPLINAS_pre_requisitos;
-- DELETE FROM DISCIPLINAS;
-- DELETE FROM MATRIZ_CURRICULAR;
-- DELETE FROM CURSO;
-- ============================================================

-- 2. GARANTIR USUÁRIO PADRÃO (Evita erro de Constraint)
INSERT OR IGNORE INTO USUARIO (id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, gestao_inicio, portaria)
VALUES (1, 'pbkdf2_sha256$1000000$hash_falso', 1, 'admin_system', 'Admin', 'Sistema', 'admin@iffar.edu.br', 1, 1, datetime('now'), NULL, NULL);

-- 3. CRIAR CURSO
INSERT INTO CURSO (nome) VALUES ('Bacharelado em Sistemas de Informação');

-- 4. CRIAR MATRIZES CURRICULARES (NOVA e ANTIGA)
INSERT INTO MATRIZ_CURRICULAR (nome, ch_total, estagio, acc, ano_referencia, curso_id, usuario_id) VALUES 
('BSI - NOVO A PARTIR DE 2023', 3006, 0, 270, 2023, (SELECT id FROM CURSO WHERE nome LIKE 'Bacharelado%' LIMIT 1), 1),
('BSI - MATRIZ ANTIGA', 3180, 0, 300, 2018, (SELECT id FROM CURSO WHERE nome LIKE 'Bacharelado%' LIMIT 1), 1);

-- 5. CADASTRAR DISCIPLINAS (Baseado nos PDFs e Schedule 2025)

-- === DISCIPLINAS MATRIZ NOVA (2023) - SEMESTRES 1, 3, 5 ===
-- Semestre 1
INSERT INTO DISCIPLINAS (nome, sigla, ch, semestre, codigo, usuario_id, matriz_curricular_id) VALUES 
('Fundamentos de Programação', 'FPROG', 72, 1, 'BSI2301', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Fundamentos da Computação e Sistemas de Informação', 'FCSI', 72, 1, 'BSI2302', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Lógica para Computação', 'LOG', 72, 1, 'BSI2303', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Matemática e Álgebra Linear', 'ALGLIN', 72, 1, 'BSI2304', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Inglês Instrumental', 'ING', 36, 1, 'BSI2305', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Fundamentos da Administração', 'ADM', 36, 1, 'BSI2306', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023));

-- Semestre 2 (Para histórico)
INSERT INTO DISCIPLINAS (nome, sigla, ch, semestre, codigo, usuario_id, matriz_curricular_id) VALUES 
('Fundamentos de Programação Web', 'WEB1', 36, 2, 'BSI2307', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Estrutura de Dados', 'ED', 72, 2, 'BSI2308', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023));

-- Semestre 3 (Turma 2024)
INSERT INTO DISCIPLINAS (nome, sigla, ch, semestre, codigo, usuario_id, matriz_curricular_id) VALUES 
('Organização e Arquitetura de Computadores', 'OAC', 72, 3, 'BSI2313', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Processo de Software e Engenharia de Requisitos', 'REQ', 72, 3, 'BSI2314', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Fundamentos de Banco de Dados', 'BD1', 72, 3, 'BSI2315', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Programação Orientada a Objetos', 'POO', 72, 3, 'BSI2316', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Metodologia Científica', 'MET', 36, 3, 'BSI2317', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Contabilidade e Custos', 'CONT', 36, 3, 'BSI2318', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023));

-- Semestre 5 (Turma 2023)
INSERT INTO DISCIPLINAS (nome, sigla, ch, semestre, codigo, usuario_id, matriz_curricular_id) VALUES 
('Sistemas Operacionais', 'SO', 72, 5, 'BSI2325', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Projeto de Software', 'PROJSOFT', 36, 5, 'BSI2326', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Programação Web', 'WEB2', 72, 5, 'BSI2327', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Laboratório de Banco de Dados', 'BD2', 72, 5, 'BSI2328', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Redes de Computadores II', 'REDES2', 72, 5, 'BSI2329', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)),
('Sistemas Distribuídos', 'SISTDIST', 36, 5, 'BSI2330', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2023)); -- Eletiva usada no horario

-- === DISCIPLINAS MATRIZ ANTIGA (2018) - SEMESTRE 7 ===
-- Semestre 7 (Turma 2022)
INSERT INTO DISCIPLINAS (nome, sigla, ch, semestre, codigo, usuario_id, matriz_curricular_id) VALUES 
('Inteligência Artificial', 'IA', 72, 7, 'BSI1835', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018)),
('Qualidade e Desenvolvimento de Software', 'QUAL', 72, 7, 'BSI1836', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018)),
('Governança de Tecnologia da Informação', 'GOVTI', 72, 7, 'BSI1837', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018)),
('Auditoria e Segurança de Sistemas', 'SEG', 36, 7, 'BSI1838', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018)),
('Trabalho de Conclusão de Curso I', 'TCCI', 72, 7, 'BSI1839', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018)),
('Software Livre Linux', 'LINUX', 36, 7, 'BSI1840', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018)); -- Eletiva

-- Disciplinas básicas da antiga (para histórico)
INSERT INTO DISCIPLINAS (nome, sigla, ch, semestre, codigo, usuario_id, matriz_curricular_id) VALUES 
('Lógica de Programação', 'LOG_OLD', 72, 1, 'BSI1801', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018)),
('Estrutura de Dados', 'ED_OLD', 72, 3, 'BSI1815', 1, (SELECT id FROM MATRIZ_CURRICULAR WHERE ano_referencia = 2018));


-- 6. CRIAR TURMAS
INSERT INTO TURMA (nome, ano_ingresso, usuario_id) VALUES 
('Sistemas de Informação 2025', 2025, 1),
('Sistemas de Informação 2024', 2024, 1),
('Sistemas de Informação 2023', 2023, 1),
('Sistemas de Informação 2022', 2022, 1);

-- 7. CADASTRAR HORÁRIOS (Correção: Periodos "1-2" e "3-4")

-- === TURMA 2025 (1º Semestre) ===
INSERT INTO HORARIO (dia_semana, periodo, disciplina_id, turma_id, usuario_id) VALUES
('SEG', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2301'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Fund Prog
('SEG', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2301'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Fund Prog
('TER', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2303'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Logica
('TER', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2302'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Fund Comp SI
('QUA', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2305'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Ingles
('QUA', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2306'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Adm
('QUI', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2304'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Alg Lin
('QUI', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2303'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Logica
('SEX', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2302'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1), -- Fund Comp SI
('SEX', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2304'), (SELECT id FROM TURMA WHERE ano_ingresso=2025), 1); -- Alg Lin

-- === TURMA 2024 (3º Semestre) ===
INSERT INTO HORARIO (dia_semana, periodo, disciplina_id, turma_id, usuario_id) VALUES
('SEG', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2313'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- OAC
('SEG', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2316'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- POO
('TER', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2313'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- OAC
('TER', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2316'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- POO
('QUA', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2314'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- Eng Req
('QUA', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2315'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- BD1
('QUI', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2317'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- Metod
('QUI', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2315'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- BD1
('SEX', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2318'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1), -- Contab
('SEX', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2314'), (SELECT id FROM TURMA WHERE ano_ingresso=2024), 1); -- Eng Req

-- === TURMA 2023 (5º Semestre) ===
INSERT INTO HORARIO (dia_semana, periodo, disciplina_id, turma_id, usuario_id) VALUES
('SEG', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2327'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Web
('SEG', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2325'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Sist Op
('TER', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2327'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Web
('TER', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2329'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Redes 2
('QUA', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2328'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Lab BD
('QUA', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2330'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Sist Dist (Eletiva)
('QUI', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2328'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Lab BD
('QUI', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2329'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Redes 2
('SEX', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2326'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1), -- Proj Soft
('SEX', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI2325'), (SELECT id FROM TURMA WHERE ano_ingresso=2023), 1); -- Sist Op

-- === TURMA 2022 (7º Semestre - Antiga) ===
INSERT INTO HORARIO (dia_semana, periodo, disciplina_id, turma_id, usuario_id) VALUES
('SEG', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1835'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- IA
('SEG', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1840'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- Linux
('TER', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1836'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- Qualidade
('TER', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1839'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- TCC 1
('QUA', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1835'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- IA
('QUA', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1836'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- Qualidade
('QUI', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1837'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- Gov TI
('QUI', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1839'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- TCC 1
('SEX', '1-2', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1838'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1), -- Auditoria
('SEX', '3-4', (SELECT id FROM DISCIPLINAS WHERE codigo='BSI1837'), (SELECT id FROM TURMA WHERE ano_ingresso=2022), 1); -- Gov TI

-- 8. POPULAR ALUNOS (Fictícios para Teste)
-- Formandos (Matriz Antiga)
INSERT INTO ALUNO (nome, matricula, ano_ingresso, curso_id) VALUES 
('João Silva (7º Sem)', '20221001', '2022', (SELECT id FROM CURSO LIMIT 1)),
('Maria Oliveira (7º Sem)', '20221002', '2022', (SELECT id FROM CURSO LIMIT 1));

-- Em Curso (Matriz Nova)
INSERT INTO ALUNO (nome, matricula, ano_ingresso, curso_id) VALUES 
('Carlos Souza (5º Sem)', '20231003', '2023', (SELECT id FROM CURSO LIMIT 1)),
('Ana Pereira (3º Sem)', '20241004', '2024', (SELECT id FROM CURSO LIMIT 1));

-- Calouros (Matriz Nova)
INSERT INTO ALUNO (nome, matricula, ano_ingresso, curso_id) VALUES 
('Roberto Alves (1º Sem)', '20251005', '2025', (SELECT id FROM CURSO LIMIT 1));

-- 9. HISTÓRICO (Apenas um exemplo para o formando João)
INSERT INTO HISTORICO (data_upload, status, arquivo_original, aluno_id, usuario_id) 
VALUES (datetime('now'), 'PROCESSADO', 'historico_joao.pdf', (SELECT id FROM ALUNO WHERE matricula='20221001'), 1);

INSERT INTO HISTORICO_ITENS (disciplina_nome, disciplina_sigla, ch, nota, frequencia, status_disciplina, semestre_cursado, historico_id)
VALUES ('Lógica de Programação', 'LOG', 72, 8.5, 100, 'Aprovado', '2022/1', (SELECT id FROM HISTORICO WHERE aluno_id = (SELECT id FROM ALUNO WHERE matricula='20221001')));

COMMIT;