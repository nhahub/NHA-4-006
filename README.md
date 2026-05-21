# Containerized URL Shortener Webservice 🚀

A full-stack URL shortener webservice built with Python (Flask) and SQLite, fully containerized using Docker, and instrumented with Prometheus, Grafana, and Alertmanager for real-time monitoring, visualization, and alerting.

## 🏗️ Architecture

The application is deployed using `docker compose` and consists of four services:

| Service | Image | Port | Description |
|---------|-------|------|-------------|
| **URL Shortener** | Custom (Flask) | `5000` | REST API for shortening URLs and redirecting |
| **Prometheus** | `prom/prometheus:v3` | `9090` | Time-series database that scrapes application metrics |
| **Alertmanager** | `prom/alertmanager:v0.32.1` | `9093` | Handles alerts from Prometheus and sends email notifications |
| **Grafana** | `grafana/grafana:13.0.1-security-01` | `3000` | Dashboard visualization for monitoring metrics |

---

## 🚀 How to Run

### Prerequisites
- Docker and Docker Compose installed

### Start the stack

```bash
docker compose up -d --build
```

This will build the application image and start all four services.

### Stop the stack

```bash
docker compose down        # keeps data (volumes persist)
docker compose down -v     # full reset (deletes all volumes and data)
```

---

## 📚 API Documentation

### 1. Health Check

- **Endpoint:** `/`
- **Method:** `GET`
- **Description:** Confirms the server is alive.
- **Response (200 OK):**
  ```
  Server is running
  ```

### 2. Shorten a URL

- **Endpoint:** `/shorten`
- **Method:** `POST`
- **Content-Type:** `application/json`
- **Request Body:**
  ```json
  {
    "url": "https://www.example.com"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "short_url": "http://localhost:5000/7vplvZ"
  }
  ```
- **Example:**
  ```bash
  curl -X POST http://localhost:5000/shorten \
    -H "Content-Type: application/json" \
    -d '{"url": "https://www.google.com"}'
  ```

### 3. Redirect to Original URL

- **Endpoint:** `/<short_code>`
- **Method:** `GET`
- **Description:** Looks up the short code and redirects to the original URL via a `302 Found` HTTP status.
- **Example:**
  ```bash
  curl -L http://localhost:5000/7vplvZ
  ```

### 4. Prometheus Metrics

- **Endpoint:** `/metrics`
- **Method:** `GET`
- **Description:** Exposes application metrics in Prometheus exposition format for scraping.

### Error Responses

| Status Code | Condition | Response Body |
|-------------|-----------|---------------|
| `400` | Missing `url` field | `{"error": "Missing 'url' field"}` |
| `400` | Invalid URL scheme | `{"error": "URL must start with http:// or https://"}` |
| `400` | Missing domain | `{"error": "URL is missing a domain (e.g. example.com)"}` |
| `404` | Unknown short code | `{"error": "Short URL not found"}` |

---

## 📊 Observability & Monitoring

The project features a fully configured monitoring stack. The URL Shortener exposes custom metrics at `/metrics` which are scraped by Prometheus every 5 seconds.

### Exposed Metrics (Prometheus)

| Metric | Type | Description |
|--------|------|-------------|
| `urls_shortened_total` | Counter | Total number of URLs successfully shortened |
| `redirects_total` | Counter | Total number of successful redirects |
| `failed_lookups_total` | Counter | Total number of 404 errors |
| `request_latency_seconds` | Histogram | Request latency for `shorten` and `redirect` operations |

### Grafana Dashboard

Grafana has been fully integrated and automated using **Provisioning**. No manual setup is required!

- **Data Source Provisioning:** Grafana automatically connects to Prometheus.
- **Dashboard Provisioning:** A custom dashboard titled **"URL Shortener Overview"** is automatically loaded.

**The dashboard includes the following visualizations:**

1. **Total Shortened Links:** A single stat showing the total count of shortened links.
2. **Rate of URL Creations & Redirections:** A time-series graph showing operations over time.
3. **95th Percentile Request Latency:** A real-time graph of the P95 latency categorized by operation.
4. **Rate of 404 Errors:** A graph tracking bad requests and failed lookups.

---

## 🚨 Alerting

Alerting is configured using **Prometheus alerting rules** (`rules.yml`) and **Alertmanager** for email notifications via Gmail.

### Configured Alert Rules

| Alert | Expression | Threshold | For | Severity |
|-------|-----------|-----------|-----|----------|
| **High404ErrorRate** | `rate(failed_lookups_total[5m])` | > 0.1 req/s (~6/min) | 2 min | ⚠️ Warning |
| **HighRequestLatency** | `rate(request_latency_seconds_sum[5m]) / rate(request_latency_seconds_count[5m])` | > 500ms | 2 min | 🔴 Critical |

### Alert Flow

```
Flask App → Prometheus (evaluates rules) → Alertmanager (sends email) → Gmail inbox
```

- View alert states at: `http://localhost:9090/alerts`
- View Alertmanager at: `http://localhost:9093`

---

## 💾 Data Persistence

All stateful data is persisted using Docker named volumes, ensuring nothing is lost on restart.

| Volume | Service | Container Path | Purpose |
|--------|---------|----------------|---------|
| `db_shortener_url` | URL Shortener | `/opt/app/data` | SQLite database containing all shortened URLs |
| `prometheus_data` | Prometheus | `/prometheus` | Time-series metrics data (TSDB) |
| `grafana_data` | Grafana | `/var/lib/grafana` | Internal database (users, dashboard state, settings) |

Data survives `docker compose down` and `docker compose up` cycles.
To perform a **full reset**, use `docker compose down -v` to remove all volumes.

---

## 📁 Project Structure

```
URL_Shortener_v1/
├── app.py                          # Flask application with API endpoints and metrics
├── Dockerfile                      # Container image definition
├── docker-compose.yml              # Multi-service orchestration with persistent volumes
├── prometheus.yml                  # Prometheus scrape configuration and alerting target
├── rules.yml                       # Prometheus alerting rules
├── alertmanager.yml                # Alertmanager configuration (Gmail SMTP)
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
└── grafana/
    ├── dashboards/
    │   └── url_shortener.json      # Provisioned Grafana dashboard
    └── provisioning/
        ├── dashboards/
        │   └── dashboards.yml      # Dashboard provisioning config
        └── datasources/
            └── prometheus.yml      # Datasource provisioning config
```

---

## 🔐 Accessing the Services

| Service | URL |
|---------|-----|
| **URL Shortener API** | `http://localhost:5000` |
| **Prometheus UI** | `http://localhost:9090` |
| **Alertmanager UI** | `http://localhost:9093` |
| **Grafana UI** | `http://localhost:3000` |

### Grafana Credentials:
- **Username:** `admin`
- **Password:** `4kadmin`
