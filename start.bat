@echo off
cd /d "%~dp0"
set ADMIN_USER=admin
set ADMIN_PASS=1234
set MAIL_TO=escola@exemplo.com
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USER=seuusuario@gmail.com
set SMTP_PASS=suasenha
set SMTP_STARTTLS=true
if not exist .venv\Scripts\python.exe (
  echo Criando ambiente virtual...
  py -3 -m venv .venv || python -m venv .venv
)
if not exist .venv\Scripts\python.exe (
  echo Falha ao criar ambiente virtual. Verifique instalacao do Python.
  pause
  exit /b 1
)
set ADMIN_USER=admin
set ADMIN_PASS=1234
set MAIL_TO=escola@exemplo.com
set SMTP_HOST=smtp.seuprovedor.com
set SMTP_PORT=587
set SMTP_USER=seuusuario
set SMTP_PASS=suasenha
set SMTP_STARTTLS=true
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
".venv\Scripts\python.exe" web_app\app.py

