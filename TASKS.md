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
- [x] Notes order fix: edited notes keep their original position (sorted by
      `original_created_at`), and the recipe card's `latest_note` is the last
      note *posted*, not the last edited

- [x] Alembic migrations: 0001 baseline, 0002 adopts the Pi's hand-applied
      `superseded_by_id` column; backend runs `alembic upgrade head` on start;
      a test fails if models drift from migrations
- [x] CD: pull-based deployer (`deploy/deploy.sh` + systemd timer), not a
      self-hosted runner -- repo is public, so a runner would let any PR run
      code on the Pi. Deploys `origin/main` once GitHub checks pass, with a
      backend healthcheck and both-side health verification after deploy
- [x] Pi's existing database stamped (`alembic stamp 0001`), running version
      confirmed at migration `0002`
- [x] `sudo ./deploy/install.sh` run on the Pi -- systemd timer installed
      and enabled, first tick completed successfully
- [x] Branch protection on `main`: require PR + all 4 CI checks, no direct
      pushes even for the owner. "Require approvals" deliberately left off
      -- GitHub won't let you approve your own PR, which would have made
      every PR on this solo repo permanently unmergeable (hit this live)
- [x] Fixed: `deploy/*.sh` were committed non-executable (`core.fileMode`
      was `false` on the authoring machine, so `chmod +x` never made it into
      git) -- caught when `sudo ./deploy/install.sh` failed with "command
      not found" on the Pi; fixed via `git update-index --chmod=+x`
- [x] README.md added: full architecture diagram, deployment rationale
      (pull-based vs. self-hosted runner), security decisions, schema
      migration story, testing approach

## Next

- [ ] Confirm a full unattended deploy loop: push -> PR -> merge -> Pi
      deploys within 5 min with zero manual `docker compose` commands
      (in progress -- see whether this README PR triggered it)

## Backlog / ideas

- [ ] Recipe search by ingredient text, not just tag match
- [ ] Bulk tag rename/merge UI
- [ ] Codify the Playwright smoke check as an e2e test
