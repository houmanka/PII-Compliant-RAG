# Complaint Ingestion Pipeline

A bank drops 50,000 customer complaint reports into a cloud bucket every night.
This pipeline processes them durably with PII redaction, ML classification, and vector embeddings — using Temporal as the orchestration backbone.

---

## Status

| Component | Status |
|---|---|
| Pub/Sub listener | Done |
| Temporal event handler (standalone activity) | Done |
| Complaint ingestion activity (streaming, PII, classify, persist) | Done |
| Postgres storage provider | Done |
| Cloud storage provider | Done |
| Embedding provider (AllMiniLM) | Done |
| Cache provider (Redis + ABC contract) | Done |
| Embedding activity (fetch → embed → push to Pinecone) | In progress |
| Pinecone provider | In progress |

---

## How It Works

```
                        ┌─────────────────────────────────────────────────────────┐
                        │                    INFRASTRUCTURE                        │
                        │   Pub/Sub Emulator · Postgres · Redis · Temporal Server  │
                        └─────────────────────────────────────────────────────────┘

Cloud Bucket
(CSV dropped)
     │
     │  ObjectCreated event
     ▼
┌──────────────┐
│  Google      │
│  Pub/Sub     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ subscriber   │  Pulls Pub/Sub messages
│ .py          │
└──────┬───────┘
       │  FileInput { provider, path, event_type }
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Temporal Worker                                                     │
│                                                                      │
│  ┌─────────────────────┐                                            │
│  │ ingestion_handler   │  Standalone Activity — starts the workflow │
│  │ (Activity)          │  via Temporal client                       │
│  └──────────┬──────────┘                                            │
│             │                                                        │
│             ▼                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  ComplaintWorkflow                                           │   │
│  │                                                              │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │  ingest_file_activity                                  │  │   │
│  │  │                                                        │  │   │
│  │  │  for each row in CSV (streamed, not loaded in memory): │  │   │
│  │  │    1. skip if case_id already in Postgres (idempotent) │  │   │
│  │  │    2. PII scan + redact  ◄── MCP tool (HTTP)          │  │   │
│  │  │    3. classify           ◄── ML model (joblib)        │  │   │
│  │  │    4. persist to Postgres                              │  │   │
│  │  │                                                        │  │   │
│  │  │  returns: file_id                                      │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  │                                                              │   │
│  │  ┌────────────────────────────────────────────────────────┐  │   │
│  │  │  embedding_activity                    [IN PROGRESS]   │  │   │
│  │  │                                                        │  │   │
│  │  │  1. fetch complaints where embedded = false (Postgres) │  │   │
│  │  │  2. embed redacted text  ◄── AllMiniLM                │  │   │
│  │  │  3. push vectors         ──► Pinecone                 │  │   │
│  │  │  4. mark embedded = true                               │  │   │
│  │  └────────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

                    ┌──────────┐     ┌──────────┐     ┌──────────┐
                    │ Postgres │     │  Redis   │     │ Pinecone │
                    │          │     │  Cache   │     │ (vector) │
                    └──────────┘     └──────────┘     └──────────┘
```

---

## Provider Architecture

Each integration is built as a **swappable provider** — a contract defines the interface, a registry handles construction, and the worker only ever calls `build_*`. Swapping backends (e.g. Redis → Memcached) means changing one enum value in config.

```
providers/
  cloud_storage/          Protocol-based contract
    contract.py           CloudStorage protocol
    registry.py           CloudStorageKind enum + build_cloud_storage()
    local_cloud.py        Local filesystem implementation

  storage/                Protocol-based contract
    contract.py           DataStore protocol (complaints, files, classifications)
    registry.py           DataStorageKind enum + build_data_store()
    postgres.py           SQLAlchemy + Postgres implementation

  embeddings/             Protocol-based contract
    contracts.py          EmbeddingProvider protocol
    registry.py           EmbeddingProviderKind enum + build_embedding_provider()
    all_mini_lm.py        sentence-transformers AllMiniLM implementation

  cache_provider/         ABC-based contract (strict — unimplemented methods raise at instantiation)
    contract.py           CacheProvider ABC (create, exists, fetch, update, delete)
    registry.py           CacheProviderKind enum + build_cache_provider()
    redis.py              Redis implementation
```

**Why ABC for cache?** The other providers use Python `Protocol` (structural typing — satisfies by shape). The cache provider uses `ABC` (nominal typing — must inherit and implement all abstract methods). This enforces the contract at instantiation time rather than relying on static analysis alone, which suits a provider where partial implementation would silently fail at runtime.

---

## Data Model

```
files
  id            PK
  path
  created_at
  archived_at

complaints
  id                PK
  case_id           unique — idempotency key from source CSV
  text_redacted     raw text is never stored; only the redacted version
  embedded          bool — true once pushed to Pinecone; prevents re-embedding on retry
  classification_id FK → classifications
  file_id           FK → files
  created_at
  updated_at

classifications
  id    PK
  name  e.g. "billing", "service", "account"
```

---

## Tech Stack

| Concern | Technology |
|---|---|
| Orchestration | [Temporal](https://temporal.io/) |
| Messaging | Google Pub/Sub |
| Storage | Postgres (SQLAlchemy + Alembic) |
| Cache | Redis |
| Embeddings | sentence-transformers AllMiniLM |
| Vector DB | Pinecone *(in progress)* |
| PII scanning | MCP tool (fastmcp, HTTP) |
| ML classification | scikit-learn (joblib pipeline) |
| Config | pydantic-settings |
| Runtime | Python 3.13, uv |

---

## Local Development

### Prerequisites

- Docker
- [uv](https://docs.astral.sh/uv/)
- Temporal dev server: `temporal server start-dev`
  - requires `temporal version 1.7.0 (Server 1.31.0, UI 2.49.1)` for standalone activity support

### Environment

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql://app_user:change_me@localhost:5432/complaint_store
PUBSUB_EMULATOR_HOST=localhost:8085
GOOGLE_CLOUD_PROJECT=local
MCP_PATH=http://127.0.0.1:8090/mcp
EMBEDDING_ENGINE=all-MiniLM-L6-v2
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Start infrastructure

```bash
docker compose up -d
```

This starts Postgres, Redis, and the Pub/Sub emulator.

### Run database migrations

```bash
uv run alembic upgrade head
```

### One-time Pub/Sub setup

```bash
export PUBSUB_EMULATOR_HOST=localhost:8085
export GOOGLE_CLOUD_PROJECT=local

uv run python ./localdev/pubsub_emulator_tools.py create-topic --topic object-created
uv run python ./localdev/pubsub_emulator_tools.py create-sub --topic object-created --subscription object-created-sub
```

### Start the MCP PII server

```bash
cd ./localdev/mcp/mcp_pii_server
source .venv/bin/activate
fastmcp run pii_classify.py:mcp --transport http --host 127.0.0.1 --port 8090
```

### Start the worker and subscriber

```bash
uv run python worker/worker.py
uv run python subscriber.py
```

### Publish a test event

Copy a CSV into `data/inbox/`, then:

```bash
export PUBSUB_EMULATOR_HOST=localhost:8085
export GOOGLE_CLOUD_PROJECT=local

uv run python ./localdev/pubsub_emulator_tools.py publish \
  --topic object-created \
  --json '{"provider":"local","path":"data/inbox/support.csv","eventType":"ObjectCreated"}'
```

### Verify the event

```bash
uv run python ./localdev/pubsub_subscriber.py --subscription object-created-sub
```
