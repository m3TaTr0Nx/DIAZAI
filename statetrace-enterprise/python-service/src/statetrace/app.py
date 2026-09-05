from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel

from .conformance import compare
from .evidence import build_evidence_bundle
from .fixtures import synthetic_trace
from .ledger import Ledger
from .models import ConformanceRequest, DivergenceRequest, EventEnvelope, EvidenceRequest
from .replay import first_divergence, replay

class SyntheticRequest(BaseModel):
    trace_id: str
    count: int = 100
    mutation_at: int | None = None

class BatchRequest(BaseModel):
    events: list[EventEnvelope]

DB_PATH = os.getenv("STATETRACE_DB", ":memory:")
ledger = Ledger(DB_PATH)
app = FastAPI(title="DIAZAI StateTrace Enterprise", version="1.0.0")
origins = [x.strip() for x in os.getenv("STATETRACE_CORS_ORIGINS", "http://127.0.0.1:8080,http://localhost:8080").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health(): return {"status":"ok","service":"statetrace-python","version":"1.0.0","db":DB_PATH}

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    ids=ledger.trace_ids(); return f"statetrace_traces {len(ids)}\nstatetrace_events {sum(len(ledger.trace(t)) for t in ids)}\n"

@app.post("/v1/events")
def ingest_event(event: EventEnvelope):
    accepted,receipt=ledger.ingest(event); return {"accepted":accepted,"duplicate":not accepted,"receipt":receipt}

@app.post("/v1/events/batch")
def ingest_batch(request: BatchRequest):
    existing={event.event_id for event in request.events if ledger.has_event(event.event_id)}
    receipts=ledger.ingest_many(request.events)
    duplicates=sum(1 for event in request.events if event.event_id in existing)
    return {"accepted":len(request.events)-duplicates,"duplicates":duplicates,"receipts":receipts}

@app.post("/v1/scenarios/synthetic")
def create_synthetic(request: SyntheticRequest):
    receipts=ledger.ingest_many(synthetic_trace(request.trace_id,request.count,request.mutation_at))
    return {"trace_id":request.trace_id,"count":len(receipts),"head_hash":receipts[-1]["receipt_hash"] if receipts else None}

@app.get("/v1/traces")
def list_traces(): return {"traces":ledger.trace_ids()}

@app.get("/v1/traces/{trace_id}")
def get_trace(trace_id: str):
    trace=ledger.trace(trace_id)
    if not trace: raise HTTPException(404,"trace not found")
    return {"trace_id":trace_id,"items":trace,"verification":ledger.verify(trace_id)}

@app.get("/v1/traces/{trace_id}/replay")
def replay_trace(trace_id: str):
    trace=ledger.trace(trace_id)
    if not trace: raise HTTPException(404,"trace not found")
    return replay(trace)

@app.get("/v1/traces/{trace_id}/verify")
def verify_trace(trace_id: str): return ledger.verify(trace_id)

@app.post("/v1/divergence")
def divergence(request: DivergenceRequest):
    left,right=ledger.trace(request.left_trace_id),ledger.trace(request.right_trace_id)
    if not left or not right: raise HTTPException(404,"both traces must exist")
    return first_divergence(left,right)

@app.post("/v1/conformance")
def conformance(request: ConformanceRequest): return compare(request.left,request.right,request.ignored_paths)

@app.post("/v1/evidence")
def evidence(request: EvidenceRequest):
    if not ledger.trace(request.trace_id): raise HTTPException(404,"trace not found")
    return build_evidence_bundle(ledger,request.trace_id,request.include_events)

@app.delete("/v1/admin/reset")
def reset():
    if os.getenv("STATETRACE_ENABLE_ADMIN_RESET","false").lower()!="true": raise HTTPException(403,"admin reset disabled")
    ledger.clear(); return {"cleared":True}

@app.get("/", response_class=HTMLResponse)
def root():
    for path in [Path(__file__).resolve().parents[3]/"web-console"/"index.html",Path("/app/web-console/index.html")]:
        if path.exists(): return path.read_text(encoding="utf-8")
    return "<h1>DIAZAI StateTrace</h1><p>Open <a href='/docs'>/docs</a>.</p>"
