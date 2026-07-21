from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence
@dataclass(frozen=True)
class RBSFrame:
    length:int;bitmask:bytes;values:bytes;checksum:str
    def to_dict(self):return {"schema":"diazai.rbs.frame.v1","length":self.length,"bitmask_hex":self.bitmask.hex(),"values_hex":self.values.hex(),"checksum":self.checksum}
def encode(values:Sequence[int])->RBSFrame:
    if any(not 0<=int(v)<=8 for v in values):raise ValueError("exact integers 0..8 required")
    mask=bytearray((len(values)+7)//8);nz=bytearray()
    for i,v in enumerate(values):
        v=int(v)
        if v:mask[i//8]|=1<<(i%8);nz.append(v)
    body=len(values).to_bytes(4,"big")+bytes(mask)+bytes(nz)
    return RBSFrame(len(values),bytes(mask),bytes(nz),sha256(body).hexdigest())
def decode(frame:RBSFrame)->list[int]:
    body=frame.length.to_bytes(4,"big")+frame.bitmask+frame.values
    if sha256(body).hexdigest()!=frame.checksum:raise ValueError("checksum mismatch")
    out=[0]*frame.length;c=0
    for i in range(frame.length):
        if frame.bitmask[i//8]&(1<<(i%8)):
            if c>=len(frame.values):raise ValueError("truncated frame")
            out[i]=frame.values[c];c+=1
    if c!=len(frame.values):raise ValueError("trailing values")
    return out
