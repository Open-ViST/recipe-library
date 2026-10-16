/* OpenViST Tools — MIT. Invoke only inside a terminable Worker in the browser. */
(function(root){
 'use strict';
 const core=typeof module==='object'&&module.exports?require('./tools-core.js'):root.OpenViSTTools,previous=core.run;
 function run(task){
  if(typeof task.input!=='string'||new TextEncoder().encode(task.input).length>262144)throw new Error('Regex text must be at most 256 KiB.');
  if(typeof task.pattern!=='string'||new TextEncoder().encode(task.pattern).length>4096)throw new Error('Pattern must be at most 4 KiB. Enter it without / delimiters.');
  const flags=task.flags??'';
  if(typeof flags!=='string'||!/^[gimsuy]*$/.test(flags)||new Set(flags).size!==flags.length)throw new Error('Use each supported flag at most once: g, i, m, s, u, y.');
  let regex;try{regex=new RegExp(task.pattern,flags)}catch(e){throw new Error('JavaScript regex error: '+e.message)}
  const matches=[];let m,budget=0;
  while((m=regex.exec(task.input))!==null){
   if(matches.length===1000)throw new Error('More than 1,000 matches. Narrow your pattern or use a shorter text.');
   if(m.length>201)throw new Error('At most 200 capture groups are supported.');
   const item={index:m.index,end:m.index+m[0].length,text:m[0],captures:Array.from(m).slice(1).map(v=>v===undefined?null:v),named_groups:m.groups?Object.fromEntries(Object.entries(m.groups).map(([k,v])=>[k,v===undefined?null:v])):null};
   budget+=new TextEncoder().encode(JSON.stringify(item)).length+128;
   if(budget>5*1024*1024)throw new Error('Regex result exceeds 5 MiB. Use a shorter text or fewer captures.');
   matches.push(item);
   if(!regex.global)break;
   if(m[0]===''){
    const i=regex.lastIndex;
    regex.lastIndex=i+(regex.unicode&&i<task.input.length&&task.input.codePointAt(i)>0xffff?2:1);
   }
  }
  const report={engine:'JavaScript RegExp in your browser',pattern:task.pattern,flags,matches,scope:'Indices are zero-based UTF-16 code units; end is exclusive. Captures are numbered from 1; null means an unmatched group. Without g, only the first match is returned. Sticky y requires a match at the current lastIndex. This is not the Python, PHP or Rust engine.'};
  const text=JSON.stringify(report,null,2)+'\n';
  if(new TextEncoder().encode(text).length>5*1024*1024)throw new Error('Regex result exceeds 5 MiB.');
  return {text,matches,summary:matches.length+' match'+(matches.length===1?'':'es')+' · JavaScript engine · UTF-16 positions.',extension:'json',mime:'application/json;charset=utf-8'};
 }
 core.run=task=>task.tool==='regex-tester'?run(task):previous(task);
 if(typeof module==='object'&&module.exports)module.exports=core;
})(typeof self==='object'?self:globalThis);
