/* OpenViST Tools — MIT. Structural JSON comparison, without numeric rounding. */
(function(root){
 'use strict';
 const core=typeof module==='object'&&module.exports?require('./tools-core.js'):root.OpenViSTTools;
 const previous=core.run;
 class Numeric {constructor(raw){this.raw=raw}}
 const kind=v=>v instanceof Numeric?'number':v===null?'null':Array.isArray(v)?'array':typeof v;
 function source(v){
  if(v instanceof Numeric)return v.raw;
  if(Array.isArray(v))return '['+v.map(source).join(',')+']';
  if(v!==null&&typeof v==='object')return '{'+Object.keys(v).map(k=>JSON.stringify(k)+':'+source(v[k])).join(',')+'}';
  return JSON.stringify(v);
 }
 function compare(before,after){
  let a,b;
  try{a=core.json(before,n=>new Numeric(n)).data}catch(e){throw new Error('Before JSON: '+e.message)}
  try{b=core.json(after,n=>new Numeric(n)).data}catch(e){throw new Error('After JSON: '+e.message)}
  const changes=[],counts={added:0,removed:0,modified:0};let bytes=0;
  const escape=k=>String(k).replace(/~/g,'~0').replace(/\//g,'~1');
  function change(path,operation,left,right){
   if(changes.length===10000)throw new Error('More than 10,000 changes. Compare smaller documents.');
   const entry={path,kind:operation};
   if(operation!=='added')entry.before_json=source(left);
   if(operation!=='removed')entry.after_json=source(right);
   bytes+=new TextEncoder().encode(JSON.stringify(entry)).length+64;
   if(bytes>5*1024*1024)throw new Error('Result exceeds 5 MiB. Compare smaller documents.');
   changes.push(entry);counts[operation]++;
  }
  function visit(left,right,path){
   const type=kind(left);
   if(type!==kind(right)){change(path,'modified',left,right);return}
   if(type==='object'){
    for(const key of Object.keys(left)){
     const p=path+'/'+escape(key);
     if(!Object.hasOwn(right,key))change(p,'removed',left[key]);else visit(left[key],right[key],p);
    }
    for(const key of Object.keys(right))if(!Object.hasOwn(left,key))change(path+'/'+escape(key),'added',undefined,right[key]);
   }else if(type==='array'){
    const common=Math.min(left.length,right.length);
    for(let i=0;i<common;i++)visit(left[i],right[i],path+'/'+i);
    for(let i=common;i<left.length;i++)change(path+'/'+i,'removed',left[i]);
    for(let i=common;i<right.length;i++)change(path+'/'+i,'added',undefined,right[i]);
   }else if(type==='number'?left.raw!==right.raw:left!==right)change(path,'modified',left,right);
  }
  visit(a,b,'');
  const report={equal:changes.length===0,counts,changes,scope:'Object key order is ignored. Arrays are compared by zero-based index. Number spellings are compared exactly (1 and 1.0 differ); strings are compared after JSON unescaping. Paths use JSON Pointer; an empty path denotes the root. before_json and after_json are JSON source strings, preserving numeric tokens. This report is not a JSON Patch.'};
  const text=JSON.stringify(report,null,2)+'\n';
  if(new TextEncoder().encode(text).length>5*1024*1024)throw new Error('Result exceeds 5 MiB. Compare smaller documents.');
  return {text,summary:report.equal?'JSON documents match under the stated comparison rules.':counts.added+' added · '+counts.removed+' removed · '+counts.modified+' modified.',extension:'json',mime:'application/json;charset=utf-8'};
 }
 core.run=task=>task.tool==='json-compare'?compare(task.input,task.second):previous(task);
 if(typeof module==='object'&&module.exports)module.exports=core;
})(typeof self==='object'?self:globalThis);
