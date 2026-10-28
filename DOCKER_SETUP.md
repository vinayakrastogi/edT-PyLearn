# Start edT with Docker

From `edT`, with Docker Desktop running:

```bash
docker compose up -d --build
```

On a fresh checkout only, copy `.env.example` to `.env` before starting and fill
in your API keys. Do not replace an existing configured environment file.

| Service | How it runs | URL |
|---|---|---|
| Frontend | Built React app served by Nginx | http://localhost:5173 |
| Backend | FastAPI / Uvicorn, Python 3.14 | http://localhost:8000/docs |
| Database | PostgreSQL 16, persistent volume | localhost:5432 |

Compose starts the services in order, waits for database health, runs Alembic
migrations, and starts the backend before the frontend. No separate terminals,
local Python environment or local Node installation are required. The three
services appear together as the `edt` stack in Docker Desktop.

The requested presentation accounts are created or updated on startup:

| Account | Email | Password |
|---|---|---|
| Student | `demostudent@example.com` | `demostudent` |
| Faculty | `demofaculty@example.com` | `demofaculty` |

The original demo learner is renamed to the demo student, preserving its ID and
progress. The two demo passwords and edT roles are kept consistent on startup;
unrelated accounts are unchanged. `SEED_DEMO_USER=false` disables this seeding.
Use the faculty account for AI generation and other faculty-only features.

## Stop, restart, inspect

```bash
docker compose stop                 # stop all edT services; keep their data
docker compose up -d               # start again using the built images
docker compose ps                 # service status
docker compose logs -f backend     # backend logs (Ctrl+C exits log viewing)
docker compose up -d --build       # rebuild after code changes
```

`docker compose down` also removes the containers and network while preserving
the database volume. Adding `-v` deletes the database; it is not part of normal
startup or shutdown. Stop any manually started edT processes first to free ports
5173, 8000 and 5432.

## Persistence and configuration

PostgreSQL uses the existing `edt_postgres_data` named volume. The `content/`
folder is mounted into the backend, so generated modules survive restarts.
Environment files and credentials are excluded from Docker image builds.

The backend loads `backend/.env`, then root `.env`; root values take precedence.
Compose overrides the database URL to use its internal `postgres` hostname.
`GROQ_API_KEY` is required for AI generation; it is never sent to the frontend.

The frontend uses Nginx to forward `/api` requests to the backend. This keeps
login cookies and API calls on the same browser origin and supports page refresh
on lesson routes. AI requests have a longer proxy timeout. This is a built
frontend; edit source and rebuild to see code changes.

Learner Python code runs as a subprocess inside the non-root backend container,
with the existing timeout, output limits and resource limits. NumPy, pandas and
Matplotlib are installed. This local-demo setup shares the backend container;
it does not create a fresh isolated container per submission.

## LifeAdmin stays outside Docker

The current root `.env` uses
`LIFEADMIN_DOCKER_API_URL=https://polygon-coastal-glazing.ngrok-free.dev`.
LifeAdmin's `python scripts/run_api.py` starts its API and ngrok tunnel on the
hosting computer. This works when LifeAdmin is on your computer or your friend's
computer; the URL stays the same. See its `NGROK_SETUP.md` for moving hosts.

The host-address settings below are the local/LAN alternative to ngrok.

Start LifeAdmin's API and Streamlit UI manually in its own project. The Docker
backend uses this root `.env` setting to reach the API on your computer:

```dotenv
LIFEADMIN_DOCKER_API_URL=http://host.docker.internal:8001
LIFEADMIN_API_KEY=<same-key-as-LifeAdmin>
```

`host.docker.internal` means the computer hosting Docker. The ordinary
`LIFEADMIN_API_URL=http://127.0.0.1:8001` setting is for running the backend
manually, outside Docker. Compose selects the Docker-specific URL automatically.
For LifeAdmin on another device, set `LIFEADMIN_DOCKER_API_URL` to that device's
LAN URL instead. Its API must bind to `0.0.0.0:8001`.

Sign in to both applications using the same email. The LifeAdmin demo accounts
have the same credentials listed above. Other users register their own LifeAdmin
account; notes are associated with that account and visible only after login.

## Optional pgAdmin

```bash
docker compose --profile tools up -d
```

Open `http://localhost:5050` using `PGADMIN_EMAIL` and `PGADMIN_PASSWORD` from
`.env`. To register the database, use host `postgres`, port 5432, and the configured
PostgreSQL credentials. It is optional and is not needed by the app.

## Another browser on your network

Open `http://<edT-computer-LAN-IP>:5173`. Browser API calls still use Nginx's
same-origin proxy. If using Google OAuth, update `FRONTEND_URL` and register its
callback separately. Email/password works for the local-network demonstration.
# Hosted deployments

This guide describes the local stack. See [DEPLOYMENT.md](DEPLOYMENT.md) for HTTPS
production settings, same-origin frontend hosting and the separate isolated runner.
