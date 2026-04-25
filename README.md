# URL Shortener (FastAPI + Python)

A simple URL shortener you can use to learn **system design, data modeling, and architecture**, with a concrete backend implementation ready for local run and Railway deployment.

## Tech stack

- FastAPI
- SQLAlchemy
- PostgreSQL (Railway) or SQLite (local default)

## Features in this starter

- Create short URLs (`POST /api/v1/shorten`)
- Redirect by code (`GET /{code}`)
- Link stats (`GET /api/v1/links/{code}/stats`)
- Supports redirect status code: **301, 302, 307, 308**
- Optional custom alias and expiry time

## Project structure

- `app/main.py` – API routes and app setup
- `app/db.py` – DB engine/session setup
- `app/models.py` – SQLAlchemy models
- `app/schemas.py` – request/response models
- `app/utils.py` – short-code generator
- `requirements.txt` – dependencies
- `Procfile` – Railway start command

## API examples

### 1) Create short URL

`POST /api/v1/shorten`

```json
{
  "url": "https://example.com/very/long/path",
  "custom_alias": "optional-alias",
  "expires_at": "2026-12-31T00:00:00Z",
  "redirect_status_code": 307
}
```

### 2) Redirect

`GET /{code}`

### 3) Stats

`GET /api/v1/links/{code}/stats`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000/docs`

By default, local run uses SQLite via `DATABASE_URL=sqlite:///./urlshortener.db`.

## Deploy to Railway

Since your GitHub repo is already connected in Railway:

1. In Railway project, create a **PostgreSQL** service.
2. In your app service variables, set:
   - `DATABASE_URL` = your PostgreSQL connection string (Railway `postgres://...` is supported)
   - `APP_BASE_URL` = your public Railway URL (optional but recommended)
3. Push this repo; Railway will build and run using `Procfile`:
   - `web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
4. Verify:
   - `GET /health`
   - `POST /api/v1/shorten`
   - `GET /{code}`

## Learning next steps

- Add Redis cache for redirect hot-path.
- Add async click-event pipeline.
- Add rate limiting and abuse checks.
- Add user auth/multi-tenant ownership.
- Add Alembic migrations and CI tests.
