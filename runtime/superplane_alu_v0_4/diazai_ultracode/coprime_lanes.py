from math import gcd
from .generator_lanes import U9,FAMS,generator_state

def display(t): return tuple(9 if x==0 else x for x in t)
def coprime_class(t):
    a,b,c=display(t)
    pairwise=(gcd(a,b)==1 and gcd(a,c)==1 and gcd(b,c)==1)
    if pairwise: return "y"
    return "s" if gcd(gcd(a,b),c)==1 else "n"
def full_y_rows(family,u_h,u_v):
    return [r for r in range(9) if all(coprime_class(generator_state(family,u_h,u_v,r,c))=="y" for c in range(9))]
def full_y_cols(family,u_h,u_v):
    return [c for c in range(9) if all(coprime_class(generator_state(family,u_h,u_v,r,c))=="y" for r in range(9))]
def audit_108_gauges():
    return [{"family":f,"u_h":uh,"u_v":uv,"full_y_rows":full_y_rows(f,uh,uv),"full_y_cols":full_y_cols(f,uh,uv)} for f in FAMS for uh in U9 for uv in U9]
