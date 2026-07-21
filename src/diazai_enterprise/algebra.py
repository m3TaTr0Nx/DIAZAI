from __future__ import annotations
from dataclasses import dataclass
from itertools import permutations
from math import gcd

MODULUS=9
DIGITS=tuple(range(1,10))
UNITS=(1,2,4,5,7,8)
STATORS=(3,6,9)
GENERATORS={"GX":(0,1,2),"GY":(0,1,5),"GZ":(0,1,8),"GV":(1,1,1),"GT":(0,3,6)}
Triple=tuple[int,int,int]

def residue(n:int)->int:return n%9
def dr(n:int)->int:
    r=n%9
    return 9 if r==0 else r

def encode_address(t:Triple)->int:
    if any(d not in DIGITS for d in t):raise ValueError("digits must be 1..9")
    i,j,k=t;return (i-1)*81+(j-1)*9+k-1

def decode_address(a:int)->Triple:
    if not 0<=a<729:raise ValueError("address must be 0..728")
    i,r=divmod(a,81);j,k=divmod(r,9);return i+1,j+1,k+1

def digit_to_trits(d:int)->tuple[int,int]:
    if d not in DIGITS:raise ValueError("digit must be 1..9")
    return divmod(d-1,3)

def triple_to_six_trits(t:Triple)->tuple[int,...]:return tuple(x for d in t for x in digit_to_trits(d))
def atlas_position(t:Triple)->tuple[int,int]:
    p=[digit_to_trits(d) for d in t]
    return 9*p[0][0]+3*p[1][0]+p[2][0],9*p[0][1]+3*p[1][1]+p[2][1]
def from_atlas_position(row:int,col:int)->Triple:
    if not(0<=row<27 and 0<=col<27):raise ValueError("atlas coords 0..26")
    hi,r=divmod(row,9);hj,hk=divmod(r,3);li,r=divmod(col,9);lj,lk=divmod(r,3)
    return 1+3*hi+li,1+3*hj+lj,1+3*hk+lk

def add(t:Triple,g:Triple,stride:int=1)->Triple:return tuple(dr(v+stride*x) for v,x in zip(t,g))
def negate(t:Triple)->Triple:return tuple(dr(-residue(v)) for v in t)
def permute(t:Triple,p:tuple[int,int,int])->Triple:return t[p[0]],t[p[1]],t[p[2]]
def superplane(slope:int)->list[list[Triple]]:return [[(r,dr(r+c),dr(r+slope*c)) for c in range(9)] for r in DIGITS]
def classify_coprimality(t:Triple)->str:
    i,j,k=t
    if gcd(i,j)==gcd(j,k)==gcd(i,k)==1:return "Y"
    if gcd(gcd(i,j),k)==1:return "S"
    return "N"
def hinge_integer(t:Triple)->bool:i,j,k=t;return i*k==j*j
def hinge_mod9(t:Triple)->bool:i,j,k=t;return residue(i*k-j*j)==0
def orbit(t:Triple,g:Triple,limit:int=9)->list[Triple]:
    out=[t];cur=t
    for _ in range(limit-1):
        cur=add(cur,g)
        if cur==t:break
        out.append(cur)
    return out
def s3_orbit(t:Triple)->tuple[Triple,...]:return tuple(dict.fromkeys(permute(t,p) for p in permutations((0,1,2))))
def all_states():
    for i in DIGITS:
        for j in DIGITS:
            for k in DIGITS:yield i,j,k
@dataclass(frozen=True)
class StateDescriptor:
    triple:Triple;address:int;six_trits:tuple[int,...];atlas_position:tuple[int,int];digital_root:int;coprimality:str;hinge_integer:bool;hinge_mod9:bool
def describe(t:Triple)->StateDescriptor:
    return StateDescriptor(t,encode_address(t),triple_to_six_trits(t),atlas_position(t),dr(sum(t)),classify_coprimality(t),hinge_integer(t),hinge_mod9(t))
