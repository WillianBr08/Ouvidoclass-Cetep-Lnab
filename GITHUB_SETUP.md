# Como Colocar o Projeto no GitHub

Este guia vai te ajudar a colocar o projeto "Ouvidoria CETEP/LNAB" no GitHub.

## Pré-requisitos

1. **Conta no GitHub**: Se não tiver, crie em [github.com](https://github.com)
2. **Git instalado**: Verifique com `git --version`
   - Linux: `sudo apt-get install git`
   - Windows: Baixe de [git-scm.com](https://git-scm.com)

## Passo 1: Criar um Repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique no botão **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha:
   - **Repository name**: `ouvidoria-cetep-lnab` (ou outro nome de sua escolha)
   - **Description**: "Sistema de ouvidoria para manifestações"
   - **Visibility**: Escolha **Public** (público) ou **Private** (privado)
   - **NÃO marque** "Initialize this repository with a README" (já temos arquivos)
5. Clique em **"Create repository"**

## Passo 2: Preparar o Projeto Localmente

### 2.1. Criar arquivo .gitignore

Crie um arquivo chamado `.gitignore` na raiz do projeto com o seguinte conteúdo:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/
*.egg-info/
dist/
build/

# Banco de dados
*.db
*.sqlite
*.sqlite3
web_app/app.db

# Arquivos de dados sensíveis
web_app/data.json
*.json.bak

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Arquivos temporários
*.tmp
*.bak
```

### 2.2. Criar arquivo README.md (opcional mas recomendado)

Crie um arquivo `README.md` na raiz do projeto:

```markdown
# Ouvidoria CETEP/LNAB

Sistema de ouvidoria para recebimento de denúncias, elogios, reclamações e sugestões.

## Funcionalidades

- Registro e autenticação de usuários
- Criação de manifestações (denúncia, elogio, reclamação, sugestão)
- Painel administrativo para visualizar e responder manifestações
- Envio automático de emails para a escola e manifestantes
- Interface web moderna e responsiva

## Tecnologias

- Python 3.10+
- Flask 3.0.3
- SQLite
- HTML/CSS/JavaScript

## Instalação

### Linux
```bash
./start.sh
```

### Windows
```bash
start.bat
```

## Configuração

Configure as variáveis de ambiente para email e administrador:

- `ADMIN_USER`: Usuário do administrador
- `ADMIN_PASS`: Senha do administrador
- `SMTP_HOST`: Servidor SMTP
- `SMTP_PORT`: Porta SMTP (geralmente 587)
- `SMTP_USER`: Usuário do email
- `SMTP_PASS`: Senha do email
- `MAIL_TO`: Email que receberá as manifestações
- `MAIL_FROM`: Email remetente (opcional)

## Licença

[Especifique sua licença aqui]
```

## Passo 3: Inicializar Git e Fazer o Primeiro Commit

Abra o terminal na pasta do projeto e execute:

```bash
# 1. Inicializar repositório Git
git init

# 2. Adicionar todos os arquivos
git add .

# 3. Fazer o primeiro commit
git commit -m "Initial commit: Sistema de ouvidoria CETEP/LNAB"
```

## Passo 4: Conectar com o GitHub

No GitHub, após criar o repositório, você verá instruções. Execute os comandos mostrados, que serão algo como:

```bash
# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu usuário do GitHub)
git remote add origin https://github.com/SEU_USUARIO/ouvidoria-cetep-lnab.git

# Renomear branch principal para main (se necessário)
git branch -M main

# Enviar código para o GitHub
git push -u origin main
```

**Nota**: Se pedir autenticação:
- **Token de acesso pessoal**: GitHub não aceita mais senha. Você precisa criar um token:
  1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token (classic)
  3. Dê um nome e selecione escopos: `repo` (todos)
  4. Copie o token e use como senha ao fazer push

## Passo 5: Verificar

1. Acesse seu repositório no GitHub
2. Você deve ver todos os arquivos do projeto
3. Pronto! Seu código está no GitHub

## Comandos Úteis do Git

```bash
# Ver status dos arquivos
git status

# Adicionar arquivos específicos
git add arquivo.py

# Fazer commit
git commit -m "Descrição da mudança"

# Enviar para o GitHub
git push

# Baixar atualizações do GitHub
git pull

# Ver histórico de commits
git log

# Ver diferenças
git diff
```

## Dicas de Segurança

⚠️ **IMPORTANTE**: Nunca commite informações sensíveis!

- **NÃO** inclua senhas, tokens ou chaves de API no código
- **NÃO** commite o arquivo `app.db` (banco de dados)
- **NÃO** commite `data.json` com dados reais
- Use variáveis de ambiente para configurações sensíveis
- O arquivo `.gitignore` já está configurado para ignorar arquivos sensíveis

## Próximos Passos

1. **Colaboradores**: Vá em Settings → Collaborators para adicionar pessoas
2. **Issues**: Use a aba Issues para gerenciar tarefas e bugs
3. **Releases**: Crie releases para versões do projeto
4. **GitHub Pages**: Pode hospedar o site estático (se tiver frontend separado)

## Problemas Comuns

### Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/ouvidoria-cetep-lnab.git
```

### Erro: "failed to push some refs"
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Esqueceu de adicionar arquivo ao .gitignore
```bash
# Remover arquivo do Git mas manter localmente
git rm --cached arquivo.db
git commit -m "Remove arquivo sensível"
git push
```

## Suporte

Se tiver dúvidas:
- Documentação do Git: [git-scm.com/doc](https://git-scm.com/doc)
- Documentação do GitHub: [docs.github.com](https://docs.github.com)

---

**Boa sorte com seu projeto! 🚀**

