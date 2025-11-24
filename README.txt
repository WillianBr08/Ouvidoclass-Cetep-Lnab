Como rodar localmente (Windows, sem PowerShell)

Aplicação Tkinter (Python)
==========================

Como executar
-------------
1) Certifique-se de ter Python 3.10+ instalado.
2) No Windows, você pode usar o atalho:
   - start_tkinter.bat (duplo clique)
   ou executar manualmente:
   - cd tk_app
   - python app.py

Funcionalidades
---------------
- Registrar e entrar (armazenamento local em data.json)
- Criar "manifestos" (denúncia, elogio, reclamação, sugestão)
- Listar "Meus envios", abrir e apagar

Arquivos principais
-------------------
- tk_app/app.py      → Interface Tkinter (Home, Login, Registrar, Visualizar)
- tk_app/storage.py  → Persistência simples em JSON


Aplicação Web (Flask)
=====================

Como executar
-------------
1) Windows: start.bat
   - Cria venv, instala Flask e inicia em http://127.0.0.1:5000

Variáveis de email (opcional)
-----------------------------
Defina como variáveis de ambiente antes de rodar (para enviar email ao criar manifesto):
- SMTP_HOST
- SMTP_PORT (ex: 587)
- SMTP_USER
- SMTP_PASS
- MAIL_FROM (remetente; se vazio usa SMTP_USER)
- MAIL_TO (email da escola que receberá os manifestos)
- SMTP_STARTTLS=true (padrão)

Arquivos principais
-------------------
- web_app/app.py           → Rotas Flask e envio de email
- web_app/storage.py       → Persistência JSON (usuários, sessão por cookie, manifestos)
- web_app/templates/*.html → Páginas HTML sem JS
- web_app/static/styles.css→ CSS

Administração
-------------
Rotas:
- /admin/login → login de administrador
- /admin       → listagem de todos os envios

Defina credenciais via ambiente:
- ADMIN_USER
- ADMIN_PASS

1) Requisitos
- Node.js LTS instalado (inclui npm)

2) Iniciar o servidor
- Dê duplo clique em start.bat (nesta pasta).
- Ou abra o cmd e rode:
  cd "C:\Users\Aluno\Documents\Golpe mega-sena\backend"
  npm install
  npm start

3) Acessar
- Abra o navegador em: http://localhost:3000

4) Fluxos
- Registrar: criar conta na página Registrar
- Entrar: autenticar e manter sessão via cookie httpOnly
- Enviar: na página inicial (após login), preencha e envie
- Meus envios: lista seus envios

5) Dados locais
- backend\data\users.json (usuarios)
- backend\data\reports.json (envios)

6) Dicas
- Se a página nao carregar, confirme se o servidor está iniciado no cmd.
- Se o login falhar, verifique o arquivo users.json e tente registrar novamente.


