from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Optional
import html
import requests

from flask import Flask, render_template, request, redirect, url_for, make_response

import storage
import db


def _send_email_via_sendgrid(subject: str, html_body: str, text_body: str, recipients: list[str], category: Optional[str] = None) -> bool:
    """Envia emails usando a API do SendGrid."""
    api_key = os.getenv('SENDGRID_API_KEY')
    sender = os.getenv('MAIL_FROM') or os.getenv('SMTP_USER')

    if not api_key:
        print("[EMAIL] SENDGRID_API_KEY não configurada. Pulei envio.")
        return False

    if not sender:
        print("[EMAIL] MAIL_FROM (ou SMTP_USER) não configurado. Pulei envio.")
        return False

    if not recipients:
        print("[EMAIL] Nenhum destinatário informado.")
        return False

    payload = {
        "personalizations": [{
            "to": [{"email": addr} for addr in recipients]
        }],
        "from": {"email": sender},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": text_body},
            {"type": "text/html", "value": html_body}
        ]
    }

    if category:
        payload["categories"] = [category]

    try:
        response = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        if response.status_code >= 400:
            print(f"[EMAIL] Erro SendGrid {response.status_code}: {response.text}")
            return False
        print(f"[EMAIL] Email enviado via SendGrid para {', '.join(recipients)}")
        return True
    except requests.RequestException as exc:
        print(f"[EMAIL] Falha ao chamar SendGrid: {exc}")
        return False


