"""729-address, 27x27, padded 1000, and 8-bit GF9 control codecs."""
from .z9 import trits,from_trits
from .gf9 import primitive_cycle,projective_direction

def triple_to_six_trits(t):
    out=[]
    for x in t: out.extend(trits(x))
    return tuple(out)

def six_trits_to_triple(q):
    if len(q)!=6: raise ValueError
    return (from_trits(q[0],q[1]),from_trits(q[2],q[3]),from_trits(q[4],q[5]))

def six_trits_to_27x27(q):
    if len(q)!=6: raise ValueError
    return (q[0]*9+q[1]*3+q[2], q[3]*9+q[4]*3+q[5])

def padded_complement(t): return tuple(9-x for x in t)

def body_diagonal(q,kind="+++"):
    if not 0<=q<=9: raise ValueError
    if kind=="+++": return (q,q,q)
    if kind=="++-": return (q,q,9-q)
    if kind=="+-+": return (q,9-q,q)
    if kind=="-++": return (9-q,q,q)
    raise ValueError(kind)

def gf9_control_labels(): return [(idx,v,projective_direction(v)) for idx,v in enumerate(primitive_cycle())]

def decode_mask8(mask):
    if not 0<=mask<256: raise ValueError
    return [i for i in range(8) if (mask>>i)&1]
