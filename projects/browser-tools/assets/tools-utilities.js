/* OpenViST Tools — MIT. Local encoding and checksums; no network APIs. */
(function(root){
 'use strict';
 const limit=2*1024*1024;
 const fail=m=>{throw new Error(m)};
 const text=t=>{if(typeof t!=='string'||new TextEncoder().encode(t).length>limit)fail('Input must be at most 2 MiB.');return t;};
 const plain=(value,summary)=>({text:value,summary,extension:'txt',mime:'text/plain;charset=utf-8'});
 async function run(task){
  const input=text(task.input??'');
  if(task.tool==='url-encoder'){
   if(task.operation==='parameters'){
    let query=input;
    if(/^https?:\/\//i.test(input)){try{query=new URL(input).search.slice(1)}catch(_){fail('Enter a valid HTTP(S) URL or a query string.')}}
    else {if(query.startsWith('?'))query=query.slice(1);query=query.split('#')[0]}
    // Validate before URLSearchParams, which otherwise replaces malformed UTF-8 silently.
    try{decodeURIComponent(query.replace(/\+/g,' '))}catch(_){fail('Invalid percent encoding or UTF-8 in the query string.')}
    const entries=[];for(const [name,value] of new URLSearchParams(query)){if(entries.length===20000)fail('Query inspection accepts at most 20,000 parameters.');entries.push({name,value});}
    return {text:JSON.stringify(entries,null,2),summary:entries.length+' parameters; repeated names and order preserved.',extension:'json',mime:'application/json;charset=utf-8'};
   }
   if(task.operation==='encode')return plain(encodeURIComponent(input),'Encoded as one URL component. Spaces become %20.');
   if(task.operation==='decode'){try{return plain(decodeURIComponent(input),'Decoded one URL component. A literal + remains +.')}catch(_){fail('Invalid percent encoding or UTF-8.')}}
   fail('Choose an encoding operation.');
  }
  let bytes=task.bytes instanceof Uint8Array?task.bytes:new TextEncoder().encode(input);
  if(bytes.length>limit)fail('Each input file must be at most 2 MiB.');
  if(task.tool==='sha256-checksum'){
   const expected=(task.expected??'').trim();
   if(expected&&!/^[a-f0-9]{64}$/i.test(expected))fail('Expected checksum must contain exactly 64 hexadecimal characters.');
   if(!root.crypto?.subtle)fail('SHA-256 requires a browser with Web Crypto on HTTPS.');
   const digest=Array.from(new Uint8Array(await root.crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');
   return plain(digest,expected?(digest===expected.toLowerCase()?'Checksum matches.':'Checksum does not match.'):'SHA-256 calculated from '+bytes.length+' bytes. A checksum alone does not establish authenticity.');
  }
  if(task.tool==='base64'){
   if(task.operation==='encode'){
    let raw='';for(let i=0;i<bytes.length;i+=8192)raw+=String.fromCharCode(...bytes.subarray(i,i+8192));
    let encoded=btoa(raw);
    if(task.alphabet==='url')encoded=encoded.replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
    return plain(encoded,'Encoded '+bytes.length+' bytes. Base64 is encoding, not encryption.');
   }
   if(task.operation!=='decode')fail('Choose encode or decode.');
   let value=input;
   if(task.alphabet==='url'){
    if(!/^[A-Za-z0-9_-]*$/.test(value)||value.length%4===1)fail('Use unpadded Base64url without whitespace.');
    value=value.replace(/-/g,'+').replace(/_/g,'/');value+='='.repeat((4-value.length%4)%4);
   }else if(!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(value))fail('Use standard padded Base64 without whitespace.');
   const raw=atob(value);
   if(btoa(raw)!==value)fail('Noncanonical Base64: unused padding bits must be zero.');
   bytes=Uint8Array.from(raw,c=>c.charCodeAt(0));
   if(task.decoded==='binary')return {text:'Decoded '+bytes.length+' bytes. Download BIN to save the original bytes.',summary:'Binary output is not executed or rendered.',bytes,extension:'bin',mime:'application/octet-stream'};
   try{return plain(new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(bytes),'Decoded '+bytes.length+' bytes as strict UTF-8.')}catch(_){fail('Decoded bytes are not valid UTF-8. Choose binary output to download them.');}
  }
  fail('Unknown utility.');
 }
 const api={run};if(typeof module==='object'&&module.exports)module.exports=api;else root.OpenViSTUtilities=api;
})(typeof globalThis!=='undefined'?globalThis:this);
