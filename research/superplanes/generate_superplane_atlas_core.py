import itertools

LAM=(1,1,1)
U9=(1,2,4,8,7,5)
REPS=[(1,t) for t in range(9)]+[(0,1),(3,1),(6,1)]

def add(a,b):
    return tuple((a[i]+b[i])%9 for i in range(3))

def smul(s,a):
    return tuple((s*x)%9 for x in a)

def plane(h):
    return frozenset(add(smul(r,LAM),smul(c,h)) for r in range(9) for c in range(9))

planes={rep:plane((0,rep[0],rep[1])) for rep in REPS}
assert len(set(planes.values()))==12
assert all(len(P)==81 for P in planes.values())

ambient=list(itertools.product(range(9),repeat=3))
hist={}
for x in ambient:
    m=sum(x in P for P in planes.values())
    hist[m]=hist.get(m,0)+1
assert hist=={1:648,3:72,12:9}

# 6 horizontal unit gauges and 6 vertical rotor gauges per full plane.
assert len(U9)*len(U9)*len(planes)==432

print('PASS',hist)
