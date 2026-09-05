import cmath,math
U9=(1,2,4,8,7,5)
FAMS=("X","Y","Z")
LAM=(1,1,1)
SEEDS={"X":(0,1,2),"Y":(0,1,5),"Z":(0,1,8)}

def add(a,b): return tuple((x+y)%9 for x,y in zip(a,b))
def smul(u,v): return tuple((u*x)%9 for x in v)
def generator_state(family,u_h,u_v,r,c):
    H=smul(u_h,SEEDS[family]); V=smul(u_v,LAM)
    return add(smul(r,V),smul(c,H))
def lambda_interval(family,u_h,u_v,r): return [generator_state(family,u_h,u_v,r,c) for c in range(10)]
def kernel(m,n,r,c): return cmath.exp(2j*math.pi*((m*r+n*c)%9)/9)
def rotor_kernel(u_v,u_h,r,c):
    if u_v not in U9 or u_h not in U9: raise ValueError("primitive U9 frequencies required")
    return kernel(u_v,u_h,r,c)
