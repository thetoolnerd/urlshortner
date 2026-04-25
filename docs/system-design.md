# System Design Notes: URL Shortener

## 1) Functional requirements

- Shorten long URLs.
- Redirect quickly from short code to long URL.
- Support custom aliases.
- Support expiration.
- Provide basic stats.

## 2) Non-functional requirements

- Low latency redirects (target p95 < 50ms at service tier).
- High read throughput (redirects dominate writes).
- Reasonable durability for mappings.
- Basic abuse prevention.

## 3) Capacity planning (example assumptions)

- 10 million new URLs/month.
- 100 million redirects/day.
- Average short code length: 7 chars base62.

Rough base62 keyspace:

- `62^7 ~= 3.5 trillion` possible keys.

## 4) APIs

### 4.1 Create short URL

- `POST /api/v1/shorten`
- Validates URL format and policy constraints.
- If custom alias exists, enforce uniqueness.

### 4.2 Resolve short URL

- `GET /{code}`
- Reads mapping from cache first, DB fallback.
- Returns `301` for permanent or `302` for temporary redirects.

### 4.3 Stats

- `GET /api/v1/links/{code}/stats`
- Returns click count, created time, expiry info.

## 5) Data model

### 5.1 `links`

| Column | Type | Notes |
|---|---|---|
| id | UUID/ULID | Primary key |
| short_code | VARCHAR(16) | Unique, indexed |
| long_url | TEXT | Destination URL |
| created_at | TIMESTAMPTZ | Creation timestamp |
| expires_at | TIMESTAMPTZ NULL | Optional expiry |
| owner_id | UUID NULL | Optional multi-tenant ownership |
| is_custom | BOOLEAN | Whether alias is user-defined |

### 5.2 `click_events` (optional for analytics)

| Column | Type | Notes |
|---|---|---|
| id | BIGSERIAL | Primary key |
| short_code | VARCHAR(16) | Indexed |
| clicked_at | TIMESTAMPTZ | Event time |
| ip_hash | VARCHAR(128) | Privacy-preserving hash |
| user_agent | TEXT | Optional |
| referer | TEXT | Optional |

## 6) Code generation strategy

Options:

1. **Random base62 + collision check** (simple MVP).
2. **Hash(long_url + salt)** with truncation (deterministic-ish).
3. **Snowflake/sequence -> base62 encode** (good at scale).

Recommended for learning path:

- Start with random base62 + DB unique constraint.
- Retry on collision (rare at moderate scale).

## 7) Read/write paths

### Create path

1. Validate input.
2. Generate short code.
3. Insert into DB with unique constraint.
4. Populate cache.
5. Return short URL.

### Redirect path

1. Parse code.
2. Lookup Redis (`code -> long_url`).
3. On miss, query DB and warm cache.
4. Emit click event asynchronously (queue preferred).
5. Return redirect response.

## 8) Caching

- Use cache-aside strategy.
- TTL for non-expiring URLs can still exist (e.g., 1 day) to allow refresh.
- Negative caching for invalid/missing codes can reduce DB load.

## 9) Reliability and scaling

- DB: primary + read replica for analytics reads.
- Cache: Redis with persistence depending on SLA.
- App tier: stateless, horizontally scalable behind load balancer.
- Add message queue (Kafka/SQS/RabbitMQ) for click ingestion as traffic grows.

## 10) Security and abuse prevention

- URL validation and deny-listing for malicious domains.
- Per-IP/user/API-key rate limits.
- Optional malware/phishing scanning integration.
- Avoid open-redirect vulnerabilities by only redirecting stored URLs.

## 11) Observability

Track:

- Redirect latency (p50/p95/p99).
- Cache hit ratio.
- DB query latency and error rates.
- Create API success/error rates.
- Top missing/expired code lookups.

## 12) Trade-offs

- Strong consistency is usually required for create -> immediate redirect behavior.
- Analytics can be eventually consistent.
- Longer codes reduce collision probability but are less user-friendly.

## 13) Incremental roadmap

1. MVP with one service, Postgres, Redis.
2. Separate redirect service for independent scaling.
3. Async event pipeline for clicks.
4. Archival policy and partitioning for large `click_events` table.
5. Multi-region with geo-routing if global latency is a target.
