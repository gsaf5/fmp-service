# Claude Market API — Gary FMP Service

Live FMP data proxy for Claude conviction scoring, portfolio scans, and watchlist tracking.
Desktop and Mobile compatible.

## Live Service URLs

Primary: https://mktpxdata72.com
Backup: https://web-production-7e4e6.up.railway.app

## Endpoints

- `GET /ping` — health check (no auth required)
- `GET /quote?symbols=RKLB,ASTS,NVDA` — live batch quotes, any US ticker
- `GET /scan?symbols=RKLB,ASTS,KTOS` — price + RSI + volume for portfolio scan
- `GET /conviction?symbol=RKLB` — full conviction data: price, RSI, EPS history, income statement, key metrics, Altman Z, Piotroski, insider stats, analyst grades + price targets, news scan
- `GET /financials?symbol=RKLB&period=quarter&limit=4` — quarterly income statement, balance sheet, cash flow, key metrics, EPS history for any US ticker
- `GET /vet?symbol=RKLB` — Phase 0 vetting gate: insider, balance sheet, analyst coverage, price target, news red flags
- `GET /watchlist` — live watchlist with zone status (Z1/Z2) from GitHub Gist

All endpoints except `/ping` and `/` require header: `x-api-key: <secret>`

## Deployment

Deployed on Railway (grateful-ambition service). Auto-deploys on push to main.
GitHub repo: https://github.com/gsaf5/fmp-service

