import test from 'node:test';
import assert from 'node:assert/strict';
import * as c from '../src/core.mjs';
import * as m from '../src/mixed.mjs';
import * as a from '../src/adapter.mjs';
import { callTool, manifest, smoke } from '../src/registry.mjs';

test('729 codec roundtrip',()=>{for(let i=0;i<729;i++)assert.equal(c.encodeIndex(c.decodeIndex(i)),i);});
test('555 center in all charts',()=>{assert.deepEqual(c.fixedIChart([5,5,5]),[13,13]);assert.deepEqual(c.highLowChart([5,5,5]),[13,13]);assert.deepEqual(c.arithmeticChart([5,5,5]),[13,13]);});
test('chart bijections',()=>{for(const v of Object.values(c.verifyCharts()))assert.equal(v.bijective,true);});
test('strict union count',()=>assert.equal(c.strictUnion180().length,180));
test('BTMR32 roundtrip',()=>{const q=m.quantizeBTMR32(1.25);assert.equal(m.unpackBTMR32(q.hex).hex,q.hex);});
test('adapter removes secrets',()=>{const e=a.translateEvent({operation:'add_item',avatar_id:'abc',payload:{jwt_token:'x',item:'key'}});assert.equal(e.payload.jwt_token,'[REDACTED_SECRET]');assert.equal(e.state_index>=0&&e.state_index<729,true);});
test('all manifest tools execute',()=>{const result=smoke();assert.equal(result.failed,0,JSON.stringify(result.failures));assert.equal(result.tools_tested,manifest.count-2);});
test('known tool call',()=>assert.equal(callTool('state_encode_index',{triple:[5,5,5]}),364));
