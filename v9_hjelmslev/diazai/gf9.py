"""GF(9)=F3[alpha]/(alpha^2+1), pair (a,b)=a*alpha+b."""
ZERO=(0,0); ONE=(0,1)

def add(x,y):
    return ((x[0]+y[0])%3,(x[1]+y[1])%3)

def mul(x,y):
    a,b=x; c,d=y
    return ((a*d+b*c)%3,(b*d+2*a*c)%3)

def pow_(x,n):
    y=ONE
    while n:
        if n&1:y=mul(y,x)
        x=mul(x,x); n//=2
    return y

def inv(x):
    if x==ZERO: raise ZeroDivisionError
    return pow_(x,7)

def primitive_cycle(g=(1,1)):
    out=[]; x=ONE
    for _ in range(8):
        x=mul(x,g); out.append(x)
    if len(set(out))!=8 or out[-1]!=ONE:
        raise ValueError("not primitive")
    return out

def projective_direction(v):
    a,b=v
    if a%3:
        inva=1 if a%3==1 else 2
        return (1,(b*inva)%3)
    if b%3:
        return (0,1)
    raise ValueError("zero vector has no projective direction")
