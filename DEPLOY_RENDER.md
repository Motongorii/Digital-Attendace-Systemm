# Deploying to Render — exact steps

This guide explains how to deploy the Digital Attendance System to Render (https://render.com) using the Dockerfile already in the repo. Follow these steps exactly.

Prerequisites
- A Render account and a GitHub/GitLab account connected to Render.
- A PostgreSQL database (Render offers managed Postgres databases you can provision from the dashboard).
- Secret values: `DJANGO_SECRET_KEY`, `DATABASE_URL`, `FIREBASE_CREDENTIALS_JSON` (or use `FIREBASE_CREDENTIALS_PATH`), and optional storage credentials if you use GCS/S3 for media.

1) Add `release.sh` and Dockerfile
- The project already contains a `Dockerfile`. This repo includes `release.sh` which runs migrations, collects static files, then starts Gunicorn.

2) Connect your repository
- In Render: **New → Web Service** → choose your repo and branch (e.g., `main`).
- For **Environment**, choose **Docker** (not the language presets).
- For **Dockerfile Path** keep `Dockerfile`.

3) Set service settings
- Build Command: Use defaults (Render will use Dockerfile).
- Start Command: none required (CMD is in the Dockerfile and runs `/app/release.sh`).
- Instance Type: choose `Starter` for testing, scale up for production.

4) Add Environment Variables (Render dashboard → Environment → Environment Variables)
- `DJANGO_SECRET_KEY`: a long random secret (do NOT commit).
- `DATABASE_URL`: your Postgres connection string (e.g., `postgres://user:pass@host:5432/dbname`).
- `ALLOWED_HOSTS`: comma-separated hostnames (e.g., `your-service.onrender.com` or `yourdomain.com`).
- `CSRF_TRUSTED_ORIGINS`: comma-separated origins including protocol (e.g., `https://your-service.onrender.com`).
- `DEBUG`: `False` in production.
- `FIREBASE_CREDENTIALS_JSON`: (Recommended) base64-encoded JSON of service account or set `FIREBASE_CREDENTIALS_PATH` and upload JSON to a private store accessible at runtime. (Prefer secrets management.)

5) Provision Postgres (optional via Render)
- From Render: **New → PostgreSQL Database** and attach it to the service or copy the connection string into `DATABASE_URL`.

6) Deploy and verify
- Click **Create Web Service**. Render will build the Docker image and deploy.
- Watch build logs for successful `pip install` and final step `Starting Gunicorn on 0.0.0.0:$PORT`.
- Open the service URL to verify the site loads.

7) Post-deploy tasks
- If `release.sh` ran migrations automatically, DB will be up-to-date. If not, use Render's Shell access to run:

```bash
render services shell <service-name>
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Create admin without shell (for free plans)
-----------------------------------------
If you are on Render's free plan and can't access the Shell, you can create or update a superuser by adding temporary environment variables to the service and redeploying. The `release.sh` startup script will detect these and create the user automatically.

Add the following environment variables in the Render dashboard (Service → Environment):

- `CREATE_SUPERUSER_USERNAME`: e.g. `rizla`
- `CREATE_SUPERUSER_PASSWORD`: e.g. a strong temporary password
- `CREATE_SUPERUSER_EMAIL`: optional (defaults to `admin@example.com`)

Then trigger a redeploy (Manual Deploy or push). After the deploy completes, "Created superuser" or "Updated superuser" will be logged. Remove these env vars immediately afterward to avoid storing credentials in the environment.

Security note: Use a strong temporary password and rotate it immediately by logging in and changing the password in the admin UI.

8) Media files
- Local `MEDIA_ROOT` is not durable across instances. For production, configure Google Cloud Storage (`django-storages`) or S3 and set `DEFAULT_FILE_STORAGE` in settings using env vars. This repo already includes `google-cloud-storage` in `requirements.txt`.

9) Add domain and TLS
- In Render dashboard, add custom domain and enable SSL (Render provides automatic TLS certificates).

Example CLI (optional)
- If you prefer the `render` CLI, you can create services and set env vars. Use the Render docs/CLI for exact commands:

    - `render services create web --name <name> --repo https://github.com/<org>/<repo> --branch main --env docker --dockerfilePath Dockerfile`
    - Use the dashboard to add secrets: `DJANGO_SECRET_KEY`, `DATABASE_URL`, `FIREBASE_CREDENTIALS_JSON`.

Security notes
- Never commit service-account JSON or secrets to the repo. Use Render's secret/env var store.

Done — if you'd like, I can create a `render.yaml` (template included in repo) and open a PR, then guide you through connecting the repo to Render and setting required secrets.
