import time, statistics, json, math, platform, os
import numpy as np
from numba import njit
try:
    import torch
except Exception:
    torch=None

P1=58321; G1=11; P2=1459; G2=3; N=729
W1=pow(G1,(P1-1)//N,P1); W2=pow(G2,(P2-1)//N,P2)
assert pow(W1,N,P1)==1 and pow(W1,N//3,P1)!=1
assert pow(W2,N,P2)==1 and pow(W2,N//3,P2)!=1

@njit(cache=True)
def powmod(a,e,m):
    r=1; a%=m
    while e>0:
        if e&1: r=(r*a)%m
        a=(a*a)%m; e//=2
    return r

@njit(cache=True)
def ntt_rec(x, root, p):
    n=x.shape[0]
    if n==1:
        y=np.empty(1,np.int64); y[0]=x[0]%p; return y
    m=n//3
    x0=np.empty(m,np.int64); x1=np.empty(m,np.int64); x2=np.empty(m,np.int64)
    for s in range(m):
        x0[s]=x[3*s]; x1[s]=x[3*s+1]; x2[s]=x[3*s+2]
    r3=powmod(root,3,p)
    y0=ntt_rec(x0,r3,p); y1=ntt_rec(x1,r3,p); y2=ntt_rec(x2,r3,p)
    z=powmod(root,m,p); z2=(z*z)%p
    out=np.empty(n,np.int64); wk=1
    for k in range(m):
        A=y0[k]; B=(wk*y1[k])%p; wk2=(wk*wk)%p; C=(wk2*y2[k])%p
        out[k]=(A+B+C)%p
        out[k+m]=(A+(B*z)%p+(C*z2)%p)%p
        out[k+2*m]=(A+(B*z2)%p+(C*z)%p)%p
        wk=(wk*root)%p
    return out

@njit(cache=True)
def ntt_inv(x,root,p):
    y=ntt_rec(x,powmod(root,p-2,p),p); ninv=powmod(x.shape[0],p-2,p)
    for i in range(y.shape[0]): y[i]=(y[i]*ninv)%p
    return y

@njit(cache=True)
def cyclic_conv_direct(a,b):
    n=a.shape[0]; out=np.zeros(n,np.int64)
    for i in range(n):
        s=0
        for j in range(n): s += a[j]*b[(i-j)%n]
        out[i]=s
    return out

@njit(cache=True)
def conv_mod_ntt(a,b,root,p):
    aa=np.empty(a.shape[0],np.int64); bb=np.empty(b.shape[0],np.int64)
    for i in range(a.shape[0]): aa[i]=a[i]%p; bb[i]=b[i]%p
    A=ntt_rec(aa,root,p); B=ntt_rec(bb,root,p)
    for i in range(A.shape[0]): A[i]=(A[i]*B[i])%p
    return ntt_inv(A,root,p)

@njit(cache=True)
def crt2_signed(r1,r2,p1,p2):
    n=r1.shape[0]; out=np.empty(n,np.int64); inv=powmod(p1,p2-2,p2); M=p1*p2; half=M//2
    for i in range(n):
        t=(((r2[i]-r1[i])%p2)*inv)%p2; x=r1[i]+p1*t
        if x>half: x-=M
        out[i]=x
    return out

def py_ntt(x,root,p):
    n=len(x)
    if n==1:return [x[0]%p]
    m=n//3; y=[py_ntt(x[r::3],pow(root,3,p),p) for r in range(3)]
    z=pow(root,m,p); z2=z*z%p; out=[0]*n; wk=1
    for k in range(m):
        A=y[0][k]; B=wk*y[1][k]%p; C=(wk*wk%p)*y[2][k]%p
        out[k]=(A+B+C)%p; out[k+m]=(A+B*z+C*z2)%p; out[k+2*m]=(A+B*z2+C*z)%p; wk=wk*root%p
    return out

def bench(fn,reps=100,warm=10):
    for _ in range(warm): fn()
    vals=[]
    for _ in range(reps):
        t=time.perf_counter_ns(); fn(); vals.append((time.perf_counter_ns()-t)/1e6)
    vals.sort(); return {'median_ms':float(statistics.median(vals)),'p10_ms':float(vals[int(.1*(len(vals)-1))]),'p90_ms':float(vals[int(.9*(len(vals)-1))]),'min_ms':float(vals[0]),'reps':reps}

rng=np.random.default_rng(7); x=rng.integers(-127,128,size=N,dtype=np.int64); h=rng.integers(-127,128,size=N,dtype=np.int64)
z=ntt_rec(x%P1,W1,P1); assert np.array_equal(ntt_inv(z,W1,P1),x%P1)
d=cyclic_conv_direct(x,h); r1=conv_mod_ntt(x,h,W1,P1); r2=conv_mod_ntt(x,h,W2,P2); assert np.array_equal(crt2_signed(r1,r2,P1,P2),d)
f=np.fft.ifft(np.fft.fft(x.astype(np.float64))*np.fft.fft(h.astype(np.float64))).real; assert np.max(np.abs(np.rint(f).astype(np.int64)-d))==0
assert np.array_equal(np.array(py_ntt(list(x%P1),W1,P1),dtype=np.int64),z)

res={}
res['ntt729_numba_exact_fixed']=bench(lambda:ntt_rec(x%P1,W1,P1),400,40)
res['intt729_numba_exact_fixed']=bench(lambda:ntt_inv(z,W1,P1),400,40)
res['ntt729_python_generic']=bench(lambda:py_ntt(list(x%P1),W1,P1),30,2)
res['conv729_singleprime_numba']=bench(lambda:conv_mod_ntt(x,h,W1,P1),150,15)
res['conv729_twoprime_rns_exact']=bench(lambda:crt2_signed(conv_mod_ntt(x,h,W1,P1),conv_mod_ntt(x,h,W2,P2),P1,P2),100,10)
res['conv729_direct_int64_numba']=bench(lambda:cyclic_conv_direct(x,h),100,10)
res['fft729_numpy_float64']=bench(lambda:np.fft.fft(x.astype(np.float64)),1000,100)
res['conv729_numpy_fft_float64']=bench(lambda:np.fft.ifft(np.fft.fft(x.astype(np.float64))*np.fft.fft(h.astype(np.float64))).real,700,70)
C=np.empty((N,N),np.float64); hf=h.astype(np.float64)
for i in range(N):
    for j in range(N): C[i,j]=hf[(i-j)%N]
xf=x.astype(np.float64); res['dense729_circulant_matvec_numpy']=bench(lambda:C@xf,300,30)
XB=rng.normal(size=(64,N)); res['dense729_batch64_numpy']=bench(lambda:XB@C.T,100,10); res['fftconv729_batch64_numpy']=bench(lambda:np.fft.ifft(np.fft.fft(XB,axis=1)*np.fft.fft(hf)[None,:],axis=1).real,100,10)
scales={}
for n in [3,9,27,81,243,729]:
    w=pow(G1,(P1-1)//n,P1); xx=(x[:n]%P1).copy(); ntt_rec(xx,w,P1); scales[str(n)]=bench(lambda xx=xx,w=w:ntt_rec(xx,w,P1),500 if n<=243 else 300,50)
pt={}
if torch is not None:
    tx=torch.from_numpy(x.astype(np.float64)); th=torch.from_numpy(h.astype(np.float64)); tC=torch.from_numpy(C)
    pt['torch_fft729_cpu']=bench(lambda:torch.fft.fft(tx),500,50); pt['torch_fftconv729_cpu']=bench(lambda:torch.fft.ifft(torch.fft.fft(tx)*torch.fft.fft(th)).real,300,30); pt['torch_dense729_cpu']=bench(lambda:tC@tx,300,30)
stages=6; butterflies=stages*(N//3)
out={'environment':{'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,'numba':__import__('numba').__version__,'torch':getattr(torch,'__version__',None),'cpu_count':os.cpu_count()},'parameters':{'N':N,'p1':P1,'root1':W1,'p2':P2,'root2':W2,'coeff_range':'int8 [-127,127]','crt_product':P1*P2,'stages':stages,'radix3_butterflies':butterflies},'correctness':{'ntt_roundtrip':True,'python_generic_matches_fixed':True,'rns_equals_direct':True,'numpy_fft_rounding_equals_direct':True},'benchmarks':res,'torch_cpu':pt,'scales':scales}
b=out['benchmarks']; out['derived']={'fixed_vs_generic_python_ntt_speedup':b['ntt729_python_generic']['median_ms']/b['ntt729_numba_exact_fixed']['median_ms'],'rns_ntt_vs_direct_exact_speedup':b['conv729_direct_int64_numba']['median_ms']/b['conv729_twoprime_rns_exact']['median_ms'],'numpy_fft_vs_exact_fixed_ntt_ratio':b['ntt729_numba_exact_fixed']['median_ms']/b['fft729_numpy_float64']['median_ms'],'batch64_dense_vs_fftconv_speedup':b['dense729_batch64_numpy']['median_ms']/b['fftconv729_batch64_numpy']['median_ms']}
open('diazai_deep_benchmark_results.json','w').write(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
