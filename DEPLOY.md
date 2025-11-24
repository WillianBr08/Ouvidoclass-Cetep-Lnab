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
   - `SMTP_HOST` - smtp.gmail.com
   - `SMTP_PORT` - 587
   - `SMTP_USER` - seu-email@gmail.com
   - `SMTP_PASS` - senha do app
   - `MAIL_FROM` - seu-email@gmail.com
   - `MAIL_TO` - email que receberá as manifestações
   - `SMTP_STARTTLS` - true

6. Clique em **"Create Web Service"**

7. Aguarde o deploy (pode levar alguns minutos)

8. Seu site estará disponível em: `https://ouvidoria-cetep-lnab.onrender.com` (ou o nome que você escolheu)

## Notas

- O plano gratuito pode "adormecer" após 15 minutos de inatividade
- O primeiro acesso após dormir pode levar alguns segundos
- Para produção, considere um plano pago

