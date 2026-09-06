# TaskPulse v1.0

![Automated Continuous Integration](https://github.com/demmanuel58-spec/taskpulse/actions/workflows/test.yml/badge.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)
![Redis](https://img.shields.io/badge/Redis-7.0-dc382d.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0-336791.svg)

An enterprise-grade, distributed task queue and background execution engine built with Python, FastAPI, Redis, and PostgreSQL. Engineered to eliminate API latency, handle flaky operations with exponential backoff retries, and isolate failing payloads via a Dead-Letter Queue (DLQ).

---

## 🎯 Target Audience & Industry Use Cases

* **High-Throughput SaaS Platforms:** Engineering teams needing to offload bulk PDF generation, video/image transcoding, or batch notification dispatches without degrading web response times.
* **Fintech & Transactional Workflows:** Systems executing multi-step payment reconciliations, third-party webhook dispatches, and asynchronous database syncs requiring state tracking and retry guarantees.
* **DevOps & Infrastructure Teams:** Engineers managing distributed microservices who require self-healing, fault-tolerant background processing with Dead-Letter Queue containment.
* **Data Pipelines & ETL Routines:** Applications executing scheduled data ingestion, web scraping, and data transformation jobs where mutation logging and failure auditing are mandatory.

---

## ⚡ The Real-World Problem Solved

Executing long-running or resource-intensive tasks synchronously inside a single HTTP request cycle leads to severe API degradation:
1. **Dismal UX:** API endpoints hang, leading to client-side spinners and dropped connections.
2. **Server Exhaustion & Timeouts:** Web gateways (e.g., NGINX, Cloudflare) time out long requests (30–60s), causing partial writes and thread pool starvation.

### **The TaskPulse Solution**
**TaskPulse** decouples task dispatching from execution using an asynchronous Producer-Broker-Worker topology:
* **Sub-50ms Responses:** The FastAPI Producer enqueues task requests into Redis and immediately returns a `202 Accepted` status with a unique Task UUID.
* **Isolated Horizontal Scaling:** Background Python workers pull and execute jobs independently without impacting the primary web API.
* **Resilience & State Auditability:** Built-in exponential backoff retries handle transient errors automatically, while PostgreSQL persists real-time task states (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `DEAD_LETTER`).

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Producer (FastAPI)                   │
│   - Receives async task requests (e.g., PDF generation)│
│   - Generates Unique Task ID & pushes payload          │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Broker / Queue (Redis)                │
│   - In-Memory Task Queue (RPUSH / LPOP)                │
│   - Dead-Letter Queue (DLQ) for failed execution       │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Worker Pool (Python Concurrent)            │
│   - Consumes jobs asynchronously                       │
│   - Exponential Backoff & Retry Handling               │
│   - Updates Execution Status in DB                     │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Task State Store (PostgreSQL)              │
│   - Tracks status: PENDING | RUNNING | FAILED | DONE   │
└───────────────────────────┴────────────────────────────┘
```


## 🛡️ Core Engineering Features

* **Non-Blocking Dispatching:** Decoupled HTTP interface providing instant request processing and status polling endpoints.
* **Atomic Redis Message Queue:** High-throughput in-memory job distribution built on blocking pop (BLPOP) mechanics.
* **Exponential Backoff Retries:** Automated retry logic ($2^n$ second delays) to safely handle transient network and database failures.
* **Dead-Letter Queue (DLQ) Isolation:** Exhausted tasks exceeding max retry thresholds are safely routed to a dedicated DLQ and logged for diagnostics.
* **Relational State Persistence:** Full lifecycle tracking in PostgreSQL for real-time monitoring and compliance auditing.
* **Fully Containerized:** Docker Compose orchestration for single-command deployment across dev and production environments.


## 🚀 Quickstart & Local Setup

Prerequisites
*  Docker & Docker Compose installed


**1. Clone & Spin Up Containers**
```
git clone [https://github.com/demmanuel58-spec/taskpulse.git]
cd taskpulse

# Launch PostgreSQL, Redis, FastAPI Producer, and Workers
docker compose up --build
```

**2. Submit a Background Task**
```
curl -X 'POST' \
  'http://localhost:8000/tasks' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "task_type": "generate_pdf_report",
  "payload": {"report_id": "REP-9921", "format": "pdf"},
  "max_retries": 3
}'
```

**3. Monitor Task Status**
```
curl -X 'GET' 'http://localhost:8000/tasks/<YOUR_TASK_UUID>'
```

---

## 👤 Author

**David Emmanuel**  
Backend Software Engineer specializing in distributed systems, REST APIs, and database architecture.

* **GitHub:** [@demmanuel58-spec](https://github.com/demmanuel58-spec)
* **LinkedIn:** [David Emmanuel](https://linkedin.com)

---

## ⚠️ Disclaimer

* **Educational & Demonstration Purposes:** **TaskPulse** was implemented to showcase enterprise distributed system design patterns, worker concurrency, and fault tolerance mechanisms.
* **Production Deployment:** High-availability production deployments require setting up external secret management, broker clustering/sentinels, and SSL/TLS database connections.
* **No Warranty:** This software is provided "as-is" without warranty of any kind.







