"""Four exact 27x27 scalar tilings from P^1(Z9)->P^1(F3)."""
import numpy as np

FIBERS={"F0":[0,3,6],"F1":[1,4,7],"F2_XYZ":[2,5,8]}
TAIL=[0,3,6]

def disp(x):
    r=x%9
    return 9 if r==0 else r

def affine_k(i,j,t): return disp(i+t*(j-i))
def tail_j(i,k,a): return disp(i+a*(k-i))

def affine_tiling(ts):
    M=np.zeros((27,27),dtype=np.int16)
    for j in range(1,10):
        for i in range(1,10):
            ks=sorted(affine_k(i,j,t) for t in ts)
            br=3*(j-1);bc=3*(i-1)
            for rr,k in enumerate(ks): M[br+rr,bc:bc+3]=[i,j,k]
    return M

def tail_tiling():
    M=np.zeros((27,27),dtype=np.int16)
    for k in range(1,10):
        for i in range(1,10):
            js=sorted(tail_j(i,k,a) for a in TAIL)
            br=3*(k-1);bc=3*(i-1)
            for rr,j in enumerate(js): M[br+rr,bc:bc+3]=[i,j,k]
    return M

def four_tilings():
    return {"F0":affine_tiling(FIBERS["F0"]),"F1":affine_tiling(FIBERS["F1"]),"F2_XYZ":affine_tiling(FIBERS["F2_XYZ"]),"Finf":tail_tiling()}

def expected_lambda_diagonal(): return np.repeat(np.arange(1,10),3)
