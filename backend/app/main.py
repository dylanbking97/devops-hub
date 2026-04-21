import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

from .routes import topics, session

app = FastAPI(title="DevOps Learning Hub", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus ───────────────────────────────────────────────────────────────
# Auto-instrument all routes and expose /metrics for Prometheus to scrape
Instrumentator().instrument(app).expose(app)

# ── OpenTelemetry Tracing ────────────────────────────────────────────────────
# service.name tags every span with "backend" in Jaeger so you can filter by service
resource = Resource.create({"service.name": "backend"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318/v1/traces"),
        )
    )
)
trace.set_tracer_provider(provider)

# Auto-instrument FastAPI (HTTP spans) and Redis (command spans)
FastAPIInstrumentor.instrument_app(app)
RedisInstrumentor().instrument()

app.include_router(topics.router, prefix="/api/topics", tags=["topics"])
app.include_router(session.router, prefix="/api/session", tags=["session"])


@app.get("/health")
def health():
    return {"status": "ok"}
