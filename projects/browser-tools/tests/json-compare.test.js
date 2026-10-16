const {test}=require('node:test');
const assert=require('node:assert/strict');
const core=require('../assets/tools-json-compare.js');
const compare=(input,second)=>JSON.parse(core.run({tool:'json-compare',input,second}).text);
test('Object order and string escape spelling do not create differences',()=>{
 assert.equal(compare('{"a":1,"b":"hello"}','{"b":"h\\u0065llo","a":1}').equal,true);
 assert.equal(compare('null','null').equal,true);
});
test('Added, removed, modified and missing versus null are distinct',()=>{
 const r=compare('{"gone":null,"v":1,"same":false}','{"new":null,"v":"1","same":false}');
 assert.deepEqual(r.counts,{added:1,removed:1,modified:1});
 assert.deepEqual(r.changes.find(x=>x.path==='/gone'),{path:'/gone',kind:'removed',before_json:'null'});
});
test('Large integers and exponent spellings are preserved without float conversion',()=>{
 const r=compare('{"n":9007199254740993,"z":-0,"exp":1e999999999999999}','{"n":9007199254740994,"z":0,"exp":2e999999999999999}');
 assert.equal(r.changes[0].before_json,'9007199254740993');assert.equal(r.changes[0].after_json,'9007199254740994');
 assert.equal(r.counts.modified,3);
 assert.equal(compare('1','1.0').equal,false);
});
test('JSON Pointer escapes keys and root replacements use empty path',()=>{
 const r=compare('{"a/b":{"~key":1},"":2,"__proto__":3}','{"a/b":{"~key":2},"":3,"__proto__":4}');
 assert.deepEqual(r.changes.map(c=>c.path),['/a~1b/~0key','/','/__proto__']);
 assert.equal(compare('[]','{}').changes[0].path,'');
 assert.equal({}.polluted,undefined);
});
test('Arrays compare by index and report removed or added tails',()=>{
 const r=compare('[1,2,3]','[1,4]');assert.deepEqual(r.counts,{added:0,removed:1,modified:1});
 assert.equal(r.changes[1].path,'/2');
 const added=compare('{}','{"x":{"n":9007199254740993}}');
 assert.equal(added.changes.length,1);assert.equal(added.changes[0].after_json,'{"n":9007199254740993}');
});
test('Duplicate keys, malformed JSON and nesting errors identify the input',()=>{
 assert.throws(()=>compare('{"a":1,"a":2}','{}'),/Before JSON: Duplicate/);
 assert.throws(()=>compare('{}','['),/After JSON:/);
 assert.throws(()=>compare('['.repeat(102)+'0'+']'.repeat(102),'null'),/100 levels/);
});
test('Input and change-count limits fail honestly without partial reports',()=>{
 assert.throws(()=>compare('"'+'a'.repeat(2097152)+'"','null'),/2 MiB/);
 assert.throws(()=>compare(JSON.stringify(Array(10001).fill(0)),JSON.stringify(Array(10001).fill(1))),/10,000 changes/);
});
test('Existing JSON formatting still works through dispatch',()=>{
 assert.match(core.run({tool:'json-validator',input:'{"a":9007199254740993}'}).text,/9007199254740993/);
});
