# recipe-box

A self-hosted recipe manager deployed on a home Raspberry Pi 5, accessible
privately via Tailscale.

## Purpose

Save recipes (tried or want-to-try), tag by cuisine/ingredients, search/filter,
attach YouTube source links, and keep a running notes log of modifications made
across multiple cooking attempts.

## Stack

- **Frontend**: React
- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 16
- **Reverse proxy**: Caddy (routes by path, no public TLS — Tailscale handles HTTPS).
  The Pi hosts multiple apps under one Tailscale hostname: `/` is a static
  homepage (lives on the Pi, not in this repo), recipe-box lives under
  `/recipe-box/*`. Caddy strips the `/recipe-box` prefix before forwarding,
  so the frontend and backend never see it — the frontend's Vite `base` and
  the API client derive the prefix from `import.meta.env.BASE_URL`, backend
  routes stay at `/api/*` internally.
- **Access**: Tailscale only — this app is never exposed to the public internet
- **Runtime**: Docker Compose, one container per service
- **Prod host**: Raspberry Pi 5, headless, reached over Tailscale — deploy target only

## Where development happens

**Claude Code runs on the laptop, never on the Pi.** The Pi is a deploy target,
not a dev environment — no live editing, no direct file changes there. Code is
authored, tested, and committed on the laptop; the Pi only ever pulls from
GitHub and runs `docker compose` (automatically, see Deployment pattern). If a task seems to require editing
files directly on the Pi, stop and flag it instead of doing it — it likely means
the change should go through git first.

## Project layout

recipe-box/
├── CLAUDE.md
├── TASKS.md
├── docker-compose.yml
├── .env.example          # placeholder values — real .env is gitignored
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── schemas.py
└── frontend/
    └── (React app)

Caddy config lives separately on the Pi in ~/caddy/ — not part of this repo,
don't touch unless explicitly asked to add a new route.

## Data model

Four tables — recipes, tags, recipe_tags (junction), notes:

- `recipes`: id, title, youtube_url, status (want_to_try | tried), rating,
  cook_count, last_made
- `tags`: id, name, type (cuisine | ingredient) — reused across recipes
- `recipe_tags`: many-to-many join between recipes and tags
- `notes`: id, recipe_id, content, created_at, superseded_by_id — multiple
  notes per recipe, forming a modification log. A note's `content` is
  immutable once written; "editing" a note inserts a new row and sets
  `superseded_by_id` on the old one to point at it. Only rows with
  `superseded_by_id IS NULL` are "current" — that's what list/detail views
  show; the superseded chain is available via a history endpoint.

## Conventions

- Backend connects to Postgres using the Docker service name `postgres` as
  hostname — they're on the same Docker network (`appnet`), never localhost/IP.
- No ports exposed on the Postgres container — only the backend talks to it,
  over the internal Docker network.
- New backend routes go under `/api/*` so Caddy can route cleanly by path.
- Keep secrets in `.env` (gitignored), referenced via `env_file` in
  docker-compose.yml — never hardcode credentials in source.
- UUIDs for primary keys, not auto-increment ints.

## Git workflow

- `main` is always deployable — never commit directly with broken code.
- Feature work on short-lived branches: `feature/recipe-crud`, `fix/note-timestamp`.
- Small, focused commits. Format: `type: short description`
  (e.g. `feat: add recipe search endpoint`, `fix: correct tag junction query`).
- Never commit `.env`. If a new secret/var is added, update `.env.example`
  with a placeholder instead.
- GitHub is the source of truth — the Pi only ever pulls from it, never the
  other way around.

## Security

- This app is Tailscale-only. Never suggest opening ports 80/443 publicly,
  adding a public domain, or removing the Tailscale Serve requirement.
- Database has no exposed port — only reachable from other containers on `appnet`.
- Secrets live in `.env` — never hardcoded, never logged, never returned in
  API error messages.
- Flag any security-relevant change explicitly (auth, exposed ports, new
  external dependencies) rather than making it silently.

## Testing and CI

- Backend tests live in `backend/tests/` (pytest + FastAPI `TestClient`) and
  run against a **real Postgres**, not mocks. `DATABASE_URL` must point at a
  database whose name ends in `_test` — the suite truncates all tables between
  tests and `conftest.py` refuses to run otherwise.
- Local run (throwaway DB + python 3.12 container, nothing touches the app stack):
  start `postgres:16` with `POSTGRES_DB=recipebox_test` on a scratch Docker
  network, then run `pytest` in a `python:3.12-slim` container with `backend/`
  mounted and `DATABASE_URL` set.
- GitHub Actions (`.github/workflows/ci.yml`) runs on every push: backend
  pytest (Postgres service container), frontend `npm run lint` + `npm run build`,
  and `docker compose config` + `docker compose build`.
- Schema changes go through Alembic (`backend/migrations/`). After changing
  `models.py`, generate a migration with `alembic revision --autogenerate -m "..."`
  (against a scratch DB), review it, and commit it. A test fails if the models
  drift from the migrations. The backend container runs `alembic upgrade head`
  on start, and tests build their schema through the same migrations. There is
  no `create_all`.
- `deploy/test/test_deploy.sh` tests the deploy script against a fake GitHub API
  and fake docker; it runs in CI together with shellcheck.

## Deployment pattern

Local (laptop) → PR → CI → merge to `main` → the Pi deploys itself.

A systemd timer on the Pi runs `deploy/deploy.sh` every 5 minutes. It fetches
`origin/main`, waits until every GitHub check on that exact commit has passed,
then: `docker compose build` → `alembic upgrade head` in a one-off backend
container (if a migration fails, the old version keeps running) →
`docker compose up -d --wait` → health checks directly and through Caddy.
State lives in `~/.recipe-box-deploy/` (`deployed`, `failed`); a failed commit
is not retried until a new commit lands. Logs: `journalctl -u recipe-box-deploy`.

- It is **pull-based on purpose**. This repo is public, so a self-hosted GitHub
  runner on the Pi would let anyone's pull request run code on it. The Pi only
  makes outbound requests; nothing on it is reachable from GitHub.
- Anything merged to `main` with green CI runs on the Pi, so protect `main` in
  GitHub (require a PR and passing checks) and treat write access as deploy access.
- One-time install on the Pi: `sudo ./deploy/install.sh`. A database created
  before Alembic must first be adopted with
  `docker compose run --rm --no-deps backend alembic stamp 0001`.
- Manual fallback: `cd ~/recipe-box && git pull && docker compose up -d --build`.

## Current status

- [x] Postgres container running on Pi
- [x] Caddy reverse proxy running on Pi, exposed via Tailscale Serve
- [x] FastAPI backend — CRUD endpoints for recipes, tags, and notes
- [x] React frontend — deployed at `/recipe-box/`
- [x] Wire backend into Caddyfile routing on Pi
- [x] First `git push` → Pi deploy cycle

See `TASKS.md` for granular task tracking.