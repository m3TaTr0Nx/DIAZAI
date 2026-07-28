from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Literal
from pydantic import BaseModel, Field, model_validator


class OasisDomain(StrEnum):
    AVATAR = "avatar"
    INVENTORY = "inventory"
    QUEST = "quest"
    KARMA = "karma"
    GEO = "geo"
    NFT = "nft"
    PROVIDER = "provider"
    AGENT = "agent"
    SYSTEM = "system"


class OasisAction(StrEnum):
    START = "start"
    READ = "read"
    UPDATE = "update"
    COMPLETE = "complete"
    ADD = "add"
    USE = "use"
    TRANSFER = "transfer"
    COMPENSATE = "compensate"
    VERIFY = "verify"


class Reversibility(StrEnum):
    EXACT = "exact"
    COMPENSATING = "compensating"
    NONREVERSIBLE = "nonreversible"


class OasisEvent(BaseModel):
    event_id: str
    event_type: str
    domain: OasisDomain
    action: OasisAction
    avatar_id: str = "anonymous"
    entity_id: str
    game_source: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quantity: int | None = None
    provider: str | None = None
    location: dict[str, float] | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_quantity(self):
        if self.quantity is not None and self.quantity < 0:
            raise ValueError("quantity must be non-negative")
        return self


class AtlasAddress(BaseModel):
    codec_version: str = "oasis-event-729.v1"
    i: int
    j: int
    k: int
    scalar: int
    index729: int
    trits6: list[int]
    row27: int
    col27: int
    bank: str


class TransitionReceipt(BaseModel):
    sequence: int
    event: OasisEvent
    address: AtlasAddress
    before_hash: str
    after_hash: str
    event_hash: str
    previous_receipt_hash: str
    receipt_hash: str
    reversibility: Reversibility
    inverse_event: OasisEvent | None = None
    compensation_event: OasisEvent | None = None
    applied: bool = True
    notes: list[str] = Field(default_factory=list)


class WorldState(BaseModel):
    avatar_id: str = "anonymous"
    inventory: dict[str, int] = Field(default_factory=dict)
    quests: dict[str, dict[str, Any]] = Field(default_factory=dict)
    karma: int = 0
    last_location: dict[str, float] | None = None
    provider_routes: dict[str, str] = Field(default_factory=dict)
    agent_memory: dict[str, Any] = Field(default_factory=dict)
    seen_event_ids: list[str] = Field(default_factory=list)


class DivergenceResult(BaseModel):
    equal: bool
    first_sequence: int | None = None
    reason: str | None = None
    left_event_id: str | None = None
    right_event_id: str | None = None
    left_after_hash: str | None = None
    right_after_hash: str | None = None


class ProviderRunResult(BaseModel):
    provider: str
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    latency_ms: float


class ConformanceResult(BaseModel):
    contract_id: str
    equivalent: bool
    left: ProviderRunResult
    right: ProviderRunResult
    differences: list[str] = Field(default_factory=list)


class CanonEntry(BaseModel):
    key: str
    revision: int = 1
    status: Literal["PROPOSED", "VERIFIED", "SUPERSEDED", "REJECTED"] = "PROPOSED"
    title: str
    statement: str
    evidence: list[str] = Field(default_factory=list)
    supersedes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
