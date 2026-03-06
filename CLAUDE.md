# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

성남시 수영장 자유수영 스케줄 통합 시스템 (Seongnam City public pool free-swim schedule system). A monorepo with three services:

- **parser** (`services/parser/`) - Crawls pool schedule notices, extracts HWP/PDF text, parses via Claude API, saves to MariaDB
- **api** (`services/api/`) - FastAPI backend serving schedule data with Redis caching
- **frontend** (`services/frontend/`) - React/TypeScript/Tailwind SPA

## Common Commands

### Full Stack (Docker)
```bash
make init          # Copy .env.example files (first-time setup)
make build         # Build all Docker images
make up            # Start all services (detached)
make down          # Stop all services
make logs          # Tail logs from all services
make clean         # Remove containers, volumes, built artifacts
make db-shell      # Connect to MariaDB shell
make parser-run    # Run parser once via Docker
```

### API (local development)
```bash
cd services/api
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Parser (local development)
```bash
cd services/parser
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements/dev.txt

python main.py                          # Full pipeline (crawl → parse → save)
python main.py --crawl                  # Crawl only
python main.py --parse                  # LLM parse only
python main.py --save                   # DB save only
python main.py --keyword 수영 --max-pages 3
python main.py --test-discord           # Test Discord notification
python scheduler.py                     # Run with APScheduler (daily at midnight KST)
```

### Frontend (local development)
```bash
cd services/frontend
npm install
npm run dev      # Dev server
npm run build    # Production build (tsc && vite build)
npm run lint     # ESLint
```

## Architecture

### Parser Pipeline
`crawl → parse → save_to_db → save_base_schedule_fallbacks`

1. **Crawl** (`core/crawler/`) - Two target organizations: `snyouth` (성남시청소년재단) and `snhdc` (성남시시설관리공단). Each has concrete implementations of `list_crawler`, `detail_crawler`, `attachment_downloader`, `facility_info_crawler` extending base classes.
2. **Parse** (`core/parser/`) - Extracts text from HWP/PDF attachments, sends to Claude API (`llm/llm_parser.py`), validates `valid_month` against notice date to filter bad parses.
3. **Save** (`infrastructure/database/repository.py`) - Upserts into MariaDB via PyMySQL. Also triggers Discord notifications via `infrastructure/notification/`.
4. **Fallback** (`application/fallback_service.py`) - For facilities with no notice found, generates entries from base schedule data.

Storage: intermediate JSON files written to `STORAGE_DIR` between pipeline stages.

### API Layer (DDD-style)

```
presentation/   → FastAPI routes (controllers)
application/    → Service classes (business logic)
domain/         → SQLAlchemy ORM models + repository interfaces
infrastructure/ → DB connection (SQLAlchemy engine), Redis cache
shared/         → Settings, logging, utilities
```

Key domain models: `Facility`, `SwimSchedule`, `SwimSession`, `Notice`, `Fee`, `FacilityClosure`, `Review`.

Tables are auto-created on startup via `Base.metadata.create_all()`. Season logic (하절기/동절기) is applied at query time based on `valid_month` month number — schedules store a `season` field and the service filters to match.

API endpoints (all under `/api`):
- `GET /api/facilities`
- `GET /api/schedules?facility=&month=YYYY-MM`
- `GET /api/schedules/daily?date=YYYY-MM-DD`
- `GET /api/schedules/calendar?year=&month=`
- `GET /api/reviews`, `POST /api/reviews`

All GET endpoints use `fastapi-cache2` with Redis. Cache TTLs are configured in `settings.py`.

### Frontend

Two pages routed by React Router:
- `DailySchedule` - shows all facilities for a selected date
- `FacilityPage` - facility detail with date/monthly tabs and reviews

API calls are centralized in `services/api.ts`. Types in `types/schedule.ts` and `types/review.ts`.

## Environment Variables

Root `.env` is shared across services (parser and api both read from it via `python-dotenv`). Key variables:

| Variable | Used by |
|---|---|
| `DB_HOST/PORT/USER/PASSWORD/NAME` | api, parser |
| `ANTHROPIC_API_KEY` | parser (Claude API for LLM parsing) |
| `REDIS_HOST/PORT` | api, parser |
| `DISCORD_WEBHOOK_URL` | parser (optional; Discord notifications enabled when set) |
| `LOKI_ENABLED`, `LOKI_URL` | api, parser (structured log shipping) |
| `ENV` | api (`dev`/`prod`) |

## CI/CD

GitHub Actions (`.github/workflows/deploy-dev.yml`) triggers on push to `main`:
1. Parallel Docker image builds for parser, api, frontend → pushed to GHCR
2. SSH deploy to server: copies `docker-compose.dev.yml` as `docker-compose.yml`, pulls images, restarts
3. Health check against `http://<host>:80/health`

Required GitHub secrets: `SSH_PRIVATE_KEY`, `SSH_HOST`, `SSH_USER`, `DB_ROOT_PASSWORD`, `DB_PASSWORD`, `ANTHROPIC_API_KEY`, `GRAFANA_PASSWORD`, `DISCORD_WEBHOOK_URL`.

## Monitoring

`monitoring/` contains Prometheus, Loki, and Grafana configs. Grafana is accessible on port 3001 in dev (see `docker-compose.dev.yml`).
