FAMS=("X","Y","Z")
FIDX={f:i for i,f in enumerate(FAMS)}
COLORS=("a","b","c")
CIDX={q:i for i,q in enumerate(COLORS)}
SEEDS={"X":(0,1,2),"Y":(0,1,5),"Z":(0,1,8)}
LAM=(1,1,1)

def smul(u,v): return tuple((u*x)%9 for x in v)
def add(a,b): return tuple((x+y)%9 for x,y in zip(a,b))
def plane_state(family,r,c): return add(smul(r,LAM),smul(c,SEEDS[family]))
def layer_index(family,color): return 3*FIDX[family]+CIDX[color]
def unlayer(layer):
    f,q=divmod(layer,3); return FAMS[f],COLORS[q]
def fabric_addr(r,c,layer):
    if not(0<=r<9 and 0<=c<9 and 0<=layer<9): raise ValueError
    return r*81+c*9+layer
def unfabric_addr(a):
    if not 0<=a<729: raise ValueError
    r,x=divmod(a,81); c,l=divmod(x,9); return r,c,l
def is_lambda_exchange(c): return c in (0,3,6)
