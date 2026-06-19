# AI Tool Risk Profiler

Automated security scoring for AI tools — built for Oximy.

## Project structure

```
app/
├── __init__.py
├── main.py       # FastAPI app, routes only
├── config.py     # Env vars and constants
├── schemas.py    # Pydantic request/response models
├── scraper.py    # Fetches privacy/security pages from a domain
├── extractor.py  # LLM extraction via OpenRouter
├── scoring.py    # Trust score calculation
└── database.py   # Supabase persistence
run.py            # Entry point (python run.py)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python run.py
```

## Environment variables

| Variable           | Required | Description                        |
|--------------------|----------|------------------------------------|
| `API_KEY_SECRET`   | Yes      | Secret for X-API-Key header        |
| `OPENROUTER_API_KEY` | Yes    | OpenRouter API key                 |
| `SUPABASE_URL`     | No       | Supabase project URL               |
| `SUPABASE_KEY`     | No       | Supabase anon/service key          |

## API

### `POST /analyze`

**Header:** `X-API-Key: <your-key>`

**Body:**
```json
{ "domain": "slack.com" }
```

**Response:**
```json
{
  "success": true,
  "domain": "slack.com",
  "trust_score": 90,
  "data_retention": "90 days",
  "trains_on_input": false,
  "soc2_certified": true,
  "hipaa_compliant": true,
  "gdpr_compliant": true,
  "iso_27001": false,
  "breach_mentions": false,
  "processing_time_ms": 3200
}
```

### `GET /health`

Returns service health and configuration status.

## Scoring

| Signal                       | Points  |
|------------------------------|---------|
| SOC 2 certified              | +15     |
| GDPR compliant               | +15     |
| HIPAA compliant              | +10     |
| ISO 27001 certified          | +10     |
| Does not train on user input | +10     |
| Breach incidents found       | −20     |
| Baseline                     | 50      |



## How scoring works

Every domain starts at a baseline of 50.

The scraper fetches the domain's privacy, security, and compliance pages.
An LLM reads the raw text and extracts signals — not a database lookup,
just reading what the vendor actually published.

Points are added or removed based on what's found:
- Compliance certs (SOC2, GDPR, HIPAA, ISO 27001) add trust
- Not training on user input adds trust
- Any mention of a data breach removes trust

Score is clamped between 0 and 100.

A score of 60 with everything unknown means the vendor's public pages
don't mention compliance at all — which is itself a signal.

