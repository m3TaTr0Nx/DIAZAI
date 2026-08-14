N=729
count=0
for s in range(6):
    span=3**s
    m=span*3
    step=N//m
    for g in range(N//m):
        base=g*m
        for j in range(span):
            a=base+j; b=a+span; c=b+span
            e1=(j*step)%N; e2=(2*e1)%N
            assert 0<=a<b<c<N
            assert 0<=e1<N and 0<=e2<N
            count+=1
assert count==1458
print('PASS golden schedule:', count, 'butterflies')
