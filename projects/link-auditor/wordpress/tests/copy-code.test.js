'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const script=fs.readFileSync(path.join(__dirname,'../assets/copy-code.js'),'utf8');
const text='mkdir -p ~/openvist-tools\npython3 run_audit.py --deadline 600 -- https://example.com/ \\\n  --max-pages 200 --max-urls 1000';
function fixture(clipboard,copyResult=true){const status={textContent:''};let handler,copied,removed=false;const button={dataset:{ovlaCopy:'code'},hidden:true,textContent:'Copy code',disabled:false,parentElement:{querySelector:()=>status},addEventListener:(_,fn)=>handler=fn,focus(){}};const area={value:'',style:{},setAttribute(){},select(){copied=this.value;},remove(){removed=true;}};const context={document:{querySelectorAll:()=>[button],getElementById:()=>({textContent:text}),createElement:()=>area,body:{append(){}},execCommand:command=>{assert.equal(command,'copy');return copyResult;}},navigator:{clipboard},setTimeout:()=>1,clearTimeout(){}};vm.runInNewContext(script,context);return {button,status,click:()=>handler(),copied:()=>copied,removed:()=>removed};}
(async()=>{
 let copied;const normal=fixture({writeText:async value=>{copied=value;}});assert.equal(normal.button.hidden,false);await normal.click();assert.equal(copied,text);assert.equal(normal.button.textContent,'Copied!');assert.equal(normal.button.disabled,false);
 const denied=fixture({writeText:async()=>{throw new Error('Denied');}});await denied.click();assert.match(denied.status.textContent,/Could not copy/);assert.equal(denied.button.textContent,'Copy code');assert.equal(denied.button.disabled,false);
 const fallback=fixture(undefined);await fallback.click();assert.equal(fallback.copied(),text);assert.equal(fallback.removed(),true);assert.equal(fallback.button.textContent,'Copied!');
 const failed=fixture(undefined,false);await failed.click();assert.match(failed.status.textContent,/manually/);assert.equal(failed.removed(),true);
 console.log('PASS exact multiline clipboard text, success feedback, permission denial and fallback cleanup');
})().catch(e=>{console.error(e);process.exitCode=1;});
