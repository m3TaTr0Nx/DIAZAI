"""DIAZAI Lambda/T Nine-Map exact codecs v9.1."""
U9=(1,2,4,8,7,5)
LAMBDA=(1,1,1)
GENERATORS={'X':(0,1,2),'Y':(0,1,5),'Z':(0,1,8)}

def add(a,b): return tuple((x+y)%9 for x,y in zip(a,b))
def scale(s,a): return tuple((s*x)%9 for x in a)
def display(x):
    r=x%9
    return 9 if r==0 else r

def column(h,c):
    return [add(scale(r,LAMBDA),scale(c,h)) for r in range(9)]

def column_class(c):
    c%=9
    if c==0:return 'LAMBDA'
    if c in (3,6):return 'STATOR'
    return 'ROTOR'

def column_raster(h,c): return [[display(x) for x in t] for t in column(h,c)]
def equality_class(t):
    n=len(set(t)); return 'AAA' if n==1 else 'AAB' if n==2 else 'ABC'
def aab_rank(pattern,repeated,delta):
    if pattern not in range(3) or repeated not in range(9) or delta not in range(1,9):raise ValueError
    return ((pattern*9+repeated)*8)+(delta-1)
def rank_to_u9cube(rank):
    if rank not in range(216):raise ValueError
    a,rem=divmod(rank,36);b,c=divmod(rem,6); return (U9[a],U9[b],U9[c])
