"""
DIAZAI real-world routing algorithms v0.5.

These algorithms preserve logical model semantics. They route *physical work*:
expert replicas, KV blocks, queues, ranks, cache sources, or transport channels.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Optional
import hashlib, statistics

from .superplane_alu import U9,FAMS,SuperplaneState
from .superplane_moe import is_lambda_exchange
from .coprime_lanes import full_y_rows

SCOPES=("LOCAL_GPU","NODE","RACK","GLOBAL_CLUSTER")

def stable_u64(*parts)->int:
    h=hashlib.blake2b(digest_size=8,person=b"DIAZAI05")
    for p in parts:
        h.update(str(p).encode()); h.update(b"\0")
    return int.from_bytes(h.digest(),"little")

@dataclass(frozen=True,slots=True)
class RouteCandidate:
    candidate_id:str
    rank:int
    node:int=0
    scope:int=0
    cache_hit:float=0.0
    transfer_ms:float=0.0
    queue_ms:float=0.0
    thermal_pressure:float=0.0
    fabric_pressure:float=0.0
    expert_pressure:float=0.0
    bytes_remote:int=0
    family:str="X"
    color:str="a"
    u_h:int=1
    u_v:int=1
    valid:bool=True

@dataclass(frozen=True,slots=True)
class RouteRequest:
    request_id:str
    logical_expert:int
    layer:int
    token_id:int
    kv_key:str=""
    family:str="X"
    r:int=0
    c:int=0
    color:str="a"
    preferred_scope:int=0

@dataclass(frozen=True,slots=True)
class RouteDecision:
    request_id:str
    candidate_id:str
    cost:float
    family:str
    color:str
    u_h:int
    u_v:int
    reason:str
    receipt_word32:int

@dataclass(frozen=True)
class CostWeights:
    miss:float=4.0
    transfer_ms:float=1.0
    queue_ms:float=1.0
    thermal:float=1.2
    fabric:float=1.0
    expert:float=1.4
    scope:float=0.35
    lane_collision:float=0.8
    migration:float=0.5

def route_cost(c:RouteCandidate,w:CostWeights=CostWeights(),lane_collision=0.0)->float:
    return (w.miss*(1.0-c.cache_hit)+w.transfer_ms*c.transfer_ms+
            w.queue_ms*c.queue_ms+w.thermal*c.thermal_pressure+
            w.fabric*c.fabric_pressure+w.expert*c.expert_pressure+
            w.scope*abs(c.scope)+w.lane_collision*lane_collision)

class SpectralRendezvousRouter:
    def __init__(self,weights:CostWeights=CostWeights()): self.weights=weights
    def preferred_lane(self,req:RouteRequest):
        z=stable_u64(req.kv_key,req.logical_expert,req.layer,req.token_id)
        return U9[z%6],U9[(z//6)%6]
    def choose(self,req:RouteRequest,candidates:Sequence[RouteCandidate],occupied_lanes:Optional[set[tuple[str,int,int]]]=None)->RouteDecision:
        occupied_lanes=occupied_lanes or set(); pref=self.preferred_lane(req); best=None
        for c in candidates:
            if not c.valid: continue
            collision=1.0 if (c.family,c.u_h,c.u_v) in occupied_lanes else 0.0
            lane_penalty=0.0 if (c.u_h,c.u_v)==pref else 0.05
            cost=route_cost(c,self.weights,collision)+lane_penalty
            key=(cost,stable_u64(req.request_id,c.candidate_id))
            if best is None or key<best[0]: best=(key,c)
        if best is None: raise RuntimeError("no valid route candidate")
        c=best[1]
        state=SuperplaneState(family=c.family,r=req.r%9,c=req.c%9,u_h=c.u_h,u_v=c.u_v,color=c.color,scope=c.scope)
        return RouteDecision(req.request_id,c.candidate_id,best[0][0],c.family,c.color,c.u_h,c.u_v,"spectral-rendezvous+resource-cost",state.routing_word32)

def hungarian(cost):
    """Minimum-cost assignment for n rows, m columns, n<=m."""
    n=len(cost)
    if n==0:return []
    m=len(cost[0])
    if any(len(r)!=m for r in cost): raise ValueError("ragged matrix")
    if n>m: raise ValueError("need at least as many resource columns as requests")
    u=[0.0]*(n+1);v=[0.0]*(m+1);p=[0]*(m+1);way=[0]*(m+1);INF=1e30
    for i in range(1,n+1):
        p[0]=i;j0=0;minv=[INF]*(m+1);used=[False]*(m+1)
        while True:
            used[j0]=True;i0=p[j0];delta=INF;j1=0
            for j in range(1,m+1):
                if used[j]:continue
                cur=cost[i0-1][j-1]-u[i0]-v[j]
                if cur<minv[j]:minv[j]=cur;way[j]=j0
                if minv[j]<delta:delta=minv[j];j1=j
            for j in range(m+1):
                if used[j]:u[p[j]]+=delta;v[j]-=delta
                else:minv[j]-=delta
            j0=j1
            if p[j0]==0:break
        while True:
            j1=way[j0];p[j0]=p[j1];j0=j1
            if j0==0:break
    ans=[-1]*n
    for j in range(1,m+1):
        if p[j]!=0:ans[p[j]-1]=j-1
    return ans

class LambdaExchangeMatcher:
    BIG=1e12
    def __init__(self,weights:CostWeights=CostWeights()):self.weights=weights
    def family_allowed(self,req,cand):
        return cand.family in FAMS if is_lambda_exchange(req.c%9) else cand.family==req.family
    def assign(self,requests:Sequence[RouteRequest],resource_columns:Sequence[RouteCandidate]):
        if len(requests)>len(resource_columns):raise ValueError("insufficient resource columns")
        matrix=[]
        for req in requests:
            matrix.append([route_cost(c,self.weights) if c.valid and self.family_allowed(req,c) else self.BIG for c in resource_columns])
        cols=hungarian(matrix);out=[];unresolved=[]
        for i,j in enumerate(cols):
            if j<0 or matrix[i][j]>=self.BIG/2:unresolved.append(requests[i].request_id);continue
            req=requests[i];c=resource_columns[j]
            state=SuperplaneState(family=c.family,r=req.r%9,c=req.c%9,u_h=c.u_h,u_v=c.u_v,color=c.color,scope=c.scope)
            out.append(RouteDecision(req.request_id,c.candidate_id,matrix[i][j],c.family,c.color,c.u_h,c.u_v,"lambda-exchange-mincost-matching" if c.family!=req.family else "mincost-matching",state.routing_word32))
        return out,unresolved

class HierarchicalCacheGovernor:
    def choose(self,req,candidates):
        valid=[c for c in candidates if c.valid]
        if not valid:raise RuntimeError("no cache candidates")
        return min(valid,key=lambda c:(0 if c.cache_hit else 1,c.transfer_ms+c.queue_ms,c.scope,stable_u64(req.request_id,c.candidate_id)))

class ThermalEntropyGovernor:
    def rank_penalties(self,candidates):
        by={}
        for c in candidates:by.setdefault(c.rank,[]).append(c)
        raw={r:statistics.fmean(c.thermal_pressure+c.fabric_pressure+c.expert_pressure for c in cs)/3.0 for r,cs in by.items()}
        if not raw:return {}
        mean=statistics.fmean(raw.values())
        return {r:max(0.0,x-mean) for r,x in raw.items()}

class CoprimeHandshakeScheduler:
    def __init__(self,u_h=1,u_v=1):
        if u_h not in U9 or u_v not in U9:raise ValueError
        self.u_h=u_h;self.u_v=u_v;rows=full_y_rows("Z",u_h,u_v)
        if len(rows)!=1:raise AssertionError("exact y-lane theorem violated")
        self.r=rows[0]
    def slot(self,tick:int):
        return SuperplaneState(family="Z",r=self.r,c=tick%9,u_h=self.u_h,u_v=self.u_v)
