# URL Shortener (Learning Project)

This repository contains a minimal but scalable-by-design URL shortener implementation plan and starter assets focused on **system design**, **data modeling**, and **architecture**.

## What you'll learn

- How to design APIs for URL shortening and redirects.
- How to model relational data for links and click analytics.
- How to reason about read/write paths and bottlenecks.
- How to evolve from a single-node MVP to a distributed system.

## Core product requirements

1. Create a short URL from a long URL.
2. Resolve short URL to original URL using HTTP redirect.
3. Optional custom alias.
4. Optional expiration time.
5. Track click counts.
6. Keep redirects fast and highly available.

## Suggested architecture (MVP)

- **API service**: handles create requests and admin read APIs.
- **Redirect service**: handles `GET /{code}` and returns `301` or `302`.
- **PostgreSQL**: source of truth for link metadata.
- **Redis cache**: hot key cache for `code -> long_url`.

See [docs/system-design.md](docs/system-design.md) for full details.

## API sketch

### Create short URL

`POST /api/v1/shorten`

```json
{
  "url": "https://example.com/very/long/path",
  "custom_alias": "optional",
  "expires_at": "2026-12-31T00:00:00Z"
}
```

Response:

```json
{
  "id": "01HT...",
  "short_code": "aZ91kL",
  "short_url": "https://sho.rt/aZ91kL",
  "long_url": "https://example.com/very/long/path",
  "expires_at": "2026-12-31T00:00:00Z"
}
```

### Redirect

`GET /{short_code}` -> `302 Location: <long_url>`

### Link stats

`GET /api/v1/links/{short_code}/stats`

## Data model quick view

- `links`: canonical mapping from short code to destination URL.
- `click_events`: optional event table for analytics.

Reference SQL schema: [schema.sql](schema.sql).

## How to evolve this design

1. **MVP**: single DB + cache + one app service.
2. **Scale reads**: separate redirect service and use CDN edge caching.
3. **Scale writes**: queue-based analytics ingestion.
4. **High scale**: sharded storage and code-generation service.

## Next steps for implementation

1. Choose backend stack (Node.js/FastAPI/Go).
2. Implement API + redirect endpoints.
3. Add cache-aside logic for redirect path.
4. Add rate limiting and abuse checks.
5. Add metrics dashboard (p50/p95 redirect latency, cache hit ratio).
