# recipe-box

A self-hosted recipe manager: save recipes (tried or want-to-try), tag them
by cuisine/ingredient, search and filter, attach a YouTube source link, and
keep a running notes log across multiple cooking attempts. Runs on a home
Raspberry Pi 5, reachable only over Tailscale.

## Stack

- **Frontend**: React (Vite), served at `/recipe-box/` behind Caddy
- **Backend**: FastAPI (Python 3.12), routes under `/api/*`
- **Database**: PostgreSQL 16, schema managed by Alembic
- **Runtime**: Docker Compose, one container per service

## Development

All development happens on a laptop; the Pi is a deploy target only. See
[`CLAUDE.md`](Claude.md) for project conventions, the data model, and the
full local dev / testing setup, and [`TASKS.md`](TASKS.md) for what's done
and what's next.

## Deployment

Merging to `main` with passing CI is enough — a systemd timer on the Pi polls
GitHub every few minutes and deploys automatically once checks pass. Details
in `CLAUDE.md` under "Deployment pattern" and in [`deploy/`](deploy).
