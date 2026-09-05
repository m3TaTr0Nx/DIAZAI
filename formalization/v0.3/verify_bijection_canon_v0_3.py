#!/usr/bin/env python3
P=58321
G=11

def order(a,p):
    x=1
    for n in range(1,p):
        x=x*a%p
        if x==1:return n

for K in (60,180,360):
    w=pow(G,(P-1)//K,P)
    assert order(w,P)==K
    assert pow(w,K,P)==1
    if K%2==0:
        assert pow(w,K//2,P)==P-1
    print(K, w, 'order', order(w,P), 'half-turn', pow(w,K//2,P))

for K in (180,360):
    for d in range(1,7):
        assert K%d==0
        assert (3**d)**(K//d)==3**K

print('PASS: mixed-radix cardinalities, exact finite-field roots, and half-turn sign.')
