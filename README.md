# RocketMail — backend Django

API REST do **RocketMail**, uma rede social no estilo Twitter/X. Este repositório é uma reimplementação em **Django 5 + DRF**, compatível 1:1 com o frontend existente (paths, bodies, status HTTP e `{"detail": "..."}`).

- Frontend: [https://rocket-mail-site.vercel.app](https://rocket-mail-site.vercel.app)
- Repositório do front: [RocketMailFrontEnd](https://github.com/RaulLTomaz/RocketMailFrontEnd)

O app React Native/web chama esta API no browser. **CORS quebrado = produto quebrado.**

## Stack

- Python 3.12+
- Django 5 + Django REST Framework
- PostgreSQL (`psycopg`)
- JWT HS256 (`djangorestframework-simplejwt` customizado: `{access_token, token_type}` e payload `sub`/`iat`/`exp`)
- django-cors-headers
- Cloudinary (fotos em produção)
- gunicorn
- pytest + pytest-django

## Estrutura

```
config/          # settings (base/dev/prod/test), urls, wsgi, asgi
apps/
  core/          # healthz, storage (Cloudinary/local), exceptions, throttles
  usuarios/      # model Usuario, JWT, perfil, search, stats
  posts/         # posts, feed
  seguir/
  likes/
tests/
```

Camadas: views finas → serializers (IO) → services (regras/queries) → models.

## Setup local

### 1. PostgreSQL

Crie os bancos:

```sql
CREATE DATABASE rocketmail;
CREATE DATABASE rocketmail_test;
```

### 2. Ambiente Python

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Ajuste `DATABASE_URL` e `SECRET_KEY` no `.env`. Em produção use `pip install -r requirements.txt` (sem pytest).

### 3. Migrar e rodar

```bash
python manage.py migrate
python manage.py runserver 8000
```

Health check: [http://localhost:8000/healthz](http://localhost:8000/healthz) → `{"status":"ok"}`.

No front local, aponte `EXPO_PUBLIC_API_URL` / `API_URL` para `http://localhost:8000`.

## Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `PYTHON_ENV` | `dev`, `test` ou `production` |
| `SECRET_KEY` | Obrigatória e forte em produção |
| `ALLOWED_HOSTS` | **Obrigatório em produção** (ex.: `rocketmail-django.onrender.com,.onrender.com`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default `120` |
| `DATABASE_URL` | Postgres (`postgres://` é normalizado para `postgresql://`) |
| `DATABASE_SSL` / `DATABASE_SSL_VERIFY` | SSL; verify default off (Render) |
| `ALLOWED_ORIGINS` | CSV de origins CORS (localhost é removido automaticamente em prod) |
| `ALLOWED_ORIGIN_REGEX` | Default: previews do projeto na Vercel |
| `PUBLIC_BASE_URL` | URL pública da API (produção: `https://rocketmail-django.onrender.com`) |
| `CLOUDINARY_URL` | Obrigatório em produção para upload de foto |
| `RUN_MIGRATIONS` | `1` no Render para `migrate --noinput` no boot |
| `FOTO_MAX_BYTES` | Default 5 MB |
| `THROTTLE_LOGIN` / `THROTTLE_REGISTRO` | Rate limit (default `30/min` e `20/min`) |

## Testes

Copie `.env.example` para `.env.test` (ou exporte `DATABASE_URL_TEST`) apontando para `rocketmail_test`.

```bash
pip install -r requirements-dev.txt
pytest
```

A suíte cobre cadastro/login JWT (claims, expiração), posts, feed priorizado, seguir, likes (incl. batch e post inexistente), search, fotos (magic bytes), healthz, CORS e cascade ao deletar conta.

## Deploy no Render

1. Crie o repositório no GitHub e conecte no [Render](https://render.com) via `render.yaml` (Blueprint) ou Web Service manual.
2. O addon Postgres injeta `DATABASE_URL`.
3. `PUBLIC_BASE_URL` e `ALLOWED_HOSTS` já vêm no `render.yaml`.
4. Crie conta no [Cloudinary](https://cloudinary.com) e cole `CLOUDINARY_URL` no dashboard (`cloudinary://API_KEY:API_SECRET@CLOUD_NAME`). Sem isso, `POST /usuario/me/foto` responde **503** (disco do Render é efêmero).
5. `SECRET_KEY` é gerada pelo `render.yaml`. `RUN_MIGRATIONS=1` executa `migrate` no start.

Start command (Blueprint):

```bash
bash -c 'if [ "$RUN_MIGRATIONS" = "1" ]; then python manage.py migrate --noinput; fi; gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --timeout 120 --max-requests 1000 --max-requests-jitter 50'
```

## Auth (contrato do front)

- Login: `POST /usuario/login` com `application/x-www-form-urlencoded` (`username` = e-mail, `password` = senha).
- Resposta: `{"access_token": "<jwt>", "token_type": "bearer"}`.
- Senha no cadastro/PATCH: mínimo 8 caracteres, 1 maiúscula, 1 número e 1 símbolo (igual ao front).
- Demais rotas autenticadas: `Authorization: Bearer <jwt>`.
- Erros: `{"detail": "mensagem em português"}` em JSON UTF-8. Sem token → `401` + `WWW-Authenticate: Bearer`.
- Login/registro têm rate limit (429 se abusados).
