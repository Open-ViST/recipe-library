const {test}=require('node:test');
const assert=require('node:assert/strict');
const {createHash,webcrypto}=require('node:crypto');
if(!globalThis.crypto)globalThis.crypto=webcrypto;
const {run}=require('../assets/tools-utilities.js');
test('Base64 standard, Unicode, BOM and binary bytes round trip',async()=>{
 for(const input of ['', 'f','fo','foo','OpenViST ✓','\ufeffhello']){
  const encoded=await run({tool:'base64',input,operation:'encode'});
  assert.equal(encoded.text,Buffer.from(input).toString('base64'));
  assert.equal((await run({tool:'base64',input:encoded.text,operation:'decode'})).text,input);
 }
 const bytes=Uint8Array.from([0,255,128,13,10]);
 const encoded=await run({tool:'base64',input:'',bytes,operation:'encode'});
 assert.deepEqual((await run({tool:'base64',input:encoded.text,operation:'decode',decoded:'binary'})).bytes,bytes);
 await assert.rejects(run({tool:'base64',input:encoded.text,operation:'decode'}),/UTF-8/);
});
test('Base64url and strict rejection of ambiguous spellings',async()=>{
 const bytes=Uint8Array.from([251,255]);
 assert.equal((await run({tool:'base64',input:'',bytes,operation:'encode',alphabet:'url'})).text,'-_8');
 assert.deepEqual((await run({tool:'base64',input:'-_8',operation:'decode',alphabet:'url',decoded:'binary'})).bytes,bytes);
 for(const input of ['Zg','Zg===','Zg==\n','Zh==','Z===','💣'])await assert.rejects(run({tool:'base64',input,operation:'decode'}));
 for(const input of ['Z','Zg==','++8','-_9'])await assert.rejects(run({tool:'base64',input,operation:'decode',alphabet:'url'}));
});
test('SHA-256 known vectors, exact file bytes, expected checksum validation',async()=>{
 for(const input of ['', 'abc','OpenViST ✓'])assert.equal((await run({tool:'sha256-checksum',input})).text,createHash('sha256').update(input).digest('hex'));
 const bytes=Uint8Array.from([239,187,191,13,10,0,255]);
 const hash=createHash('sha256').update(bytes).digest('hex');
 assert.equal((await run({tool:'sha256-checksum',input:'ignored',bytes,expected:hash.toUpperCase()})).summary,'Checksum matches.');
 assert.equal((await run({tool:'sha256-checksum',bytes,expected:'0'.repeat(64)})).summary,'Checksum does not match.');
 await assert.rejects(run({tool:'sha256-checksum',input:'',expected:'xyz'}),/64/);
});
test('URL components and ordered repeated query parameters have distinct plus semantics',async()=>{
 assert.equal((await run({tool:'url-encoder',input:'a + /✓',operation:'encode'})).text,'a%20%2B%20%2F%E2%9C%93');
 assert.equal((await run({tool:'url-encoder',input:'a+b%20c',operation:'decode'})).text,'a+b c');
 assert.deepEqual(JSON.parse((await run({tool:'url-encoder',input:'https://example.com/?a=1&a=2&space=a+b&__proto__=safe#ignored',operation:'parameters'})).text),[{name:'a',value:'1'},{name:'a',value:'2'},{name:'space',value:'a b'},{name:'__proto__',value:'safe'}]);
 for(const input of ['%','%GG','%FF'])for(const operation of ['decode','parameters'])await assert.rejects(run({tool:'url-encoder',input,operation}));
});
test('UTF-8 and binary size limits are enforced',async()=>{
 await assert.rejects(run({tool:'base64',input:'✓'.repeat(700000),operation:'encode'}),/2 MiB/);
 await assert.rejects(run({tool:'sha256-checksum',bytes:new Uint8Array(2097153)}),/2 MiB/);
 assert.equal((await run({tool:'base64',input:'',bytes:new Uint8Array(2097152),operation:'encode'})).text.length,2796204);
});
