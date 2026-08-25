"""
DIAZAI Spectral–Physical Intertwiner v0.5

Tagged route space:
    H_tag = C[C3_family × Z9_r × Z9_c], dim 243.

Physical ambient:
    H_phys = C[Z9^3], dim 729.

The collapse E maps each tagged basis state |f,r,c> to the ambient superplane
cell |P_f(r,c)>. It is injective on private route cells and 3-to-1 on the
27 Lambda/T cells.

The unitary route-spectrum transform is
    U = F3_family ⊗ F9_r ⊗ F9_c.

The actual spectral-to-physical intertwiner is
    I = E U^{-1}.

On each Lambda/T fiber, E retains the family-common mode and annihilates the
two C3 chiral modes because 1+omega+omega^2=0.

This module also characterizes which coordinate operations descend through E:
vertical affine actions always descend; horizontal affine actions c -> u c + b
descend exactly when b ∈ 3 Z9. This is the algebraic reason the Lambda ±3
operators are state-preserving exchange operations while a generic ±1
horizontal step requires the family tag.
"""
from __future__ import annotations
from dataclasses import dataclass
import cmath, math
import numpy as np

FAMS=("X","Y","Z")
FIDX={f:i for i,f in enumerate(FAMS)}
SEEDS={"X":(0,1,2),"Y":(0,1,5),"Z":(0,1,8)}
LAM=(1,1,1)
U9=(1,2,4,8,7,5)

def smul(u,v): return tuple((u*x)%9 for x in v)
def add3(a,b): return tuple((x+y)%9 for x,y in zip(a,b))

def plane_state(family,r,c):
    return add3(smul(r,LAM),smul(c,SEEDS[family]))

def ambient_index(t):
    i,j,k=t
    return i*81+j*9+k

def tagged_index(family,r,c):
    return FIDX[family]*81+r*9+c

def untagged_index(a):
    f,rem=divmod(a,81)
    r,c=divmod(rem,9)
    return FAMS[f],r,c

def route_fft(x):
    """Unitary F3 ⊗ F9 ⊗ F9, negative-exponent NumPy convention."""
    a=np.asarray(x,dtype=np.complex128).reshape(3,9,9)
    return np.fft.fftn(a,axes=(0,1,2),norm="ortho")

def route_ifft(xhat):
    a=np.asarray(xhat,dtype=np.complex128).reshape(3,9,9)
    return np.fft.ifftn(a,axes=(0,1,2),norm="ortho")

def collapse(tagged):
    """E: H_tag -> H_phys, accumulating the three tags on Lambda/T."""
    a=np.asarray(tagged,dtype=np.complex128).reshape(3,9,9)
    out=np.zeros(729,dtype=np.complex128)
    for fi,f in enumerate(FAMS):
        for r in range(9):
            for c in range(9):
                out[ambient_index(plane_state(f,r,c))]+=a[fi,r,c]
    return out

def spectral_to_physical(route_spectrum):
    """I = E U^{-1}."""
    return collapse(route_ifft(route_spectrum))

def preimage_fibers():
    d={}
    for f in FAMS:
        for r in range(9):
            for c in range(9):
                p=ambient_index(plane_state(f,r,c))
                d.setdefault(p,[]).append((f,r,c))
    return d

def collapse_spectrum():
    fibers=preimage_fibers()
    mult={}
    for pre in fibers.values():
        mult[len(pre)]=mult.get(len(pre),0)+1
    assert mult=={1:162,3:27}
    return {
      "rank":189,
      "nullity":54,
      "fiber_cardinality_census":mult,
      "E_dagger_E_eigenvalues":{"3":27,"1":162,"0":54},
      "singular_values":{"sqrt(3)":27,"1":162,"0":54},
    }

def family_common_vector():
    return np.array([1,1,1],dtype=np.complex128)/math.sqrt(3)

def family_chiral_plus():
    w=cmath.exp(2j*math.pi/3)
    return np.array([1,w,w*w],dtype=np.complex128)/math.sqrt(3)

