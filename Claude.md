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
- **Reverse proxy**: Caddy (routes by path, no public TLS — Tailscale handles HTTPS)
- **Access**: Tailscale only — this app is never exposed to the public internet
- **Runtime**: Docker Compose, one container per service
- **Prod host**: Raspberry Pi 5, headless, reached over Tailscale — deploy target only

## Where development happens

**Claude Code runs on the laptop, never on the Pi.** The Pi is a deploy target,
not a dev environment — no live editing, no direct file changes there. Code is
authored, tested, and committed on the laptop; the Pi only ever runs
`git pull` + `docker compose up -d --build`. If a task seems to require editing
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
- `notes`: id, recipe_id, content, created_at — multiple notes per recipe,
  never overwrite, always append (this is the modification log)

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

## Deployment pattern

Local (laptop) → commit → push to GitHub → SSH into Pi → pull → rebuild.
This repo does not run deploy commands itself — deploying is a manual step
done over SSH once code is pushed:

```bash
# On the Pi, after code is pushed to GitHub:
cd ~/recipe-box
git pull
docker compose up -d --build backend   # rebuild only what changed
```

## Current status

- [x] Postgres container running on Pi
- [x] Caddy reverse proxy running on Pi, exposed via Tailscale Serve
- [x] FastAPI backend — CRUD endpoints for recipes, tags, and notes
- [ ] React frontend — not yet started
- [x] Wire backend into Caddyfile routing on Pi
- [x] First `git push` → Pi deploy cycle

See `TASKS.md` for granular task tracking.