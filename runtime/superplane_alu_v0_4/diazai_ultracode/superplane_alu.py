from __future__ import annotations
from dataclasses import dataclass,replace,asdict
from enum import Enum,IntEnum
from math import gcd
import cmath,hashlib,json,math,time
from typing import Any,Iterable,Optional
from .routing_word import pack_word
from .superplane_moe import fabric_addr,layer_index,is_lambda_exchange
Z9=tuple(range(9)); U9=(1,2,4,8,7,5); U9SET=set(U9); FAMS=("X","Y","Z"); COLORS=("a","b","c"); LAM=(1,1,1)
SEEDS={"X":(0,1,2),"Y":(0,1,5),"Z":(0,1,8)}; FAMILY12_BIT={"X":2,"Y":5,"Z":8}

def smul(u,v): return tuple((u*x)%9 for x in v)
def add3(a,b): return tuple((x+y)%9 for x,y in zip(a,b))
def uinv(u):
    if u not in U9SET: raise ValueError(f"{u} is not a unit of Z9")
    return pow(u,-1,9)
def dlog2_u9(u):
    if u not in U9SET: raise ValueError(u)
    x=1
    for e in range(6):
        if x==u:return e
        x=2*x%9
    raise AssertionError
def inv_mod6(n):
    n%=6
    if gcd(n,6)!=1: raise ValueError(n)
    return next(x for x in range(6) if n*x%6==1)

class Cover(str,Enum): R="R"; L="L"
class Scope(IntEnum): LOCAL_GPU=0; NODE=1; RACK=2; GLOBAL_CLUSTER=3
class Op(str,Enum):
    NOP="NOP"; ADDH="ADDH"; SUBH="SUBH"; ADDR="ADDR"; SUBR="SUBR"; MULV="MULV"; DIVV="DIVV"; MULH="MULH"; DIVH="DIVH"; POWV="POWV"; POWH="POWH"; DUAL="DUAL"; LAMBDA_FWD="LAMBDA_FWD"; LAMBDA_REV="LAMBDA_REV"; LIFT="LIFT"; LOWER="LOWER"; SET_FAMILY="SET_FAMILY"; SET_COLOR="SET_COLOR"; SET_SCOPE="SET_SCOPE"; SET_MASK="SET_MASK"
@dataclass(frozen=True,slots=True)
class Instruction:
    op:Op; arg:Any=None
    @classmethod
    def parse(cls,obj): return cls(Op(obj["op"]),obj.get("arg"))
@dataclass(frozen=True,slots=True)
class SuperplaneState:
    family:str="X"; r:int=0; c:int=0; u_h:int=1; u_v:int=1; cover:Cover=Cover.R; color:str="a"; mask8:int=255; scope:Scope=Scope.LOCAL_GPU; block_depth:int=0
    def __post_init__(self):
        if self.family not in FAMS or not 0<=self.r<9 or not 0<=self.c<9 or self.u_h not in U9SET or self.u_v not in U9SET or self.color not in COLORS or not 0<=self.mask8<=255 or self.block_depth<0: raise ValueError("invalid state")
    @property
    def h(self): return smul(self.u_h,SEEDS[self.family])
    @property
    def v(self): return smul(self.u_v,LAM)
    @property
    def cell(self): return add3(smul(self.r,self.v),smul(self.c,self.h))
    @property
    def lambda_exchange(self): return is_lambda_exchange(self.c)
    @property
    def layer(self): return layer_index(self.family,self.color)
    @property
    def addr729(self): return fabric_addr(self.r,self.c,self.layer)
    @property
    def family12(self): return 1<<FAMILY12_BIT[self.family]
    @property
    def routing_word32(self): return pack_word(self.mask8,self.family12,self.addr729,int(self.scope))
@dataclass(frozen=True,slots=True)
class CharacterObservation:
    freq_r:int; freq_c:int; phase_index9:int; phase_radians:float; value_real:float; value_imag:float; vertical_exp6:int; horizontal_exp6:int
@dataclass(frozen=True,slots=True)
class ALUReceipt:
    seq:int; ts_ns:int; instruction:dict; before:dict; after:dict; cell_before:tuple; cell_after:tuple; word_before:int; word_after:int; reversible:bool; inverse_instruction:Optional[dict]; observation:Optional[dict]; notes:tuple=()
    def canonical_json(self): return json.dumps(asdict(self),sort_keys=True,separators=(",",":"),default=str)
    def sha256(self): return hashlib.sha256(self.canonical_json().encode()).hexdigest()
@dataclass(frozen=True,slots=True)
class ExecutionResult:
    state:SuperplaneState; receipt:ALUReceipt; observation:Optional[CharacterObservation]=None

