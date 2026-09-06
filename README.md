# TaskPulse v1.0

![Automated Continuous Integration](https://github.com/demmanuel58-spec/taskpulse/actions/workflows/test.yml/badge.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)
![Redis](https://img.shields.io/badge/Redis-7.0-dc382d.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15.0-336791.svg)

An asynchronous background execution engine built to decouple long-running operations from web API threads. Designed to maintain sub-50ms API response times while processing background jobs with Redis message queues and PostgreSQL state persistence.

---

## ⚡ Asynchronous Lifecycle & State Machine

Every task submitted to TaskPulse moves through a strict relational state machine ensuring zero task loss and total auditability:

```
[HTTP POST /tasks] ──► PENDING (Postgres + Redis)
                           │
                           ▼
                        RUNNING (Worker Executing)
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
        COMPLETED                     FAILED
                                          │
                                 (Retry Count < Max)
                                          │
                                          ▼
                               Exponential Backoff (2^n)
                                          │
                                 (Max Retries Exceeded)
                                          │
                                          ▼
                                     DEAD_LETTER
```
---

## 📊 Queue Performance & Reliability Mechanics

* **Latency Elimination:**  Decouples task acceptance from execution to ensure web routes return 202 Accepted in under 50ms.
* **Fault Recovery Algorithm:**  Exponential backoff delays calculated dynamically (2^retry_count seconds) to allow downstream API recoveries during network flakiness.
* **Dead-Letter Containment:**  Unprocessable jobs are automatically isolated to a Redis DLQ and logged to PostgreSQL with complete call stack traces for debugging.
* **Relational State Persistence:**  Full lifecycle tracking in PostgreSQL for real-time monitoring and compliance auditing.


---


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







