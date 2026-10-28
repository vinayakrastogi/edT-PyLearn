# PyLearn and LifeAdmin over HTTP

## Current ngrok setup

The configured LifeAdmin endpoint is
`https://polygon-coastal-glazing.ngrok-free.dev`. Both `LIFEADMIN_API_URL` and
`LIFEADMIN_DOCKER_API_URL` in the local edT `.env` use that address. The existing
service API key remains unchanged.

In LifeAdmin, activate its environment and run `python scripts/run_api.py` to
start the API and fixed tunnel together. Start its Streamlit UI separately as
shown below. See LifeAdmin's `NGROK_SETUP.md` for your friend's setup. Stop the
old tunnel before starting the same endpoint on another computer. The hosting
device must stay online; edT's URL does not change with its Wi-Fi address.

The local/LAN addresses below remain available as alternatives. With ngrok,
substitute the fixed HTTPS URL for the host or LAN URL in each environment.

The projects are separate repositories and keep separate databases:

```text
Browser -> edT frontend :5173 -> edT API :8000 -> LifeAdmin API :8001 -> SQLite
                                   |                                   ^
                               PostgreSQL                      LifeAdmin UI :8501
```

PyLearn only calls HTTP endpoints. It never imports LifeAdmin code or opens its
SQLite database. LifeAdmin is not included in edT's Docker stack.

## edT: one-command startup

With Docker Desktop running, execute from `edT`:

```bash
docker compose up -d --build
```

Open `http://localhost:5173`. API docs: `http://localhost:8000/docs`.
Stop with `docker compose stop`. See [DOCKER_SETUP.md](DOCKER_SETUP.md).
Existing database data is preserved; do not add `-v` to normal shutdown commands.

## LifeAdmin: manual startup and login

In `LifeAdmin`, activate its own environment and run the API:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn lifeadmin.api:app --env-file .env --host 0.0.0.0 --port 8001
```

In another terminal in `LifeAdmin`:

```bash
source .venv/bin/activate
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Open `http://localhost:8501`. Both applications have these demo logins:

| Account | Email | Password |
|---|---|---|
| Student | `demostudent@example.com` | `demostudent` |
| Faculty | `demofaculty@example.com` | `demofaculty` |

LifeAdmin requires login before displaying data. Each user has private notes,
documents, reminders and activity history. Users can register in LifeAdmin.
Use the same email as in PyLearn to associate PyLearn lesson notes with that
LifeAdmin account. If it does not exist, PyLearn reports that registration is
required rather than creating an account silently.

LifeAdmin's database has been reset and the previous database backed up. Startup seeds the two demo accounts when `LIFEADMIN_SEED_DEMO_USERS=true`.
Run `python scripts/reset_database.py --confirm` only when you want a fresh database. This is an explicit reset, not a normal startup command. It backs
up the old database and starts with the two demo accounts, without demo documents
or notes. Sample documents can be loaded after login when wanted.

Default storage is `LifeAdmin/data/lifeadmin.db`. Both LifeAdmin processes must
use the same path if you customize `LIFEADMIN_DB`.

## API environment

`LifeAdmin/.env` contains a generated secret, at least 32 characters:

```dotenv
LIFEADMIN_API_KEY=<generated-secret>
LIFEADMIN_SOURCE_APP=pylearn
```

Use the same secret in `edT/.env`:

```dotenv
LIFEADMIN_API_KEY=<same-generated-secret>
LIFEADMIN_API_URL=http://127.0.0.1:8001
LIFEADMIN_DOCKER_API_URL=http://host.docker.internal:8001
LIFEADMIN_CLIENT_ID=pylearn
```

The Docker backend uses `LIFEADMIN_DOCKER_API_URL`; a manually started backend
uses `LIFEADMIN_API_URL`. `localhost` inside a container points to that container,
so Docker uses `host.docker.internal` to reach LifeAdmin on your computer.
Restart the backend after environment changes. Never use a `VITE_` variable for
this server-side secret. Keep the client ID stable to preserve lesson note scopes.

## Verify the flow

Sign in to PyLearn, open a lesson, and use **My lesson notes** to save a note.
LifeAdmin saves it and returns its ID, text and timestamp. Sign in to LifeAdmin
using the same email, open **Notes**, and refresh to see it. Delete from either
application and refresh the other to confirm the result. Repeated saves of an
unchanged draft reuse a request ID to avoid duplicate notes after a timeout.

The panel shows the latest 100 notes per lesson. Drafts stay on the current lesson
after an error; navigating away discards an unsaved draft. LifeAdmin's Notes page
shows the latest 100 notes belonging to its signed-in user, including personal
notes created there. LifeAdmin can be offline while the rest of PyLearn works.

## Two-device setup

If edT runs on device A (`192.168.1.10`) and LifeAdmin on device B (`192.168.1.20`):

1. Start LifeAdmin's API on B with `--host 0.0.0.0 --port 8001`.
2. On A set `LIFEADMIN_DOCKER_API_URL=http://192.168.1.20:8001` for Docker, or
   `LIFEADMIN_API_URL=http://192.168.1.20:8001` for a manual backend.
3. Use matching API keys, restart edT, and open `http://192.168.1.10:5173`.
4. Allow TCP 8001 on B and 5173 on A if blocked by a firewall. Guest-network
   client isolation can prevent communication between devices.

Replace sample IPs with actual LAN addresses. `0.0.0.0` is a bind address, not a
browser URL. `localhost` always means the device making the request. Use HTTPS
or a private encrypted network outside a trusted LAN.

## API contract

Integration endpoints require `X-API-Key`. PyLearn derives `owner_id` and
`owner_email` from its authenticated user; the browser cannot choose them.

| Method | LifeAdmin path | Request |
|---|---|---|
| POST | `/api/v1/notes` | JSON: `owner_id`, `owner_email`, `resource_id`, UUID `request_id`, `title`, `content` |
| GET | `/api/v1/notes` | Query: `owner_id`, `owner_email`, `resource_id`, optional `limit` (1-100) |
| DELETE | `/api/v1/notes/{uuid}` | Query: `owner_id`, `owner_email` |

The email must match a registered LifeAdmin account. The note also retains its
application, installation and lesson scope. The integration key is a privileged
server credential; end users use the separate login/Bearer-token API documented
in LifeAdmin's `API.md`. Personal endpoints derive ownership from that token.

PyLearn exposes authenticated GET/POST `/api/notes/{module_id}/{doc_id}` and
DELETE `/api/notes/{note_id}`. POST accepts only `content` and UUID `request_id`.
LifeAdmin returns 201 for saves, 200 for lists and 204 for deletion. PyLearn
reports 409 for a missing LifeAdmin account, 503 for an unreachable or
unconfigured service, 504 for timeouts and 502 for invalid upstream responses.

Interactive contracts: `http://localhost:8000/docs` and
`http://localhost:8001/docs`. Postman setup is a separate next step.
# Hosted demonstration

LifeAdmin's interface is https://lifeadmin-vinayakrastogi.onrender.com and its independent
API is https://lifeadmin-api-vinayakrastogi.onrender.com. The deployed edT backend uses
that API over HTTPS with the shared integration key. Each app has its own Neon database.
Set both `LIFEADMIN_API_URL` and `LIFEADMIN_DOCKER_API_URL` to the hosted API for local
edT use; allow 75 seconds for a cold start. The ngrok instructions below remain an
optional alternative for running LifeAdmin on a computer during local development.

