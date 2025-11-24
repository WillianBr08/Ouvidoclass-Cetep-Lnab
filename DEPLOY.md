# Deploy no Render.com

## Passo a Passo

1. Acesse [render.com](https://render.com) e crie uma conta (pode usar GitHub)

2. Clique em **"New +"** → **"Web Service"**

3. Conecte seu repositório GitHub:
   - Selecione o repositório: `WillianBr08/Ouvidoclass-Cetep-Lnab`
   - Branch: `main`

4. Configure o serviço:
   - **Name**: `ouvidoria-cetep-lnab` (ou outro nome)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd web_app && gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (gratuito)

5. Configure as variáveis de ambiente (Environment Variables):
   - `ADMIN_USER` - Usuário do administrador
   - `ADMIN_PASS` - Senha do administrador
   - `MAIL_FROM` - Remetente (mesmo email configurado no SendGrid)
   - `MAIL_TO` - Email(s) da escola (separe por vírgula)
   - `SENDGRID_API_KEY` - Chave da API gerada no SendGrid
   - `FLASK_DEBUG` - `false` (opcional)

> **Importante:** O Render bloqueia SMTP direto. Para enviar emails é necessário usar o SendGrid (ou outro serviço API). Crie uma conta gratuita em [sendgrid.com](https://sendgrid.com), valide o remetente e gere uma API Key com permissão “Full Access” ou “Mail Send”. Cole essa chave em `SENDGRID_API_KEY`.

6. Clique em **"Create Web Service"**

7. Aguarde o deploy (pode levar alguns minutos)

8. Seu site estará disponível em: `https://ouvidoria-cetep-lnab.onrender.com` (ou o nome que você escolheu)

## Notas

- O plano gratuito pode "adormecer" após 15 minutos de inatividade
- O primeiro acesso após dormir pode levar alguns segundos
- Para produção, considere um plano pago

