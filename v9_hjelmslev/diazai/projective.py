"""Projective Hjelmslev line P^1(Z9) and reduction to P^1(F3)."""
P1_Z9=[(1,t) for t in range(9)]+[(0,1),(3,1),(6,1)]
FIBERS={
 "F0":[(1,0),(1,3),(1,6)],
 "F1":[(1,1),(1,4),(1,7)],
 "F2_XYZ":[(1,2),(1,5),(1,8)],
 "Finf":[(0,1),(3,1),(6,1)],
}

def reduce_direction(rep):
    a,b=rep
    a%=3;b%=3
    if a:
        inva=1 if a==1 else 2
        return (1,(b*inva)%3)
    if b:
        return (0,1)
    raise ValueError("non-unimodular reduction")

def fiber(rep):
    d=reduce_direction(rep)
    return {(1,0):"F0",(1,1):"F1",(1,2):"F2_XYZ",(0,1):"Finf"}[d]
