from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "eka_requests_total",
    "Total HTTP requests",
    ["endpoint"]
)

CHAT_LATENCY = Histogram(
    "eka_chat_latency_seconds",
    "Latency of chat endpoint"
)

UPLOAD_COUNT = Counter(
    "eka_uploads_total",
    "Total documents uploaded"
)
