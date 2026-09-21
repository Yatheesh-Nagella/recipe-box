# TASKS

Granular task tracking for recipe-box. See `CLAUDE.md` for the high-level
status checklist and project conventions.

## Done

- [x] Postgres + Caddy running on Pi
- [x] Backend scaffold: Dockerfile, SQLAlchemy models, Pydantic schemas
- [x] CRUD endpoints: `/api/recipes`, `/api/tags`, `/api/recipes/{id}/notes`
- [x] Recipe <-> tag attach/detach endpoints
- [x] Recipe list filtering (`status`, `tag`, `q`)
- [x] Postgres healthcheck + backend `depends_on: service_healthy`
- [x] Caddy bound to `127.0.0.1` only (was exposed on LAN via `0.0.0.0:80`)
- [x] Backend joined to `caddy_webnet` so Caddy can reach it by service name
- [x] Caddyfile routes `/api/*` to `backend:8000` without stripping the prefix
- [x] First Pi deploy cycle (`git pull` + `docker compose up -d --build`)
- [x] End-to-end verified: Tailscale HTTPS -> Caddy -> backend -> Postgres
- [x] React frontend scaffold (`frontend/`, Vite + React Router)
- [x] Frontend: recipe list view (search/filter by status, tag)
- [x] Frontend: recipe detail view (notes log, tags, YouTube link, rating)
- [x] Frontend: add/edit recipe form
- [x] Frontend: tag management UI
- [x] Frontend containerized (multi-stage build, nginx + SPA fallback)
- [x] Frontend joined to `caddy_webnet`, added to `docker-compose.yml`
- [x] Pi restructured for multi-app hosting: static homepage at `/`,
      recipe-box moved to `/recipe-box/*` (Caddy strips the prefix)
- [x] Dark/light theme toggle (CSS vars, system-preference default, persisted)
- [x] Browser tab title fixed ("frontend" -> "recipe-box")
- [x] Editable notes: edit-as-new-version model (`superseded_by_id`),
      "edited" badge, expandable history of prior versions
- [x] Tags UX simplified: dropped standalone Tags page, inline TagPicker
      on the recipe form, read-only pills on the detail page
- [x] Warm card-based UI redesign (list cards, note/tag styling, both themes)

- [x] Pi `notes.superseded_by_id` migration applied manually
- [x] Backend test suite (pytest, real Postgres, 32 tests, `_test`-DB guard)
- [x] GitHub Actions CI: backend tests, frontend lint + build, compose build

## Next

- [ ] Alembic migrations (prerequisite for automated deploys -- `create_all`
      never alters existing tables)
- [ ] CD: self-hosted GitHub runner on the Pi (outbound-only, fits
      Tailscale-only) running `git pull` + `docker compose up -d --build`
      after CI passes; update the "deploys are manual" line in CLAUDE.md
- [ ] Notes list order: an edited note is a new row, so it sorts by its edit
      time and jumps below newer notes -- sort by `original_created_at` instead

## Backlog / ideas

- [ ] Recipe search by ingredient text, not just tag match
- [ ] Bulk tag rename/merge UI
- [ ] Codify the Playwright smoke check as an e2e test
