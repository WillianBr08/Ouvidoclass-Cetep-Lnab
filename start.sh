#!/bin/bash

# Script para iniciar a aplicação web no Linux
# Uso: ./start.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Ouvidoria CETEP/LNAB - Iniciando ==="

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não está instalado."
    echo "Instale com: sudo pacman -S python python-pip"
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Erro ao criar ambiente virtual."
        exit 1
    fi
fi

# Verificar se o venv foi criado corretamente
if [ ! -f ".venv/bin/python" ]; then
    echo "Erro: Ambiente virtual não foi criado corretamente."
    echo "Removendo e tentando novamente..."
    rm -rf .venv
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Erro ao criar ambiente virtual."
        exit 1
    fi
fi

# Usar executáveis do venv diretamente (caminho absoluto)
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
VENV_PIP="$SCRIPT_DIR/.venv/bin/pip"

# Atualizar pip
echo "Atualizando pip..."
"$VENV_PIP" install --upgrade pip --quiet

# Instalar dependências
echo "Instalando dependências..."
"$VENV_PIP" install -r requirements.txt --quiet

# Configurar variáveis de ambiente (se não estiverem definidas)
export ADMIN_USER=${ADMIN_USER:-admin}
export ADMIN_PASS=${ADMIN_PASS:-1234}
export MAIL_TO=${MAIL_TO:-ouvidoclass.edu@gmail.com}
export SMTP_HOST=${SMTP_HOST:-smtp.gmail.com}
export SMTP_PORT=${SMTP_PORT:-587}
export SMTP_USER=${SMTP_USER:-ouvidoclass.edu@gmail.com}
export SMTP_PASS=${SMTP_PASS:-rruo scpx gska tvpb}
export MAIL_FROM=${MAIL_FROM:-ouvidoclass.edu@gmail.com}
export SMTP_STARTTLS=${SMTP_STARTTLS:-true}
export PORT=${PORT:-5000}

echo ""
echo "=== Configuração ==="
echo "Admin User: $ADMIN_USER"
echo "SMTP Host: $SMTP_HOST"
echo "SMTP User: $SMTP_USER"
echo "Mail To: $MAIL_TO"
echo "Mail From: $MAIL_FROM"
echo ""
echo "✅ Email configurado: $SMTP_USER"
echo ""
echo "=== Iniciando servidor Flask ==="
echo "Acesse: http://127.0.0.1:$PORT"
echo "Pressione Ctrl+C para parar"
echo ""

# Iniciar aplicação
cd "$SCRIPT_DIR/web_app"
"$VENV_PYTHON" app.py