def dual_observation(s):
    m,n=s.u_v,s.u_h; phase=(m*s.r+n*s.c)%9; z=cmath.exp(2j*math.pi*phase/9)
    return CharacterObservation(m,n,phase,2*math.pi*phase/9,float(z.real),float(z.imag),dlog2_u9(s.u_v),dlog2_u9(s.u_h))
def inverse_instruction(inst):
    a=inst.arg; pairs={Op.ADDH:Op.SUBH,Op.SUBH:Op.ADDH,Op.ADDR:Op.SUBR,Op.SUBR:Op.ADDR,Op.MULV:Op.DIVV,Op.DIVV:Op.MULV,Op.MULH:Op.DIVH,Op.DIVH:Op.MULH,Op.LAMBDA_FWD:Op.LAMBDA_REV,Op.LAMBDA_REV:Op.LAMBDA_FWD,Op.LIFT:Op.LOWER,Op.LOWER:Op.LIFT}
    if inst.op in pairs:return Instruction(pairs[inst.op],a if a is not None else 1)
    if inst.op in (Op.POWV,Op.POWH):
        n=int(a)%6
        return Instruction(inst.op,inv_mod6(n)) if gcd(n,6)==1 else None
    if inst.op in (Op.NOP,Op.DUAL): return Instruction(inst.op,a)
    return None
class SuperplaneALU:
    def __init__(self,state=None): self.state=state or SuperplaneState(); self._seq=0
    def _replace(self,**kw): self.state=replace(self.state,**kw)
    def execute(self,inst):
        before=self.state; obs=None; notes=[]; a=inst.arg
        if inst.op==Op.NOP: pass
        elif inst.op==Op.ADDH:self._replace(c=(before.c+int(a))%9)
        elif inst.op==Op.SUBH:self._replace(c=(before.c-int(a))%9)
        elif inst.op==Op.ADDR:self._replace(r=(before.r+int(a))%9)
        elif inst.op==Op.SUBR:self._replace(r=(before.r-int(a))%9)
        elif inst.op==Op.MULV:
            if int(a) not in U9SET:raise ValueError("MULV requires U9")
            self._replace(r=before.r*int(a)%9)
        elif inst.op==Op.DIVV:self._replace(r=before.r*uinv(int(a))%9)
        elif inst.op==Op.MULH:
            if int(a) not in U9SET:raise ValueError("MULH requires U9")
            self._replace(c=before.c*int(a)%9)
        elif inst.op==Op.DIVH:self._replace(c=before.c*uinv(int(a))%9)
        elif inst.op==Op.POWV:
            n=int(a); old=dlog2_u9(before.u_v); self._replace(u_v=pow(before.u_v,n,9)); notes.append(f"C6 dual k->{n%6}k; exp {old}->{old*n%6}")
        elif inst.op==Op.POWH:
            n=int(a); old=dlog2_u9(before.u_h); self._replace(u_h=pow(before.u_h,n,9)); notes.append(f"C6 dual k->{n%6}k; exp {old}->{old*n%6}")
        elif inst.op==Op.DUAL:obs=dual_observation(before)
        elif inst.op==Op.LAMBDA_FWD:self._replace(c=(before.c+3)%9)
        elif inst.op==Op.LAMBDA_REV:self._replace(c=(before.c-3)%9)
        elif inst.op==Op.LIFT:self._replace(block_depth=before.block_depth+(1 if a is None else int(a)))
        elif inst.op==Op.LOWER:
            n=1 if a is None else int(a)
            if before.block_depth<n:raise ValueError("LOWER")
            self._replace(block_depth=before.block_depth-n)
        elif inst.op==Op.SET_FAMILY:self._replace(family=str(a))
        elif inst.op==Op.SET_COLOR:self._replace(color=str(a))
        elif inst.op==Op.SET_SCOPE:self._replace(scope=Scope(int(a)))
        elif inst.op==Op.SET_MASK:self._replace(mask8=int(a))
        else:raise NotImplementedError(inst.op)
        after=self.state; inv=inverse_instruction(inst); self._seq+=1
        rec=ALUReceipt(self._seq,time.time_ns(),{"op":inst.op.value,"arg":inst.arg},asdict(before),asdict(after),before.cell,after.cell,before.routing_word32,after.routing_word32,inv is not None,None if inv is None else {"op":inv.op.value,"arg":inv.arg},None if obs is None else asdict(obs),tuple(notes))
        return ExecutionResult(after,rec,obs)
    def run(self,program): return [self.execute(i) for i in program]
    def rollback(self,result):
        inv=result.receipt.inverse_instruction
        if inv is None:raise ValueError("nonreversible")
        return self.execute(Instruction.parse(inv))
