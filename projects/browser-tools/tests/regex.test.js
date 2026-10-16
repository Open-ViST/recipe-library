const {test}=require('node:test'),assert=require('node:assert/strict');
const core=require('../assets/tools-regex.js');
const run=(pattern,input,flags='g')=>core.run({tool:'regex-tester',pattern,input,flags});
test('Named and numbered captures, unmatched groups, positions and flags',()=>{
 const r=run('(?<name>[A-Z]+)([0-9]+)?','ABC12 DEF','g');
 assert.deepEqual(r.matches[0],{index:0,end:5,text:'ABC12',captures:['ABC','12'],named_groups:{name:'ABC'}});
 assert.equal(r.matches[1].captures[1],null);
 assert.equal(run('abc','ABC abc','i').matches.length,1);
 assert.equal(run('^b','a\nb','gm').matches[0].index,2);
 assert.equal(run('a.b','a\nb','s').matches.length,1);
});
test('Empty matches advance over Unicode code points when u is set',()=>{
 assert.deepEqual(run('','😀','gu').matches.map(m=>m.index),[0,2]);
 assert.deepEqual(run('','😀','g').matches.map(m=>m.index),[0,1,2]);
 assert.equal(run('$','abc').matches[0].index,3);
 assert.equal(run('','').matches.length,1);
});
test('Sticky and non-global modes follow JavaScript semantics',()=>{
 assert.equal(run('b','abc','y').matches.length,0);
 assert.equal(run('a','aa','y').matches.length,1);
 assert.equal(run('a','aaa','g').matches.length,3);
});
test('Invalid patterns, flags and bounds fail instead of partial reports',()=>{
 assert.throws(()=>run('(','abc'),/JavaScript regex error/);
 for(const f of ['gg','v','d','x'])assert.throws(()=>run('a','a',f),/flag/);
 assert.throws(()=>run('a'.repeat(4097),'a'),/4 KiB/);
 assert.throws(()=>run('a','a'.repeat(262145)),/256 KiB/);
 assert.throws(()=>run('','a'.repeat(1001)),/1,000 matches/);
 assert.throws(()=>run('()'.repeat(201),''),/200 capture/);
});
test('Match text is returned literally and never evaluated',()=>{
 const r=run('.+','<img src=x onerror=alert(1)>');assert.equal(r.matches[0].text,'<img src=x onerror=alert(1)>');
 assert.equal(JSON.parse(r.text).engine,'JavaScript RegExp in your browser');
});
