from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from .models import OasisAction, OasisDomain, OasisEvent, Reversibility, WorldState


def canonical_json(value: Any) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def state_hash(state: WorldState) -> str:
    return hashlib.sha256(canonical_json(state).encode()).hexdigest()


def event_hash(event: OasisEvent) -> str:
    return hashlib.sha256(canonical_json(event).encode()).hexdigest()


def apply_event(state: WorldState, event: OasisEvent) -> tuple[WorldState, Reversibility, OasisEvent | None, OasisEvent | None, list[str]]:
    s = state.model_copy(deep=True)
    notes: list[str] = []
    inverse = None
    compensation = None
    q = event.quantity or 1

    if event.event_id in s.seen_event_ids:
        notes.append("duplicate event ignored: exactly-once guard")
        return s, Reversibility.EXACT, None, None, notes

    if event.domain == OasisDomain.AVATAR and event.action in {OasisAction.START, OasisAction.UPDATE}:
        before = s.avatar_id
        s.avatar_id = event.avatar_id
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "avatar_id": before, "entity_id": before, "action": OasisAction.UPDATE})
        rev = Reversibility.EXACT
    elif event.domain == OasisDomain.INVENTORY and event.action == OasisAction.ADD:
        s.inventory[event.entity_id] = s.inventory.get(event.entity_id, 0) + q
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "action": OasisAction.USE, "quantity": q})
        rev = Reversibility.EXACT
    elif event.domain == OasisDomain.INVENTORY and event.action == OasisAction.USE:
        before = s.inventory.get(event.entity_id, 0)
        if before < q:
            notes.append(f"insufficient inventory: have {before}, need {q}")
            rev = Reversibility.NONREVERSIBLE
        else:
            left = before - q
            if left:
                s.inventory[event.entity_id] = left
            else:
                s.inventory.pop(event.entity_id, None)
            inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "action": OasisAction.ADD, "quantity": q})
            rev = Reversibility.EXACT
    elif event.domain == OasisDomain.INVENTORY and event.action == OasisAction.TRANSFER:
        before = s.inventory.get(event.entity_id, 0)
        if before < q:
            notes.append("transfer rejected: insufficient quantity")
            rev = Reversibility.NONREVERSIBLE
        else:
            s.inventory[event.entity_id] = before - q
            compensation = event.model_copy(update={"event_id": f"compensate:{event.event_id}", "action": OasisAction.COMPENSATE, "payload": {**event.payload, "reason": "return transfer"}})
            rev = Reversibility.COMPENSATING
    elif event.domain == OasisDomain.QUEST and event.action == OasisAction.START:
        s.quests[event.entity_id] = {"status": "in_progress", "objectives": {}, **event.payload}
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "action": OasisAction.COMPENSATE, "payload": {"delete_quest": True}})
        rev = Reversibility.EXACT
    elif event.domain == OasisDomain.QUEST and event.action == OasisAction.UPDATE:
        quest_id = str(event.payload.get("quest_id", event.entity_id))
        objective_id = str(event.payload.get("objective_id", event.entity_id))
        quest = s.quests.setdefault(quest_id, {"status": "in_progress", "objectives": {}})
        old = copy.deepcopy(quest.get("objectives", {}).get(objective_id))
        quest.setdefault("objectives", {})[objective_id] = {"complete": bool(event.payload.get("complete", True)), "game_source": event.game_source}
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "payload": {**event.payload, "complete": bool(old and old.get("complete"))}})
        rev = Reversibility.EXACT
    elif event.domain == OasisDomain.QUEST and event.action == OasisAction.COMPLETE:
        quest = s.quests.setdefault(event.entity_id, {"objectives": {}})
        old = quest.get("status", "not_started")
        quest["status"] = "completed"
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "action": OasisAction.UPDATE, "payload": {"status": old}})
        rev = Reversibility.EXACT
    elif event.domain == OasisDomain.KARMA and event.action in {OasisAction.ADD, OasisAction.USE}:
        delta = q if event.action == OasisAction.ADD else -q
        if s.karma + delta < 0:
            notes.append("karma debit rejected: negative result")
            rev = Reversibility.NONREVERSIBLE
        else:
            s.karma += delta
            inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "action": OasisAction.USE if delta > 0 else OasisAction.ADD, "quantity": q})
            rev = Reversibility.EXACT
    elif event.domain == OasisDomain.GEO and event.action in {OasisAction.START, OasisAction.UPDATE, OasisAction.COMPLETE}:
        previous = copy.deepcopy(s.last_location)
        s.last_location = event.location or event.payload.get("location")
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "action": OasisAction.UPDATE, "location": previous})
        rev = Reversibility.EXACT
    elif event.domain == OasisDomain.PROVIDER and event.action in {OasisAction.UPDATE, OasisAction.TRANSFER}:
        route_key = str(event.payload.get("route_key", event.entity_id))
        old = s.provider_routes.get(route_key)
        target = event.provider or str(event.payload.get("provider", "unknown"))
        s.provider_routes[route_key] = target
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "provider": old, "action": OasisAction.UPDATE}) if old else None
        rev = Reversibility.EXACT if old else Reversibility.COMPENSATING
    elif event.domain == OasisDomain.AGENT and event.action in {OasisAction.UPDATE, OasisAction.ADD}:
        key = event.entity_id
        old = copy.deepcopy(s.agent_memory.get(key))
        s.agent_memory[key] = event.payload.get("value", event.payload)
        inverse = event.model_copy(update={"event_id": f"inverse:{event.event_id}", "payload": {"value": old}, "action": OasisAction.UPDATE})
        rev = Reversibility.EXACT
    elif event.action == OasisAction.COMPENSATE:
        if event.domain == OasisDomain.QUEST and event.payload.get("delete_quest"):
            s.quests.pop(event.entity_id, None)
        rev = Reversibility.COMPENSATING
    else:
        notes.append("event recorded but no domain reducer is registered")
        rev = Reversibility.NONREVERSIBLE

    s.seen_event_ids.append(event.event_id)
    return s, rev, inverse, compensation, notes
