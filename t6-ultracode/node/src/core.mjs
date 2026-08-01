import crypto from 'node:crypto';

export const SLOPES = { X: 2, Y: 5, Z: 8 };
export const PERMUTATIONS = [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];

export function residue(d){ const x=Number(d); if(x<1||x>9) throw new Error('digit 1..9 required'); return x%9; }
export function display(r){ const x=((Number(r)%9)+9)%9; return x===0?9:x; }
export function validateTriple(t){ if(!Array.isArray(t)||t.length!==3) throw new Error('triple length 3 required'); const x=t.map(Number); if(x.some(v=>v<1||v>9||!Number.isInteger(v))) throw new Error('digits 1..9 required'); return x; }
export const z9Add=(a,b)=>display(residue(a)+residue(b));
export const z9Sub=(a,b)=>display(residue(a)-residue(b));
export const z9Neg=a=>display(-residue(a));
export const z9Mul=(a,b)=>display(residue(a)*residue(b));
export function z9Inv(a){ const r=residue(a); for(const x of [1,2,4,5,7,8]) if((r*x)%9===1) return display(x); throw new Error('not a unit'); }
export function toricAdd(t,v){ const x=validateTriple(t); if(!Array.isArray(v)||v.length!==3) throw new Error('vector length3'); return x.map((d,i)=>display(residue(d)+Number(v[i]))); }
export const complement=t=>validateTriple(t).map(z9Neg);
export function encodeIndex(t){ const [i,j,k]=validateTriple(t); return (i-1)*81+(j-1)*9+(k-1); }
export function decodeIndex(i){ const n=Number(i); if(n<0||n>=729||!Number.isInteger(n)) throw new Error('index 0..728'); return [Math.floor(n/81)+1,Math.floor(n/9)%9+1,n%9+1]; }
export function splitSixTrits(t){ return validateTriple(t).flatMap(d=>[Math.floor((d-1)/3),(d-1)%3]); }
export function joinSixTrits(trits){ if(!Array.isArray(trits)||trits.length!==6||trits.some(x=>![0,1,2].includes(Number(x)))) throw new Error('six trits required'); return [0,2,4].map(n=>3*Number(trits[n])+Number(trits[n+1])+1); }
export function equalityClass(t){ return ['','diagonal','exactly_two_equal','all_distinct'][new Set(validateTriple(t)).size]; }
export function fixedIChart(t){ const [i,j,k]=validateTriple(t); const [i1,i0]=[Math.floor((i-1)/3),(i-1)%3]; const [j1,j0]=[Math.floor((j-1)/3),(j-1)%3]; const [k1,k0]=[Math.floor((k-1)/3),(k-1)%3]; return [9*i1+3*i0+j1,9*j0+3*k1+k0]; }
export function highLowChart(t){ const x=splitSixTrits(t); return [9*x[0]+3*x[2]+x[4],9*x[1]+3*x[3]+x[5]]; }
export const arithmeticChart=t=>{const n=encodeIndex(t);return [Math.floor(n/27),n%27];};
export function chartInverse(row,col,chart='fixed_i'){ const r=Number(row),c=Number(col); if(r<0||r>26||c<0||c>26)throw new Error('row/col 0..26'); if(chart==='arithmetic')return decodeIndex(r*27+c); if(chart==='high_low'){const h0=Math.floor(r/9),rem=r%9,h1=Math.floor(rem/3),h2=rem%3,l0=Math.floor(c/9),rem2=c%9,l1=Math.floor(rem2/3),l2=rem2%3;return joinSixTrits([h0,l0,h1,l1,h2,l2]);} if(chart==='fixed_i'){const i1=Math.floor(r/9),rem=r%9,i0=Math.floor(rem/3),j1=rem%3,j0=Math.floor(c/9),rem2=c%9,k1=Math.floor(rem2/3),k0=rem2%3;return joinSixTrits([i1,i0,j1,j0,k1,k0]);} throw new Error('unknown chart'); }
export function superplanePhase(t,f){ const [i,j,k]=validateTriple(t).map(residue); const m=SLOPES[String(f).toUpperCase()]; if(!m)throw new Error('family X/Y/Z'); return ((k-i-m*(j-i))%9+9)%9; }
export function superplaneGenerate(f,phase=0){ const m=SLOPES[String(f).toUpperCase()]; if(!m)throw new Error('family X/Y/Z'); const q=((Number(phase)%9)+9)%9; const out=[]; for(let i=0;i<9;i++)for(let t=0;t<9;t++)out.push([display(i),display(i+t),display(i+m*t+q)]); return out; }
export function strictUnion180(){ const map=new Map(); for(const f of ['X','Y','Z'])for(const t of superplaneGenerate(f,0))map.set(t.join(','),t); return [...map.values()].filter(t=>new Set(t).size===3).sort((a,b)=>encodeIndex(a)-encodeIndex(b)); }
export function torusAngles(t){ return validateTriple(t).map(d=>2*Math.PI*residue(d)/9); }
export function torusEmbed(t){ return torusAngles(t).map(a=>[Math.cos(a),Math.sin(a)]); }
export function character(t,freq){ const x=validateTriple(t).map(residue); const e=x.reduce((s,v,i)=>s+v*Number(freq[i]),0)%9; const a=2*Math.PI*e/9; return {real:Math.cos(a),imag:Math.sin(a),magnitude:1,phase:a}; }
export function digitwiseFold(t){const x=validateTriple(t),c=complement(x);return {original:x,complement:c,paired:`${x.join('')}:${c.join('')}`,residue_sums:x.map((v,i)=>(residue(v)+residue(c[i]))%9)};}
function sortObject(v){ if(Array.isArray(v))return v.map(sortObject); if(v&&typeof v==='object')return Object.fromEntries(Object.keys(v).sort().map(k=>[k,sortObject(v[k])])); return v; }
export function canonicalJson(v){ return JSON.stringify(sortObject(v)); }
export function canonicalHash(v){return crypto.createHash('sha256').update(canonicalJson(v)).digest('hex');}
export function describeState(t){ const x=validateTriple(t); return {triple:x,index:encodeIndex(x),six_trits:splitSixTrits(x),equality_class:equalityClass(x),charts:{fixed_i:fixedIChart(x),high_low:highLowChart(x),arithmetic:arithmeticChart(x)},phases:Object.fromEntries(['X','Y','Z'].map(f=>[f,superplanePhase(x,f)])),angles:torusAngles(x)}; }
export function verifyCharts(){ const result={}; for(const [name,fn] of Object.entries({fixed_i:fixedIChart,high_low:highLowChart,arithmetic:arithmeticChart})){const s=new Set();for(let i=0;i<729;i++)s.add(fn(decodeIndex(i)).join(','));result[name]={count:s.size,bijective:s.size===729,center_555:fn([5,5,5])};}return result;}
