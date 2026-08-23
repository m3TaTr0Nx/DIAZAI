#!/usr/bin/env node
const FIBERS={F0:[0,3,6],F1:[1,4,7],F2_XYZ:[2,5,8]};
const disp=x=>{const r=((x%9)+9)%9;return r===0?9:r;};
function affineK(i,j,t){return disp(i+t*(j-i));}
function tailJ(i,k,a){return disp(i+a*(k-i));}
function affineTiling(ts){const M=Array.from({length:27},()=>Array(27).fill(0));for(let j=1;j<=9;j++)for(let i=1;i<=9;i++){const ks=ts.map(t=>affineK(i,j,t)).sort((a,b)=>a-b);const br=3*(j-1),bc=3*(i-1);ks.forEach((k,r)=>{M[br+r][bc]=i;M[br+r][bc+1]=j;M[br+r][bc+2]=k;});}return M;}
function tailTiling(){const M=Array.from({length:27},()=>Array(27).fill(0));for(let k=1;k<=9;k++)for(let i=1;i<=9;i++){const js=[0,3,6].map(a=>tailJ(i,k,a)).sort((a,b)=>a-b);const br=3*(k-1),bc=3*(i-1);js.forEach((j,r)=>{M[br+r][bc]=i;M[br+r][bc+1]=j;M[br+r][bc+2]=k;});}return M;}
function fourTilings(){return {F0:affineTiling(FIBERS.F0),F1:affineTiling(FIBERS.F1),F2_XYZ:affineTiling(FIBERS.F2_XYZ),Finf:tailTiling()};}
function z9Trits(x){const r=((x%9)+9)%9;return [Math.floor(r/3),r%3];}
function sixTrits(t){return t.flatMap(z9Trits);}
function decodeMask(mask){if(mask<0||mask>255)throw new Error('mask 0..255');return [...Array(8).keys()].filter(i=>(mask>>i)&1);}
const tools=[
{name:'diazai_four_tilings',description:'Generate the four exact 27x27 scalar tilings.',inputSchema:{type:'object',properties:{}}},
{name:'diazai_six_trit_encode',description:'Encode a Z9^3 triple into six F3 trits.',inputSchema:{type:'object',properties:{triple:{type:'array',items:{type:'integer'},minItems:3,maxItems:3}},required:['triple']}},
{name:'diazai_mask256_decode',description:'Decode an 8-bit GF9-oriented control mask.',inputSchema:{type:'object',properties:{mask:{type:'integer',minimum:0,maximum:255}},required:['mask']}}
];
function call(name,args){if(name==='diazai_four_tilings')return fourTilings();if(name==='diazai_six_trit_encode')return {triple:args.triple,six_trits:sixTrits(args.triple)};if(name==='diazai_mask256_decode')return {mask:args.mask,selected:decodeMask(args.mask)};throw new Error('unknown tool');}
let buf='';process.stdin.setEncoding('utf8');process.stdin.on('data',chunk=>{buf+=chunk;let p;while((p=buf.indexOf('\n'))>=0){const line=buf.slice(0,p).trim();buf=buf.slice(p+1);if(!line)continue;let req;try{req=JSON.parse(line);let result;if(req.method==='initialize')result={protocolVersion:req.params?.protocolVersion||'2025-03-26',capabilities:{tools:{}},serverInfo:{name:'diazai-paravox',version:'2.0.0'}};else if(req.method==='tools/list')result={tools};else if(req.method==='tools/call')result={content:[{type:'text',text:JSON.stringify(call(req.params.name,req.params.arguments||{}),null,2)}]};else throw new Error('method not found');process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:req.id,result})+'\n');}catch(e){process.stdout.write(JSON.stringify({jsonrpc:'2.0',id:req?.id??null,error:{code:-32000,message:e.message}})+'\n');}}});
