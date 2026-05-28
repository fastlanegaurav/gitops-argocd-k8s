"""
GitOps Backend Microservice — Flask API
Author: Gaurav Kumar (github.com/fastlanegaurav)
"""

import os
import time
import logging
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

# ── OpenTelemetry tracing ──────────────────────────────────────────
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# ── Prometheus metrics ─────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "backend_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "backend_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

# ── Flask app ──────────────────────────────────────────────────────
app = Flask(__name__)
START_TIME = time.time()


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def record_metrics(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    return response


@app.route("/health")
def health():
    """Kubernetes liveness probe endpoint"""
    return jsonify({"status": "healthy", "service": "backend"}), 200


@app.route("/ready")
def ready():
    """Kubernetes readiness probe endpoint"""
    return jsonify({"status": "ready", "service": "backend"}), 200


@app.route("/metrics")
def metrics():
    """Prometheus scrape endpoint"""
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/api/v1/info")
def info():
    """Service info"""
    with tracer.start_as_current_span("get_info"):
        return jsonify({
            "service": "backend",
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "environment": os.getenv("APP_ENV", "development"),
            "uptime_seconds": round(time.time() - START_TIME, 2),
            "gitops": {
                "managed_by": "ArgoCD",
                "pattern": "App-of-Apps",
                "repo": "github.com/fastlanegaurav/gitops-argocd-k8s"
            }
        }), 200


@app.route("/api/v1/items", methods=["GET"])
def get_items():
    """Sample CRUD endpoint"""
    with tracer.start_as_current_span("get_items"):
        logger.info("Fetching items list")
        items = [
            {"id": 1, "name": "Item Alpha", "status": "active"},
            {"id": 2, "name": "Item Beta",  "status": "active"},
            {"id": 3, "name": "Item Gamma", "status": "inactive"},
        ]
        return jsonify({"items": items, "count": len(items)}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "endpoint not found", "status": 404}), 404


@app.errorhandler(500)
def server_error(e):
    logger.error("Internal server error: %s", str(e))
    return jsonify({"error": "internal server error", "status": 500}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("APP_ENV", "development") == "development"
    logger.info("Starting backend service on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
