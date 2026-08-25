"""
DIAZAI model adapter registry v0.6.

The runtime operates on a model-agnostic RouterEvent contract. Profiles
describe model structure; extractors remain model/runtime-specific.

Public reference profiles:
- openai/gpt-oss-20b
- Qwen/Qwen3-30B-A3B
- mistralai/Mixtral-8x7B-Instruct-v0.1
- allenai/OLMoE-1B-7B-0125-Instruct

A profile does NOT grant access to model internals. The corresponding runtime
adapter must expose router/expert events.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import math

@dataclass(frozen=True, slots=True)
class MoeProfile:
    name: str
    family: str
    layers: int
    experts: int
    top_k: int
    context_length: Optional[int]
    hidden_size: Optional[int]=None
    q_heads: Optional[int]=None
    kv_heads: Optional[int]=None
    license_hint: Optional[str]=None
    runtime_hints: tuple[str,...]=()

PROFILES = {
    "gpt-oss-20b": MoeProfile("openai/gpt-oss-20b","gpt_oss",24,32,4,131072,2880,64,8,"apache-2.0",("transformers","vllm","sglang")),
    "qwen3-30b-a3b": MoeProfile("Qwen/Qwen3-30B-A3B","qwen3_moe",48,128,8,40960,2048,32,4,"apache-2.0",("transformers","vllm")),
    "mixtral-8x7b": MoeProfile("mistralai/Mixtral-8x7B-Instruct-v0.1","mixtral",32,8,2,32768,4096,32,8,"apache-2.0",("transformers","vllm")),
    "olmoe-1b-7b": MoeProfile("allenai/OLMoE-1B-7B-0125-Instruct","olmoe",16,64,8,4096,2048,16,16,"apache-2.0",("transformers","vllm")),
}

def get_profile(name_or_alias:str)->MoeProfile:
    k=name_or_alias.lower()
    if k in PROFILES: return PROFILES[k]
    for p in PROFILES.values():
        if p.name.lower()==k: return p
    raise KeyError(name_or_alias)

def validate_router_event(profile:MoeProfile,event:dict)->None:
    layer=int(event["layer"])
    ids=list(event["expert_ids"]); weights=list(event["expert_weights"])
    if not 0 <= layer < profile.layers: raise ValueError("layer")
    if len(ids)!=profile.top_k or len(weights)!=profile.top_k: raise ValueError("top_k")
    if any(int(x)<0 or int(x)>=profile.experts for x in ids): raise ValueError("expert id")
    if any(not math.isfinite(float(w)) for w in weights): raise ValueError("weight")
