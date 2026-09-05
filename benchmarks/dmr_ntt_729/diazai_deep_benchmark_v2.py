import time, statistics, json, math, platform, os
import numpy as np
from numba import njit

P1=58321; G1=11; P2=1459; G2=3; N=729
W1=pow(G1,(P1-1)//N,P1); W2=pow(G2,(P2-1)//N,P2)

@njit(cache=True)
def powmod(a,e,m):
    r=1; a%=m
    while e:
        if e&1: r=(r*a)%m
        a=(a*a)%m; e//=2
    return r

@njit(cache=True)
def modhalf(x,p):
    x%=p
    if x&1: x+=p
    return x>>1

@njit(cache=True)
def ntt_rec_naive(x, root, p):
    n=x.shape[0]
    if n==1:
        y=np.empty(1,np.int64); y[0]=x[0]%p; return y
    m=n//3
    x0=np.empty(m,np.int64); x1=np.empty(m,np.int64); x2=np.empty(m,np.int64)
    for s in range(m): x0[s]=x[3*s]; x1[s]=x[3*s+1]; x2[s]=x[3*s+2]
    r3=powmod(root,3,p)
    y0=ntt_rec_naive(x0,r3,p); y1=ntt_rec_naive(x1,r3,p); y2=ntt_rec_naive(x2,r3,p)
    z=powmod(root,m,p); z2=z*z%p
    out=np.empty(n,np.int64); wk=1
    for k in range(m):
        A=y0[k]; B=wk*y1[k]%p; wk2=wk*wk%p; C=wk2*y2[k]%p
        out[k]=(A+B+C)%p
        out[k+m]=(A+B*z+C*z2)%p
        out[k+2*m]=(A+B*z2+C*z)%p
        wk=wk*root%p
    return out

@njit(cache=True)
def ntt_rec_opt(x, root, p):
    n=x.shape[0]
    if n==1:
        y=np.empty(1,np.int64); y[0]=x[0]%p; return y
    m=n//3
    x0=np.empty(m,np.int64); x1=np.empty(m,np.int64); x2=np.empty(m,np.int64)
    for s in range(m): x0[s]=x[3*s]; x1[s]=x[3*s+1]; x2[s]=x[3*s+2]
    r3=powmod(root,3,p)
    y0=ntt_rec_opt(x0,r3,p); y1=ntt_rec_opt(x1,r3,p); y2=ntt_rec_opt(x2,r3,p)
    z=powmod(root,m,p); z2=z*z%p
    gamma=modhalf((z-z2)%p,p)
    out=np.empty(n,np.int64); wk=1
    for k in range(m):
        A=y0[k]; B=wk*y1[k]%p; wk2=wk*wk%p; C=wk2*y2[k]%p
        s=(B+C)%p; d=(B-C)%p; hs=modhalf(s,p); gd=gamma*d%p; base=(A-hs)%p
        out[k]=(A+s)%p; out[k+m]=(base+gd)%p; out[k+2*m]=(base-gd)%p
        wk=wk*root%p
    return out

@njit(cache=True)
def intt_opt(x,root,p):
    y=ntt_rec_opt(x,powmod(root,p-2,p),p); ninv=powmod(x.shape[0],p-2,p)
    for i in range(y.shape[0]): y[i]=y[i]*ninv%p
    return y

@njit(cache=True)
def conv_opt(a,b,root,p):
    aa=np.empty(a.shape[0],np.int64); bb=np.empty(b.shape[0],np.int64)
    for i in range(a.shape[0]): aa[i]=a[i]%p; bb[i]=b[i]%p
    A=ntt_rec_opt(aa,root,p); B=ntt_rec_opt(bb,root,p)
    for i in range(A.shape[0]): A[i]=A[i]*B[i]%p
    return intt_opt(A,root,p)

@njit(cache=True)
def conv_pretransformed(a,B,root,p):
    aa=np.empty(a.shape[0],np.int64)
    for i in range(a.shape[0]): aa[i]=a[i]%p
    A=ntt_rec_opt(aa,root,p)
    for i in range(A.shape[0]): A[i]=A[i]*B[i]%p
    return intt_opt(A,root,p)

@njit(cache=True)
def direct(a,b):
    n=a.shape[0]; o=np.zeros(n,np.int64)
    for i in range(n):
        s=0
        for j in range(n): s+=a[j]*b[(i-j)%n]
        o[i]=s
    return o

@njit(cache=True)
def crt2(r1,r2,p1,p2):
    inv=powmod(p1,p2-2,p2); M=p1*p2; half=M//2; o=np.empty(r1.shape[0],np.int64)
    for i in range(r1.shape[0]):
        t=((r2[i]-r1[i])%p2)*inv%p2; x=r1[i]+p1*t
        if x>half: x-=M
        o[i]=x
    return o

def bench(fn,reps=200,warm=20):
    for _ in range(warm): fn()
    v=[]
    for _ in range(reps):
        t=time.perf_counter_ns(); fn(); v.append((time.perf_counter_ns()-t)/1e6)
    v.sort(); return {'median_ms':statistics.median(v),'p10_ms':v[int(.1*(len(v)-1))],'p90_ms':v[int(.9*(len(v)-1))],'min_ms':v[0]}

rng=np.random.default_rng(42); x=rng.integers(-127,128,N,dtype=np.int64); h=rng.integers(-127,128,N,dtype=np.int64)
a=x%P1
n1=ntt_rec_naive(a,W1,P1); o1=ntt_rec_opt(a,W1,P1); assert np.array_equal(n1,o1); assert np.array_equal(intt_opt(o1,W1,P1),a)
D=direct(x,h); H1=ntt_rec_opt(h%P1,W1,P1); H2=ntt_rec_opt(h%P2,W2,P2)
r1=conv_opt(x,h,W1,P1); r2=conv_opt(x,h,W2,P2); assert np.array_equal(crt2(r1,r2,P1,P2),D)

res={}
res['ntt729_naive_radix3_core']=bench(lambda:ntt_rec_naive(a,W1,P1),500,50)
res['ntt729_optimized_radix3_core']=bench(lambda:ntt_rec_opt(a,W1,P1),500,50)
res['inference_singleprime_pretransformed_weight']=bench(lambda:conv_pretransformed(x,H1,W1,P1),300,30)
res['inference_twoprime_pretransformed_weight']=bench(lambda:crt2(conv_pretransformed(x,H1,W1,P1),conv_pretransformed(x,H2,W2,P2),P1,P2),200,20)
res['full_twoprime_conv_weight_transform_included']=bench(lambda:crt2(conv_opt(x,h,W1,P1),conv_opt(x,h,W2,P2),P1,P2),150,15)
res['direct_exact_cyclic_conv']=bench(lambda:direct(x,h),100,10)
res['numpy_fftconv']=bench(lambda:np.fft.ifft(np.fft.fft(x.astype(float))*np.fft.fft(h.astype(float))).real,700,70)

@njit(cache=True)
def batch_pretransformed(X,H,root,p):
    B=X.shape[0]; O=np.empty(X.shape,np.int64)
    for b in range(B): O[b]=conv_pretransformed(X[b],H,root,p)
    return O
batch={}
for B in [1,4,16,64]:
    X=rng.integers(-32,33,size=(B,N),dtype=np.int64)
    batch[str(B)]=bench(lambda X=X:batch_pretransformed(X,H1,W1,P1),80 if B<=16 else 30,10)

W27=pow(G1,(P1-1)//27,P1)
@njit(cache=True)
def ntt2_27(x,p,root):
    A=x.copy()
    for r in range(27): A[r,:]=ntt_rec_opt(A[r,:],root,p)
    for c in range(27): A[:,c]=ntt_rec_opt(A[:,c].copy(),root,p)
    return A
arr=(x%P1).reshape(27,27); ntt2_27(arr,P1,W27)
res['ntt2_27x27_separable']=bench(lambda:ntt2_27(arr,P1,W27),300,30)

stages=6; bfly3=N//3*stages; mult3=3*bfly3
bfly2_1024=1024//2*10; mult2=bfly2_1024
out={'environment':{'platform':platform.platform(),'python':platform.python_version(),'numpy':np.__version__,'cpu_count':os.cpu_count()},'parameters':{'N':N,'p1':P1,'p2':P2,'root1':W1,'root2':W2},'correctness':{'optimized_equals_naive':True,'roundtrip':True,'two_prime_crt_exact':True},'benchmarks':res,'batch_singleprime_pretransformed':batch,'operation_model':{'radix3_729_stages':6,'radix3_butterflies':bfly3,'optimized_general_modular_multiplies_approx':mult3,'padded_radix2_1024_butterflies':bfly2_1024,'padded_radix2_general_twiddle_multiplies_approx':mult2,'radix3_vs_padded_radix2_mult_ratio':mult3/mult2,'memory_points_ratio_729_to_1024':729/1024}}
out['derived']={'optimized_vs_naive_radix3_speedup':res['ntt729_naive_radix3_core']['median_ms']/res['ntt729_optimized_radix3_core']['median_ms'],'pretransformed_twoprime_vs_full_twoprime_speedup':res['full_twoprime_conv_weight_transform_included']['median_ms']/res['inference_twoprime_pretransformed_weight']['median_ms'],'pretransformed_twoprime_vs_direct_speedup':res['direct_exact_cyclic_conv']['median_ms']/res['inference_twoprime_pretransformed_weight']['median_ms'],'exact_pretransformed_twoprime_vs_numpy_fftconv_slowdown':res['inference_twoprime_pretransformed_weight']['median_ms']/res['numpy_fftconv']['median_ms'],'ntt2_vs_ntt1_ratio':res['ntt2_27x27_separable']['median_ms']/res['ntt729_optimized_radix3_core']['median_ms']}
open('diazai_deep_benchmark_v2_results.json','w').write(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
