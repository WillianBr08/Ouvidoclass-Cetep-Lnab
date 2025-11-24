#!/usr/bin/env python3
"""Script para testar configuração de email"""

import os
import smtplib
from email.mime.text import MIMEText

def test_email_config():
    print("=== Teste de Configuração de Email ===\n")
    
    host = os.getenv('SMTP_HOST')
    port = int(os.getenv('SMTP_PORT', '587'))
    username = os.getenv('SMTP_USER')
    password = os.getenv('SMTP_PASS')
    mail_from = os.getenv('MAIL_FROM') or username
    mail_to = os.getenv('MAIL_TO')
    use_starttls = os.getenv('SMTP_STARTTLS', 'true').lower() in ('1','true','yes','on')
    
    print("Configurações:")
    print(f"  SMTP_HOST: {host or 'NÃO CONFIGURADO'}")
    print(f"  SMTP_PORT: {port}")
    print(f"  SMTP_USER: {username or 'NÃO CONFIGURADO'}")
    print(f"  SMTP_PASS: {'***' if password else 'NÃO CONFIGURADO'}")
    print(f"  MAIL_FROM: {mail_from or 'NÃO CONFIGURADO'}")
    print(f"  MAIL_TO: {mail_to or 'NÃO CONFIGURADO'}")
    print(f"  SMTP_STARTTLS: {use_starttls}")
    print()
    
    if not host or not username or not password:
        print("❌ ERRO: Configurações SMTP incompletas!")
        print("\nConfigure as variáveis de ambiente:")
        print("  export SMTP_HOST=smtp.gmail.com")
        print("  export SMTP_PORT=587")
        print("  export SMTP_USER=seu_email@gmail.com")
        print("  export SMTP_PASS=sua_senha")
        print("  export MAIL_FROM=seu_email@gmail.com")
        print("  export MAIL_TO=escola@exemplo.com")
        return False
    
    # Testar conexão
    print("Testando conexão SMTP...")
    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            print("✓ Conectado ao servidor")
            if use_starttls:
                print("Iniciando STARTTLS...")
                smtp.starttls()
                print("✓ STARTTLS iniciado")
            print("Fazendo login...")
            smtp.login(username, password)
            print("✓ Login realizado com sucesso")
            
            # Testar envio
            if mail_to:
                print(f"\nEnviando email de teste para {mail_to}...")
                msg = MIMEText("Este é um email de teste da Ouvidoria CETEP/LNAB", _charset='utf-8')
                msg['Subject'] = "[TESTE] Ouvidoria CETEP/LNAB"
                msg['From'] = mail_from
                msg['To'] = mail_to
                smtp.sendmail(mail_from, [mail_to], msg.as_string())
                print(f"✓ Email de teste enviado com sucesso para {mail_to}")
                print("\n✅ Configuração de email está funcionando!")
            else:
                print("\n⚠️  MAIL_TO não configurado, não foi possível enviar email de teste")
                print("   Mas a conexão SMTP está funcionando!")
            
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ ERRO: Falha de autenticação: {e}")
        print("\nVerifique:")
        print("  - Se o SMTP_USER e SMTP_PASS estão corretos")
        print("  - Se está usando 'Senha de App' no Gmail (não a senha normal)")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ ERRO SMTP: {e}")
        return False
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_email_config()

