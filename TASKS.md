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

## Next

- [ ] React frontend scaffold (`frontend/`)
- [ ] Frontend: recipe list view (search/filter by status, tag, cuisine, ingredient)
- [ ] Frontend: recipe detail view (notes log, tags, YouTube link, rating)
- [ ] Frontend: add/edit recipe form
- [ ] Frontend: tag management UI
- [ ] Wire frontend into Caddy routing (`handle /* { reverse_proxy frontend:PORT }`)
- [ ] Frontend container added to `docker-compose.yml`

## Backlog / ideas

- [ ] Recipe search by ingredient text, not just tag match
- [ ] Bulk tag rename/merge
