P1_FAMILIES=[("F0_P[1:0]",(1,0)),("F1_P[1:1]",(1,1)),("F2_X",(1,2)),("P[1:3]",(1,3)),("P[1:4]",(1,4)),("F2_Y",(1,5)),("P[1:6]",(1,6)),("P[1:7]",(1,7)),("F2_Z",(1,8)),("Finf_P[0:1]",(0,1)),("P[3:1]",(3,1)),("P[6:1]",(6,1))]
SCOPE={0:"LOCAL_GPU",1:"NODE",2:"RACK",3:"GLOBAL_CLUSTER"}

def addr729(i,j,k):
    if not(0<=i<9 and 0<=j<9 and 0<=k<9): raise ValueError("Z9 coordinate")
    return i*81+j*9+k

def unaddr729(a):
    if not 0<=a<729: raise ValueError("addr729")
    i,r=divmod(a,81); j,k=divmod(r,9); return i,j,k

def pack_word(mask8,family12,addr,scope2):
    if not 0<=mask8<=255: raise ValueError("mask8")
    if not 0<=family12<=0xFFF: raise ValueError("family12")
    if not 0<=addr<=728: raise ValueError("addr729")
    if not 0<=scope2<=3: raise ValueError("scope2")
    return (scope2<<30)|(addr<<20)|(family12<<8)|mask8

def unpack_word(word):
    word&=0xFFFFFFFF; a=(word>>20)&0x3FF
    if a>728: raise ValueError("reserved addr729")
    return {"mask8":word&0xFF,"family12":(word>>8)&0xFFF,"addr729":a,"scope2":(word>>30)&3}
