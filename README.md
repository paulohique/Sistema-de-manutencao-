# GLPI Manutenções

Sistema de manutenções com **espelho local** do GLPI:

- Integração com GLPI é **somente leitura (GET)**.
- Dados do GLPI são sincronizados e persistidos no MySQL local.
- CRUD (notas/manutenções) acontece **apenas** no banco local, sem alterar o GLPI.

## Rodar (Windows)

## Login (LDAP/AD)

O projeto tem uma tela de login em `/login` que autentica no **Active Directory via LDAP** e recebe um JWT.

- Backend: `POST /api/auth/login` (bind LDAP + emite JWT)
- Frontend: salva o token no `localStorage` e envia `Authorization: Bearer <token>` nos endpoints de escrita.

Configuração necessária no `python-api/.env` (baseado em [python-api/.env.example](python-api/.env.example)):

- `JWT_SECRET` (obrigatório)
- `LDAP_SERVER` (obrigatório)
- `LDAP_BASE_DN` (recomendado)
- `LDAP_DOMAIN` (opcional)

### 1) Popular o MySQL com dados do GLPI

Dentro de `python-api/`:

`python tools\run_sync.py`

Para validar quantidades no banco:

`python tools\db_counts.py`

### 2) Subir a API (FastAPI)

`python -m uvicorn --app-dir python-api main:app --host 127.0.0.1 --port 8002`

Health check:

`http://127.0.0.1:8002/api/health`

### 3) Subir o Frontend (Next.js)

Dentro de `Frontend/` (ou usando prefix):

`npm install`

`npm run dev`

Garanta que [Frontend/.env.local](Frontend/.env.local) aponte para a API:

`NEXT_PUBLIC_PY_API_URL=http://127.0.0.1:8002`
