# recipe-box

A self-hosted recipe manager: save recipes (tried or want-to-try), tag them
by cuisine/ingredient, search and filter, attach a YouTube source link, and
keep a running notes log across multiple cooking attempts. Runs on a home
Raspberry Pi 5, reachable only over Tailscale.

This document covers the infrastructure end to end — what runs where, and
why it was built this way — so the whole system is understandable without
reverse-engineering it from the code. Day-to-day conventions and the data
model live in [`CLAUDE.md`](Claude.md); what's done and what's next is in
[`TASKS.md`](TASKS.md).

## Stack

- **Frontend**: React (Vite), built to static files, served by nginx
- **Backend**: FastAPI (Python 3.12), routes under `/api/*`
- **Database**: PostgreSQL 16, schema managed by Alembic
- **Reverse proxy**: Caddy, routes by path
- **Access**: Tailscale only — never exposed to the public internet
- **Runtime**: Docker Compose, one container per service
- **CI**: GitHub Actions
- **Deploy**: a script + systemd timer on the Pi itself (see [Deployment](#deployment) below)

## Architecture

```
                    Tailscale (private, encrypted mesh network)
                                     │
                                     ▼
                     tailscale serve — terminates HTTPS,
                     forwards to Caddy on localhost only
                                     │
┌────────────────────────────────────┼────────────────────────────────────┐
│ Raspberry Pi 5 (Docker host)        ▼                                    │
│                          Caddy :80 (bound to 127.0.0.1 — see Security)   │
│                                     │                                    │
│                    ┌────────────────┼─────────────────┐                 │
│                    │                │                  │                │
│                 /  → homepage   /recipe-box/*   /recipe-box/api/*       │
│                 (static files,     │                    │                │
│                  Caddy's own       ▼                    ▼                │
│                  file_server,   frontend:80         backend:8000        │
│                  ~/caddy/       (nginx, static       (FastAPI)          │
│                  homepage/)      build, SPA                │            │
│                                  fallback)                 │            │
│                                                             ▼            │
│                                                   postgres:16            │
│                                                   (no published port)   │
│                                                                          │
│   networks: caddy_webnet (caddy, frontend, backend)                    │
│             appnet        (backend, postgres — postgres is on this     │
│                             one only, unreachable from caddy_webnet)   │
└──────────────────────────────────────────────────────────────────────┘
```

Caddy strips the `/recipe-box` prefix before forwarding, so neither
container ever sees it: the frontend's Vite `base` and the API client's
base path both come from `import.meta.env.BASE_URL`, and backend routes
stay at `/api/*` regardless of what's mounted in front of them. That's
what lets this Pi host more than one app under a single Tailscale hostname
— a second app would just be another path prefix and another `handle`
block in the Caddyfile.

## Deployment

**Local (laptop) → PR → CI → merge to `main` → the Pi deploys itself.**
Nothing is deployed by pushing or by SSHing in; deploys only happen because
the Pi decided, on its own, that it was time to pull.

A systemd timer runs [`deploy/deploy.sh`](deploy/deploy.sh) every 5 minutes.
Each run:

1. Fetches `origin/main` and compares it to what's already deployed.
2. If it moved, asks GitHub's check-runs API whether every check on that
   exact commit passed. If CI hasn't finished, or failed, it does nothing
   and tries again next cycle.
3. If CI passed: `docker compose build` → `alembic upgrade head` in a
   one-off backend container → `docker compose up -d --wait` → curls the
   backend directly and curls it again through Caddy.
4. Records the outcome in `~/.recipe-box-deploy/` (`deployed` or `failed`).
   A failed commit is not retried until a newer commit lands — it doesn't
   loop forever trying the same broken thing every 5 minutes.

If step 3's migration fails, it fails *before* `docker compose up` swaps
the containers, so the previous (working) version just keeps running. A
`flock` around the whole run stops two deploys from overlapping if one
ever takes longer than 5 minutes.

### Why pull, not a GitHub-hosted runner

The obvious way to automate this would be a self-hosted GitHub Actions
runner on the Pi, triggered by a workflow on push to `main`. That was
rejected on purpose: **this repo is public**, and a self-hosted runner
executes whatever the workflow file in a given commit says. On a public
repo that means anyone who can open a pull request has a path to getting
code executed on hardware sitting in this house, unless the runner is
locked down far more carefully than a personal project's CI usually is.

The pull-based deployer inverts the trust direction instead. The Pi only
ever makes outbound requests — to GitHub's public API to check commit and
CI status, and that's it. Nothing on GitHub can reach into the Pi; there
is no inbound webhook, no runner registration token, no listener waiting
for GitHub to call it. The Pi decides for itself, on its own schedule,
whether to trust what it sees.

That trust model only holds if `main` can't be moved without going through
CI, which is why branch protection matters here specifically:

- **Require a pull request before merging** — no direct pushes to `main`.
- **Require status checks to pass** — all four CI jobs (`backend`,
  `frontend`, `compose`, `deploy-script`) must be green.
- **"Do not allow bypassing the above settings"** is turned on, so this
  applies to the repo owner too, not just hypothetical other contributors.
- **"Require approvals" is deliberately off.** GitHub won't let you approve
  your own pull request — turning this on for a solo repo would mean every
  PR is permanently unmergeable. (Found this the hard way: turned it on,
  then couldn't merge the very next PR.)

### One-time setup on a fresh Pi

```bash
cd ~/recipe-box
git pull
docker compose build backend
# adopt a database that predates Alembic (skip this on a brand new DB)
docker compose run --rm --no-deps backend alembic stamp 0001
docker compose up -d --build
sudo ./deploy/install.sh   # installs and enables the systemd timer
```

`deploy/install.sh` templates `deploy/recipe-box-deploy.{service,timer}`
with the invoking user and repo path and installs them under
`/etc/systemd/system/`. Logs: `journalctl -u recipe-box-deploy`.

### Manual fallback

If the automation is ever down or you need to force a deploy:

```bash
cd ~/recipe-box && git pull && docker compose up -d --build
```

## Security decisions

A few things were deliberately configured this way, found and fixed during
setup rather than designed up front — worth recording so they don't get
silently reverted:

- **Caddy binds to `127.0.0.1:80`, not `0.0.0.0:80`.** It was originally
  the latter, which meant anyone on the same home Wi-Fi — not just
  Tailscale-authenticated devices — could reach the app directly by IP.
  `tailscale serve` talks to Caddy over `localhost` regardless, so binding
  to loopback only closes the LAN-wide hole without affecting the
  Tailscale path at all.
- **Postgres has no published port.** It's reachable only from the backend,
  over the internal `appnet` Docker network — not even from other
  containers on `caddy_webnet`, let alone the host or LAN.
- **Backend's own port (`127.0.0.1:8000`) is loopback-only**, kept around
  for local debugging on the Pi itself, never exposed further.
- **Secrets live in `.env`** (gitignored), referenced via `env_file` in
  `docker-compose.yml`. `.env.example` holds placeholders so the real
  shape of the config is still visible in git.

## Schema migrations

Managed by Alembic (`backend/migrations/`), not SQLAlchemy's `create_all`
— `create_all` only creates tables that don't exist yet; it silently does
nothing to a table that's already there, so a column added to a model
would never reach a running database. That's exactly what happened once:
`notes.superseded_by_id` was first added by hand with a raw `ALTER TABLE`
over SSH, and even then came out missing the `UNIQUE` constraint the model
declares — migration `0002` exists specifically to reconcile that
hand-patched database with what the models actually say.

The backend container runs `alembic upgrade head` on every start, before
serving any requests. A test (`backend/tests/test_migrations.py`) fails if
the models and the migrations ever drift apart, so that kind of gap gets
caught in CI instead of discovered on production data again.

## Testing

Backend tests (`backend/tests/`, pytest + FastAPI's `TestClient`) run
against a **real Postgres**, not mocks — `DATABASE_URL` must point at a
database whose name ends in `_test`, since the suite truncates every table
between tests; `conftest.py` refuses to run otherwise. The deploy script
itself has its own test suite (`deploy/test/test_deploy.sh`) that exercises
it against a fake GitHub API and a stubbed `docker` binary, covering
pending/failing CI, a failed migration, a failed health check, and that a
failed commit isn't retried until a newer one lands.

GitHub Actions (`.github/workflows/ci.yml`) runs all of this on every
push: backend pytest, frontend lint + build, `docker compose config` +
`build`, and shellcheck + the deploy script's own tests.

## Repo layout

```
recipe-box/
├── README.md              # this file
├── CLAUDE.md               # dev conventions, data model, local setup
├── TASKS.md                 # granular progress tracking
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml
├── backend/
│   ├── main.py, database.py, models.py, schemas.py
│   ├── routers/            # recipes, tags, notes
│   ├── migrations/         # Alembic
│   └── tests/
├── frontend/                # React app (Vite)
└── deploy/
    ├── deploy.sh             # the pull-based deployer
    ├── install.sh            # one-time systemd setup
    ├── recipe-box-deploy.{service,timer}
    └── test/test_deploy.sh
```

Caddy's own config lives separately on the Pi in `~/caddy/` — it's shared
across every app the Pi hosts, not specific to recipe-box, so it isn't
part of this repo.
