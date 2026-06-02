# Gary FMP Price Service

Live FMP pricing service for Claude scans — Desktop and Mobile.

## Endpoints

- `GET /` — health check
- `GET /quote?symbols=NVDA,GOOG,AAPL` — live quotes (comma separated)
- `GET /news?symbol=NVDA` — latest 5 news items
- `GET /insider?symbol=NVDA` — latest insider trades
- `GET /earnings?symbol=NVDA` — last 4 earnings reports

## Deployment

Deployed on Railway. Auto-deploys on push to main.
