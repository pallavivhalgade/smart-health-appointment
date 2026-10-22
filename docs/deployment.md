# Deployment

## Vercel browsing demo

Vercel detects Django through `manage.py`. `pyproject.toml` selects the WSGI entrypoint and runs `scripts/vercel_build.py`; Vercel collects static files automatically.

Set these environment variables in the Vercel project:

| Variable | Value |
| --- | --- |
| `DJANGO_SECRET_KEY` | A long random value; keep it private |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_DEMO_MODE` | `true` |
| `DJANGO_ALLOWED_HOSTS` | The project's production hostname |

Vercel's deployment hostname is also allowed automatically through `VERCEL_URL`. A deployment without `DATABASE_URL` defaults to demo mode. The build creates a separate `demo.sqlite3` from migrations and six fictional doctor profiles. Runtime opens that file read-only. The committed/local development database is never uploaded.

Demo visitors can browse doctors, filter specialties, and submit example text to the keyword-based symptom checker. The demo saves neither symptom input nor results. Login, registration, administration, profile changes, and appointment writes are disabled, including direct POST requests. The seed accounts are inactive and have unusable passwords.

Deploy from the repository root:

```sh
vercel link
vercel deploy --prod
```

On Windows, use `vercel.cmd` if PowerShell blocks the CLI's script launcher.

## Enable the full application

1. Add a managed PostgreSQL database through Vercel Storage or your database provider. Set its `DATABASE_URL` in Vercel, using the provider's TLS and connection-pooling configuration.
2. Set `DJANGO_DEMO_MODE=false` and retain `DJANGO_DEBUG=false` and the private signing key.
3. Set `DJANGO_ALLOWED_HOSTS` to your hostname(s), comma-separated. If your proxy uses a different browser origin, set `DJANGO_CSRF_TRUSTED_ORIGINS` to its HTTPS origin(s).
4. Set `DJANGO_TIME_ZONE` to the clinic's IANA timezone. The default is UTC; all booking date and time checks use this setting.
5. Redeploy. The build runs `migrate` against the configured database. Back up existing data before changing schemas.
6. Create an administrator from a trusted environment connected to the same database with `python manage.py createsuperuser`.

Keep preview databases separate from production. Builds with `DATABASE_URL` run migrations, so use provider database branching or isolated credentials for previews. Do not point preview deployments at the production database.

Vercel local files cannot retain profile uploads. The upload field is disabled on Vercel until persistent object storage is implemented. The remaining profile fields work with PostgreSQL. Do not enable local SQLite for writable serverless deployments.

The application is an educational project. Doctor self-registration does not verify licenses, and the symptom checker is a keyword lookup rather than a diagnostic model. Evaluate privacy, clinical workflows, account verification, access controls, and operational requirements before accepting real patient data.

## Render or another persistent server

The corrected `Procfile` starts `gunicorn smarthealth.wsgi:application`. Install `requirements.txt`, set production environment variables, run migrations and `collectstatic`, and use PostgreSQL for persistent production data. WhiteNoise serves the static assets on these servers.

## Verification

- `/health/` returns `{"status":"ok"}` when the database is reachable and HTTP 503 otherwise. It exposes no database details.
- Check the home page, doctor filters, symptom checker, CSS, and a protected account URL after deploying.
- Production redirects HTTP to HTTPS, uses secure session and CSRF cookies, and requires a signing key supplied through the environment.

References: [Vercel Django deployment](https://vercel.com/docs/frameworks/full-stack/django), [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