def send_report_email_to_school(report: dict, user: dict) -> None:
    """Envia email para a escola quando uma manifestação é criada"""
    mail_to_env = os.getenv('MAIL_TO', '')
    recipients = [email.strip() for email in mail_to_env.split(',') if email.strip()]

    if not recipients:
        print("[EMAIL] MAIL_TO não configurado, não há para quem enviar.")
        return

    assunto = f"📝 {report['tipo'].upper()} — {report['titulo']}"
    nome = report.get('alunoNome') or 'ANÔNIMO'
    turma = report.get('turma') or '—'
    autor = f"{nome} (Turma: {turma})" if not report.get('anonimo') else 'ANÔNIMO'
    criado = report['createdAt'].replace('T',' ')[:16]
    
    # Emoji baseado no tipo
    tipo_emoji = {
        'denúncia': '🚨',
        'denuncia': '🚨',
        'reclamação': '⚠️',
        'reclamacao': '⚠️',
        'elogio': '⭐',
        'sugestão': '💡',
        'sugestao': '💡'
    }
    emoji = tipo_emoji.get(report['tipo'].lower(), '📋')
    
    # Se for anônimo, não mostrar informações do usuário
    if report.get('anonimo'):
        html_corpo = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap');
                body {{
                    font-family: 'Kalam', cursive, Arial, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    padding: 20px;
                    margin: 0;
                }}
                .letter {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #1e1e2e;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
                    position: relative;
                    border: 1px solid #2d2d44;
                }}
                .letter::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: repeating-linear-gradient(
                        90deg,
                        #6c5ce7 0px,
                        #6c5ce7 10px,
                        transparent 10px,
                        transparent 20px
                    );
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px dashed #6c5ce7;
                    padding-bottom: 15px;
                }}
                .header h1 {{
                    font-size: 24px;
                    color: #e0e0e0;
                    margin: 0;
                    font-weight: 700;
                }}
                .content {{
                    line-height: 1.8;
                    color: #d0d0d0;
                    font-size: 16px;
                }}
                .info-box {{
                    background: #2d2d44;
                    border-left: 4px solid #ff9800;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    color: #e0e0e0;
                }}
                .message-box {{
                    background: #252535;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 6px;
                    border-left: 4px solid #2196F3;
                    font-style: italic;
                    white-space: pre-wrap;
                    color: #d0d0d0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px dashed #6c5ce7;
                    text-align: center;
                    color: #9ca3af;
                    font-size: 14px;
                }}
                .badge {{
                    display: inline-block;
                    background: #ff5722;
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: bold;
                    margin-left: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="letter">
                <div class="header">
                    <h1>{emoji} Ouvidoria CETEP/LNAB</h1>
                </div>
                <div class="content">
                    <p><strong>Nova manifestação recebida</strong></p>
                    
                    <div class="info-box">
                        <strong>📋 Tipo:</strong> {html.escape(report['tipo'].upper())}<br>
                        <strong>📌 Título:</strong> {html.escape(report['titulo'])}<br>
                        <strong>👤 Autor:</strong> ANÔNIMO<br>
                        <strong>📅 Data:</strong> {html.escape(criado)}
                    </div>
                    
                    <div style="background: #3d2d2d; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #f44336; color: #ffcccc;">
                        <strong>🔒 MANIFESTAÇÃO ANÔNIMA</strong><br>
                        <small style="color: #d0a0a0;">Informações do manifestante não foram divulgadas</small>
                    </div>
                    
                    <p><strong>💬 Mensagem:</strong></p>
                    <div class="message-box">{html.escape(report['mensagem'])}</div>
                </div>
                <div class="footer">
                    <p>Para responder, acesse o painel administrativo 🖥️</p>
                </div>
            </div>
        </body>
        </html>
        """
        texto_corpo = (
            f"Nova manifestação recebida na Ouvidoria CETEP/LNAB\n\n"
            f"Tipo: {report['tipo'].upper()}\n"
            f"Título: {report['titulo']}\n"
            f"Autor: ANÔNIMO\n"
            f"Data: {criado}\n"
            f"⚠️ MANIFESTAÇÃO ANÔNIMA - Informações do manifestante não foram divulgadas\n\n"
            f"Mensagem:\n{report['mensagem']}\n\n"
            f"---\n"
            f"Para responder, acesse o painel administrativo."
        )
    else:
        html_corpo = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap');
                body {{
                    font-family: 'Kalam', cursive, Arial, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    padding: 20px;
                    margin: 0;
                }}
                .letter {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #1e1e2e;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
                    position: relative;
                    border: 1px solid #2d2d44;
                }}
                .letter::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: repeating-linear-gradient(
                        90deg,
                        #6c5ce7 0px,
                        #6c5ce7 10px,
                        transparent 10px,
                        transparent 20px
                    );
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px dashed #6c5ce7;
                    padding-bottom: 15px;
                }}
                .header h1 {{
                    font-size: 24px;
                    color: #e0e0e0;
                    margin: 0;
                    font-weight: 700;
                }}
                .content {{
                    line-height: 1.8;
                    color: #d0d0d0;
                    font-size: 16px;
                }}
                .info-box {{
                    background: #2d2d44;
                    border-left: 4px solid #ff9800;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    color: #e0e0e0;
                }}
                .message-box {{
                    background: #252535;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 6px;
                    border-left: 4px solid #2196F3;
                    font-style: italic;
                    white-space: pre-wrap;
                    color: #d0d0d0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px dashed #6c5ce7;
                    text-align: center;
                    color: #9ca3af;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="letter">
                <div class="header">
                    <h1>{emoji} Ouvidoria CETEP/LNAB</h1>
                </div>
                <div class="content">
                    <p><strong>Nova manifestação recebida</strong></p>
                    
                    <div class="info-box">
                        <strong>📋 Tipo:</strong> {html.escape(report['tipo'].upper())}<br>
                        <strong>📌 Título:</strong> {html.escape(report['titulo'])}<br>
                        <strong>👤 Autor:</strong> {html.escape(autor)}<br>
                        <strong>📅 Data:</strong> {html.escape(criado)}<br>
                        <strong>✉️ Usuário:</strong> {html.escape(user['name'])} &lt;{html.escape(user['email'])}&gt;
                    </div>
                    
                    <p><strong>💬 Mensagem:</strong></p>
                    <div class="message-box">{html.escape(report['mensagem'])}</div>
                </div>
                <div class="footer">
                    <p>Para responder, acesse o painel administrativo 🖥️</p>
                </div>
            </div>
        </body>
        </html>
        """
        texto_corpo = (
            f"Nova manifestação recebida na Ouvidoria CETEP/LNAB\n\n"
            f"Tipo: {report['tipo'].upper()}\n"
            f"Título: {report['titulo']}\n"
            f"Autor: {autor}\n"
            f"Data: {criado}\n"
            f"Usuário: {user['name']} <{user['email']}>\n\n"
            f"Mensagem:\n{report['mensagem']}\n\n"
            f"---\n"
            f"Para responder, acesse o painel administrativo."
        )

    _send_email_via_sendgrid(assunto, html_corpo, texto_corpo, recipients, category="report-notification")


def send_response_email_to_user(report: dict, user: dict, admin_message: str) -> bool:
    """Envia email de resposta do administrador para o manifestante. Retorna True se enviado com sucesso."""
    if not user.get('email'):
        print("[ERRO EMAIL] Usuário não tem email cadastrado")
        return False

    try:
        assunto = f"✉️ Resposta da Ouvidoria — {report['titulo']}"
        criado = report['createdAt'].replace('T',' ')[:16]
        
        # Verificar se foi anônimo
        is_anonimo = report.get('anonimo', False)
        anonimo_badge = '<span style="background: #ff9800; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; margin-left: 8px;">🔒 ANÔNIMA</span>' if is_anonimo else ""
        anonimo_nota = " (MANIFESTAÇÃO ANÔNIMA)" if is_anonimo else ""
        
        # Emoji baseado no tipo
        tipo_emoji = {
            'denúncia': '🚨',
            'denuncia': '🚨',
            'reclamação': '⚠️',
            'reclamacao': '⚠️',
            'elogio': '⭐',
            'sugestão': '💡',
            'sugestao': '💡'
        }
        emoji = tipo_emoji.get(report['tipo'].lower(), '📋')
        
        html_corpo = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap');
                body {{
                    font-family: 'Kalam', cursive, Arial, sans-serif;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    padding: 20px;
                    margin: 0;
                }}
                .letter {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #1e1e2e;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.5);
                    position: relative;
                    border: 1px solid #2d2d44;
                }}
                .letter::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: repeating-linear-gradient(
                        90deg,
                        #00d4aa 0px,
                        #00d4aa 10px,
                        transparent 10px,
                        transparent 20px
                    );
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px dashed #00d4aa;
                    padding-bottom: 15px;
                }}
                .header h1 {{
                    font-size: 24px;
                    color: #e0e0e0;
                    margin: 0;
                    font-weight: 700;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #e0e0e0;
                    margin-bottom: 20px;
                }}
                .content {{
                    line-height: 1.8;
                    color: #d0d0d0;
                    font-size: 16px;
                }}
                .info-box {{
                    background: #2d2d44;
                    border-left: 4px solid #00d4aa;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    color: #e0e0e0;
                }}
                .message-box {{
                    background: #252535;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 6px;
                    border-left: 4px solid #2196F3;
                    font-style: italic;
                    white-space: pre-wrap;
                    color: #d0d0d0;
                }}
                .response-box {{
                    background: #1e3a3a;
                    border-left: 4px solid #00d4aa;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 6px;
                    font-weight: 500;
                    white-space: pre-wrap;
                    color: #d0d0d0;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px dashed #00d4aa;
                    text-align: center;
                    color: #9ca3af;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="letter">
                <div class="header">
                    <h1>✉️ Ouvidoria CETEP/LNAB</h1>
                </div>
                <div class="content">
                    <div class="greeting">
                        <strong>Olá {html.escape(user['name'])},</strong>
                    </div>
                    
                    <p>Você recebeu uma resposta sobre sua manifestação{anonimo_nota}:</p>
                    
                    <div class="info-box">
                        <strong>{emoji} Tipo:</strong> {html.escape(report['tipo'].upper())}{anonimo_badge}<br>
                        <strong>📌 Título:</strong> {html.escape(report['titulo'])}<br>
                        <strong>📅 Data:</strong> {html.escape(criado)}
                    </div>
                    
                    <p><strong>💬 Sua mensagem original:</strong></p>
                    <div class="message-box">{html.escape(report['mensagem'])}</div>
                    
                    <p><strong>📝 Resposta da Ouvidoria:</strong></p>
                    <div class="response-box">{html.escape(admin_message)}</div>
                </div>
                <div class="footer">
                    <p>Ouvidoria CETEP/LNAB 📚</p>
                    <p style="font-size: 12px; color: #6b7280;">Este é um email automático, por favor não responda.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        texto_corpo = (
            f"Olá {user['name']},\n\n"
            f"Você recebeu uma resposta da Ouvidoria CETEP/LNAB sobre sua manifestação{anonimo_nota}:\n\n"
            f"---\n"
            f"Tipo: {report['tipo'].upper()}{anonimo_nota}\n"
            f"Título: {report['titulo']}\n"
            f"Data da manifestação: {criado}\n\n"
            f"Sua mensagem:\n{report['mensagem']}\n\n"
            f"---\n"
            f"RESPOSTA DA OUVIDORIA:\n\n"
            f"{admin_message}\n\n"
            f"---\n"
            f"Ouvidoria CETEP/LNAB"
        )

        return _send_email_via_sendgrid(assunto, html_corpo, texto_corpo, [user['email']], category="report-response")
    except Exception as e:
        import traceback
        print(f"[ERRO EMAIL] Erro inesperado ao preparar email: {e}")
        print(f"[ERRO EMAIL] Traceback: {traceback.format_exc()}")
        return False


def is_admin_request(req) -> bool:
    admin_user = os.getenv('ADMIN_USER')
    admin_pass = os.getenv('ADMIN_PASS')
    if not admin_user or not admin_pass:
        return False
    return req.cookies.get('admin') == '1'


def create_app() -> Flask:
    app = Flask(__name__)
    db.init_db()

    @app.context_processor
    def inject_user():
        token = request.cookies.get('session')
        def type_class(tipo: str) -> str:
            t = (tipo or '').strip().lower()
            if 'denúncia' in t or 'denuncia' in t:
                return 'type-denuncia'
            if 'reclama' in t:
                return 'type-reclamacao'
            if 'elogio' in t:
                return 'type-elogio'
            return 'type-sugestao'
        return { 'current_user': storage.get_session_user(token), 'type_class': type_class }

    @app.get('/')
    def index():
        user = storage.get_session_user(request.cookies.get('session'))
        # usar DB para listar meus envios
        reports = []
        if user:
            reports = db.get_reports_by_user(user['id'])
            # Adicionar informação de resposta para cada relatório
            for report in reports:
                response = db.get_response_by_report(report['id'])
                report['has_response'] = response is not None
        return render_template('index.html', reports=reports)

    @app.get('/login')
    def login_page():
        return render_template('login.html')

    @app.post('/login')
    def login_post():
        email_enova = request.form.get('email_enova', '').strip()
        matricula = request.form.get('matricula', '').strip()
        password = request.form.get('password', '')
        
        # Deve preencher email ENOVA OU matrícula
        if not email_enova and not matricula:
            return render_template('login.html', error='Preencha o email ENOVA ou a matrícula'), 400
        
        # Buscar por email ou matrícula
        if email_enova:
            user = storage.find_user_by_email(email_enova)
        else:
            user = db.get_user_by_matricula(matricula)
        
        if not user or user.get('passwordHash') != password:
            return render_template('login.html', error='Credenciais inválidas'), 401
        pub = { 'id': user['id'], 'name': user['name'], 'email': user['email'] }
        token = str(uuid.uuid4())
        storage.create_session(token, pub)
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie('session', token, httponly=True, samesite='Lax')
        return resp

    @app.get('/register')
    def register_page():
        return render_template('register.html')

    @app.post('/register')
    def register_post():
        tipo_registro = request.form.get('tipo_registro', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        
        # Validações básicas
        if not name or not password:
            return render_template('register.html', error='Preencha todos os campos obrigatórios'), 400
        
        # Validar senha: máximo 20 caracteres
        if len(password) > 20:
            return render_template('register.html', error='Senha deve ter no máximo 20 caracteres'), 400
        
        # Processar registro por ENOVA
        if tipo_registro == 'enova':
            email_enova = request.form.get('email_enova', '').strip()
            
            if not email_enova:
                return render_template('register.html', error='Preencha o email enova'), 400
            
            # Validar que é email ENOVA
            if not email_enova.endswith('@enova.educacao.ba.gov.br'):
                return render_template('register.html', error='Apenas emails @enova.educacao.ba.gov.br são aceitos'), 400
            
            # Verificar se email já existe
            if storage.find_user_by_email(email_enova):
                return render_template('register.html', error='Email enova já cadastrado'), 400
            
            try:
                storage.save_user({ 
                    'id': str(uuid.uuid4()), 
                    'name': name, 
                    'email': email_enova,
                    'matricula': '',  # Sem matrícula para registro ENOVA
                    'passwordHash': password,
                    'createdAt': datetime.now().isoformat()
                })
            except Exception as e:
                return render_template('register.html', error='Erro ao criar conta. Email já cadastrado ou dados inválidos.'), 400
        
        # Processar registro por Matrícula
        elif tipo_registro == 'matricula':
            matricula = request.form.get('matricula', '').strip()
            email_notificacao = request.form.get('email_notificacao', '').strip()
            
            if not matricula:
                return render_template('register.html', error='Preencha a matrícula'), 400
            
            # Validar matrícula: 8 dígitos, apenas números
            if not matricula.isdigit():
                return render_template('register.html', error='Matrícula deve conter apenas números'), 400
            if len(matricula) != 8:
                return render_template('register.html', error='Matrícula deve ter exatamente 8 dígitos'), 400
            
            # Verificar se matrícula já existe
            if db.get_user_by_matricula(matricula):
                return render_template('register.html', error='Matrícula já cadastrada'), 400
            
            # Se forneceu email de notificação, validar formato e verificar se já existe
            if email_notificacao:
                if '@' not in email_notificacao:
                    return render_template('register.html', error='Email inválido'), 400
                # Verificar se email já está em uso
                if storage.find_user_by_email(email_notificacao):
                    return render_template('register.html', error='Email já cadastrado'), 400
                email_final = email_notificacao
            else:
                # Criar email fictício único baseado na matrícula
                email_final = f"{matricula}@matricula.local"
                # Verificar se esse email fictício já existe (improvável, mas possível)
                if storage.find_user_by_email(email_final):
                    email_final = f"{matricula}_{uuid.uuid4().hex[:8]}@matricula.local"
            
            try:
                storage.save_user({ 
                    'id': str(uuid.uuid4()), 
                    'name': name, 
                    'email': email_final,
                    'matricula': matricula,
                    'passwordHash': password,
                    'createdAt': datetime.now().isoformat()
                })
            except Exception as e:
                return render_template('register.html', error='Erro ao criar conta. Email ou matrícula já cadastrados.'), 400
        else:
            return render_template('register.html', error='Tipo de registro inválido'), 400
        
        return redirect(url_for('login_page'))

    @app.post('/logout')
    def logout_post():
        token = request.cookies.get('session')
        storage.destroy_session(token)
        resp = make_response(redirect(url_for('index')))
        resp.delete_cookie('session')
        return resp
    
    @app.get('/profile')
    def profile_page():
        user = storage.get_session_user(request.cookies.get('session'))
        if not user:
            return redirect(url_for('login_page'))
        # Buscar dados completos do usuário
        full_user = db.get_user_by_id(user['id'])
        return render_template('profile.html', user=full_user)
    
    @app.post('/profile/email')
    def update_email():
        user = storage.get_session_user(request.cookies.get('session'))
        if not user:
            return redirect(url_for('login_page'))
        
        new_email = request.form.get('email', '').strip()
        if not new_email or '@' not in new_email:
            full_user = db.get_user_by_id(user['id'])
            return render_template('profile.html', user=full_user, error='Email inválido'), 400
        
        # Verificar se email já está em uso por outro usuário
        existing_user = storage.find_user_by_email(new_email)
        if existing_user and existing_user['id'] != user['id']:
            full_user = db.get_user_by_id(user['id'])
            return render_template('profile.html', user=full_user, error='Email já está em uso'), 400
        
        # Atualizar email no banco
        conn = db.get_conn()
        try:
            conn.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user['id']))
            conn.commit()
        finally:
            conn.close()
        
        return redirect(url_for('profile_page'))

    @app.post('/reports')
    def create_report():
        user = storage.get_session_user(request.cookies.get('session'))
        if not user:
            return redirect(url_for('login_page'))
        tipo = request.form.get('tipo', 'sugestão')
        titulo = request.form.get('titulo', '').strip()
        mensagem = request.form.get('mensagem', '').strip()
        turma = request.form.get('turma', '').strip()
        aluno = request.form.get('alunoNome', '').strip()
        anonimo = request.form.get('anonimo') == 'on'
        if not titulo or not mensagem:
            reports = storage.list_reports_by_user(user['id'])
            return render_template('index.html', reports=reports, error='Preencha os campos.'), 400
        report = {
            'id': str(uuid.uuid4()),
            'userId': user['id'],
            'tipo': tipo,
            'titulo': titulo,
            'mensagem': mensagem,
            'turma': '' if anonimo else turma,
            'alunoNome': '' if anonimo else aluno,
            'anonimo': anonimo,
            'createdAt': datetime.now().isoformat()
        }
        # salvar no DB
        db.insert_report(report)

        # Tentar enviar email para a escola (se configurado)
        try:
            send_report_email_to_school(report, user)
        except Exception as e:
            # Não quebra o fluxo do usuário se email falhar
            print(f"Erro ao enviar email: {e}")
        return redirect(url_for('index'))

    @app.get('/reports/<rid>')
    def view_report(rid: str):
        user = storage.get_session_user(request.cookies.get('session'))
        if not user:
            return redirect(url_for('login_page'))
        r = db.get_report_with_response(rid)
        if not r:
            return redirect(url_for('index'))
        # garantir que só o dono veja via link direto
        if r['userId'] != user['id'] and not is_admin_request(request):
            return redirect(url_for('index'))
        return render_template('view.html', r=r)

    @app.post('/reports/<rid>/delete')
    def delete_report(rid: str):
        user = storage.get_session_user(request.cookies.get('session'))
        if user:
            # só apaga se for dono
            r = db.get_report(rid)
            if r and r['userId'] == user['id']:
                db.delete_report(rid)
        return redirect(url_for('index'))

    # ADMIN
    @app.get('/admin')
    def admin_index():
        if not is_admin_request(request):
            return redirect(url_for('admin_login'))
        reports = db.get_all_reports()
        # Adicionar informações de resposta para cada relatório
        for report in reports:
            response = db.get_response_by_report(report['id'])
            report['has_response'] = response is not None
            if response:
                report['response'] = response
        return render_template('admin/index.html', reports=reports)
    
    @app.get('/admin/reports/<rid>')
    def admin_view_report(rid: str):
        if not is_admin_request(request):
            return redirect(url_for('admin_login'))
        report = db.get_report_with_response(rid)
        if not report:
            return redirect(url_for('admin_index'))
        # Buscar dados do usuário
        user = db.get_user_by_id(report['userId'])
        # Converter anonimo de int para bool se necessário
        if isinstance(report.get('anonimo'), int):
            report['anonimo'] = bool(report['anonimo'])
        # Se for anônimo, ocultar informações do usuário na interface
        if report.get('anonimo'):
            # Criar versão anonimizada do usuário para exibição
            if user:
                user_display = {
                    'name': 'ANÔNIMO',
                    'email': 'oculto@anonimo.local'  # Email fictício para não quebrar template
                }
            else:
                user_display = None
            report['user'] = user_display
            # Manter usuário real em campo separado para envio de email
            report['_user_real'] = user
        else:
            report['user'] = user
            report['_user_real'] = user
        return render_template('admin/view.html', report=report)
    
    @app.post('/admin/reports/<rid>/respond')
    def admin_respond(rid: str):
        if not is_admin_request(request):
            return redirect(url_for('admin_login'))
        report = db.get_report(rid)
        if not report:
            return redirect(url_for('admin_index'))
        
        admin_message = request.form.get('admin_message', '').strip()
        if not admin_message:
            return redirect(url_for('admin_view_report', rid=rid))
        
        # Salvar resposta no banco
        response = {
            'id': str(uuid.uuid4()),
            'report_id': rid,
            'admin_message': admin_message,
            'created_at': datetime.now().isoformat()
        }
        db.insert_response(response)
        
        # Enviar email para o manifestante (mesmo se for anônimo, o email ainda é enviado)
        try:
            user = db.get_user_by_id(report['userId'])
            if user:
                # Verificar se o email não é fictício (não termina com @matricula.local)
                user_email = user.get('email', '')
                print(f"[DEBUG] Tentando enviar email para: {user_email}")
                if user_email and not user_email.endswith('@matricula.local'):
                    print(f"[DEBUG] Email válido, enviando...")
                    result = send_response_email_to_user(report, user, admin_message)
                    if result:
                        print(f"[DEBUG] Email enviado com sucesso para {user_email}")
                    else:
                        print(f"[DEBUG] Falha ao enviar email - verifique configurações SMTP")
                else:
                    print(f"[DEBUG] Email é fictício ou inválido: {user_email}")
            else:
                print(f"[DEBUG] Usuário não encontrado para report {report['userId']}")
        except Exception as e:
            import traceback
            print(f"[ERRO] Erro ao enviar email de resposta: {e}")
            print(f"[ERRO] Traceback: {traceback.format_exc()}")
        
        return redirect(url_for('admin_index'))
    
    @app.post('/admin/reports/<rid>/delete')
    def admin_delete_report(rid: str):
        if not is_admin_request(request):
            return redirect(url_for('admin_login'))
        # Deletar resposta associada primeiro (se existir)
        response = db.get_response_by_report(rid)
        if response:
            conn = db.get_conn()
            try:
                conn.execute("DELETE FROM responses WHERE report_id = ?", (rid,))
                conn.commit()
            finally:
                conn.close()
        # Deletar relatório
        db.delete_report(rid)
        return redirect(url_for('admin_index'))

    @app.get('/admin/login')
    def admin_login():
        return render_template('admin/login.html')

    @app.post('/admin/login')
    def admin_login_post():
        user = request.form.get('user','').strip()
        pwd = request.form.get('password','')
        admin_user = os.getenv('ADMIN_USER')
        admin_pass = os.getenv('ADMIN_PASS')
        
        if not admin_user or not admin_pass:
            return render_template('admin/login.html', error='Admin não configurado'), 500
            
        if user == admin_user and pwd == admin_pass:
            resp = make_response(redirect(url_for('admin_index')))
            resp.set_cookie('admin', '1', httponly=True, samesite='Lax')
            return resp
        return render_template('admin/login.html', error='Credenciais inválidas'), 401

    @app.post('/admin/logout')
    def admin_logout():
        resp = make_response(redirect(url_for('admin_login')))
        resp.delete_cookie('admin')
        return resp

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)