def family_chiral_minus():
    w=cmath.exp(2j*math.pi/3)
    return np.array([1,w*w,w],dtype=np.complex128)/math.sqrt(3)

def tagged_basis(family,r,c):
    out=np.zeros((3,9,9),dtype=np.complex128)
    out[FIDX[family],r,c]=1
    return out

def family_mode_at(r,c,mode="common"):
    out=np.zeros((3,9,9),dtype=np.complex128)
    v={"common":family_common_vector(),
       "chiral+":family_chiral_plus(),
       "chiral-":family_chiral_minus()}[mode]
    out[:,r,c]=v
    return out

def translate_tagged(x,df=0,dr=0,dc=0):
    a=np.asarray(x,dtype=np.complex128).reshape(3,9,9)
    return np.roll(a,shift=(df,dr,dc),axis=(0,1,2))

def translation_phase(df=0,dr=0,dc=0):
    q=np.arange(3)[:,None,None]
    m=np.arange(9)[None,:,None]
    n=np.arange(9)[None,None,:]
    return np.exp(-2j*math.pi*(q*df/3+m*dr/9+n*dc/9))

def scale_tagged(x,u_r=1,u_c=1):
    if u_r not in U9 or u_c not in U9: raise ValueError("U9 units required")
    a=np.asarray(x,dtype=np.complex128).reshape(3,9,9)
    out=np.zeros_like(a)
    for fi in range(3):
        for r in range(9):
            for c in range(9):
                out[fi,(u_r*r)%9,(u_c*c)%9]=a[fi,r,c]
    return out

def scale_spectrum_expected(xhat,u_r=1,u_c=1):
    a=np.asarray(xhat,dtype=np.complex128).reshape(3,9,9)
    out=np.zeros_like(a)
    for q in range(3):
        for m in range(9):
            for n in range(9):
                out[q,m,n]=a[q,(u_r*m)%9,(u_c*n)%9]
    return out

def physical_equivalent(x,y):
    return plane_state(*x)==plane_state(*y)

def action_image(tag,u_r=1,u_c=1,dr=0,dc=0,df=0):
    f,r,c=tag
    fi=(FIDX[f]+df)%3
    return FAMS[fi], (u_r*r+dr)%9, (u_c*c+dc)%9

def action_descends(u_r=1,u_c=1,dr=0,dc=0,df=0):
    if u_r not in U9 or u_c not in U9:
        return False
    fibers=preimage_fibers()
    for pre in fibers.values():
        if len(pre)<2: continue
        images=[plane_state(*action_image(x,u_r,u_c,dr,dc,df)) for x in pre]
        if len(set(images))!=1:
            return False
    return True

def descent_parameter_census():
    good=[]
    bad=[]
    for df in range(3):
      for ur in U9:
       for uc in U9:
        for dr in range(9):
         for dc in range(9):
          rec=(df,ur,uc,dr,dc)
          (good if action_descends(ur,uc,dr,dc,df) else bad).append(rec)
    return good,bad

@dataclass(frozen=True)
class IntertwinerReceipt:
    rank:int
    nullity:int
    private_cells:int
    lambda_cells:int
    tagged_dimension:int=243
    physical_dimension:int=729
    union_dimension:int=189

def desc_elements():
    return [(df,ur,uc,dr,dc) for df in range(3) for ur in U9 for uc in U9 for dr in range(9) for dc in (0,3,6)]

def compose_desc(g,h):
    dfg,urg,ucg,drg,dcg=g
    dfh,urh,uch,drh,dch=h
    return ((dfg+dfh)%3,(urg*urh)%9,(ucg*uch)%9,(urg*drh+drg)%9,(ucg*dch+dcg)%9)

def inverse_desc(g):
    df,ur,uc,dr,dc=g
    iur=pow(ur,-1,9); iuc=pow(uc,-1,9)
    return ((-df)%3,iur,iuc,(-iur*dr)%9,(-iuc*dc)%9)

DESC_ID=(0,1,1,0,0)
