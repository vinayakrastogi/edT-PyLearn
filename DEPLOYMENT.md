# Demonstration deployment

edT and LifeAdmin remain separate repositories, applications and databases. This prepares
them for hosting; it does not create provider accounts or publish either application.

## edT on Render with Neon

Use a free Neon PostgreSQL database for edT and the combined edT Docker image on a Render
web service. `docker/backend.Dockerfile` now builds React as well as Python. With
`SERVE_FRONTEND=true`, FastAPI serves the React app and `/api` at **one HTTPS address**.
Login therefore uses first-party host-only cookies and works without third-party cookies.
Deep links such as `/dashboard` work, and missing API/assets still return 404.
The existing local Docker frontend/backend arrangement still works.

1. Push edT to its own repository and create a Render Docker web service.
2. Set the Dockerfile path to `docker/backend.Dockerfile`, context to the repo root,
   and health path to `/health`.
3. Add the settings shown in `.env.production.example` to the provider's environment
   settings. Replace placeholder hostnames and secrets; do not commit real credentials.
4. Generate **separate** `SECRET_KEY`, `SESSION_SECRET`, `LIFEADMIN_API_KEY` and
   `SANDBOX_RUNNER_KEY` values with `python -c 'import secrets; print(secrets.token_urlsafe(48))'`.
5. Use your assigned Render HTTPS URL for `FRONTEND_URL`, `BACKEND_CORS_ORIGINS` and
   `TRUSTED_HOSTS`. Only the hostname goes in `TRUSTED_HOSTS`.
6. Set `LIFEADMIN_API_URL` to the hosted LifeAdmin API and use its matching integration key.
   See LifeAdmin's independent `DEPLOYMENT.md` for its PostgreSQL and UI/API setup.

The entrypoint runs existing migrations and optional demo seeding, then listens on Render's
`PORT`. `FORWARDED_ALLOW_IPS=*` is appropriate only behind Render's trusted managed ingress;
it lets Uvicorn see the original HTTPS scheme. Do not expose a raw backend with arbitrary
forwarded headers trusted. Production also checks allowed hosts and redirects HTTP to HTTPS.

## Cookie settings and API clients

Production requires `COOKIE_SECURE=true`, random signing/session secrets, explicit trusted
hosts, HTTPS frontend/CORS origins and an isolated or disabled execution mode. Unsafe
production settings fail at startup. The same settings apply to login/signup/Google-login
cookies and logout. OAuth no longer globally disables HTTPS checks; update the Google
console's callback URL if using Google login on a new domain.

Keep `COOKIE_SAMESITE=lax` and omit `COOKIE_DOMAIN` for the recommended single-origin setup.
If separately hosting frontend/backend, set exact CORS origins and `VITE_API_URL` at frontend
build time. Truly cross-site cookies require `COOKIE_SAMESITE=none` with Secure, but browser
third-party-cookie policies can still block them; prefer the combined deployment.

Cookie-authenticated mutations check Origin/Referer. The frontend also sends
`X-CSRF-Protection: 1`. In Postman, add that header when reusing login cookies without an
Origin header. Requests with a foreign Origin are rejected even if they include the header.
The separate API-key-only public runner can be disabled with `PUBLIC_API_ENABLED=false`.

## Python execution

`SANDBOX_MODE=local` remains available only for local development. Production rejects it.
An ordinary subprocess shares too much of the backend's filesystem and process environment
to be a boundary for untrusted learner code.

For hosted execution, edT calls the separately authenticated runner in `runner/app.py`:

1. On a **Docker-capable host**, build the runtime image from the edT repository root:

   ```sh
   docker build -f docker/sandbox.Dockerfile -t pylearn-sandbox:latest .
   python -m venv .venv-runner
   .venv-runner/bin/pip install -r runner/requirements.txt
   export SANDBOX_RUNNER_KEY='YOUR_RANDOM_SECRET_OF_AT_LEAST_32_CHARACTERS'
   .venv-runner/bin/uvicorn runner.app:app --host 127.0.0.1 --port 8010
   ```

2. Expose that runner through trusted HTTPS ingress (for example an ngrok tunnel on its
   own assigned domain: `ngrok http 8010 --url https://YOUR_RUNNER_DOMAIN`). Keep the same
   secret in the backend's `SANDBOX_RUNNER_KEY`; set `SANDBOX_RUNNER_URL` to its HTTPS
   base URL and `SANDBOX_MODE=remote`. The browser never receives the runner key.
3. Each run launches a fresh unprivileged container with no network, no application
   mounts, no inherited application secrets, read-only root filesystem, capped RAM/CPU,
   limited processes/files, bounded output, and temporary work storage. Standard input,
   NumPy, pandas and Matplotlib PNG output are supported. Timeout cleanup removes the
   entire named container, including any child processes.
4. A runner outage returns HTTP 503; it never falls back to local execution and does not
   save a failed graded submission or award rewards. Concurrency is bounded on both ends.

**Free-host limitation:** Render's free web service cannot launch these Docker sandboxes.
This implementation does not invent an unrestricted free remote execution provider. You can
run the runner on an existing computer with Docker plus an HTTPS tunnel for the demonstration
(that computer must stay running), or supply another suitable Docker host. If no runner is
available, use `SANDBOX_MODE=disabled`: the rest of edT works and Run/Submit returns 503.
To run `SANDBOX_MODE=docker` directly, the backend process itself needs Docker CLI/daemon
access; the ordinary Render backend image deliberately does not have that access.

Do not share LifeAdmin's assigned ngrok domain with the runner without deliberately routing
both services. A second runner domain/account or separate reverse proxy is needed.

## Presentation limitation: files remain temporary

Persistent storage for uploaded originals or generated Module 0 content was deliberately
not added. Generated modules can disappear on a Render sleep/restart/redeploy, while
database records remain. Regenerate the module when needed for the demonstration.
Render free services also sleep when idle; wake the API services before presenting.

## Verification

Backend: `cd backend && python -m pytest tests -q`.
Runner tests from repo root: `python -m pytest runner/tests -q`.
With Docker and the sandbox image available, set `RUN_SANDBOX_INTEGRATION=1` for real
stdin/scientific-package/network/filesystem/timeout/container-cleanup checks.
