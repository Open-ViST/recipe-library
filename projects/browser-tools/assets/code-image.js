/* OpenViST Tools — MIT. Canvas rendering only; no code execution or network APIs. */
(function(){
 'use strict';
 const form=document.querySelector('[data-ovt-image]');if(!form)return;
 const find=s=>form.querySelector(s),code=find('#ovt-image-code'),canvas=find('canvas'),status=find('[data-image-status]'),result=find('[data-image-result]'),render=find('[data-image-render]'),download=find('[data-image-download]'),copy=find('[data-image-copy]');
 const themes={ocean:{top:'#eaf2ff',bottom:'#bdcff5',panel:'#142135',ink:'#edf4ff',muted:'#a7b8ce',line:'#2c3c52'},midnight:{top:'#142035',bottom:'#070d17',panel:'#172336',ink:'#f0f5fc',muted:'#a7b8ce',line:'#314059'},paper:{top:'#f3f1eb',bottom:'#e4e8ee',panel:'#ffffff',ink:'#172336',muted:'#58677b',line:'#e1e6ed'}};
 let url=null,blob=null,generation=0,busy=false;
 const message=(s,error=false)=>{status.textContent=s;status.classList.toggle('is-error',error)};
 function reset(){generation++;blob=null;result.hidden=true;if(url)URL.revokeObjectURL(url);url=null;download.removeAttribute('href');copy.hidden=true;canvas.width=1;canvas.height=1;}
 function invalidate(){reset();message('Settings changed. Create the image to update the preview.');}
 form.querySelectorAll('textarea,input,select').forEach(e=>e.addEventListener('input',invalidate));
 function rounded(ctx,x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
 find('[data-image-sample]').addEventListener('click',()=>{reset();code.value='fn main() {\n    let projects = ["Learn", "Build", "Share"];\n\n    for project in projects {\n        println!("{} with OpenViST", project);\n    }\n}';find('#ovt-image-title').value='hello.rs';message('Example loaded. Create your image when ready.');code.focus()});
 find('[data-image-clear]').addEventListener('click',()=>{reset();code.value='';find('#ovt-image-title').value='';message('Code and image cleared.');code.focus()});
 render.addEventListener('click',async()=>{
  if(busy)return;reset();const ticket=generation;busy=true;render.disabled=true;
  try{
   if(!code.value.trim())throw new Error('Paste some code or load the example first.');
   if(new TextEncoder().encode(code.value).length>20480)throw new Error('Code must be at most 20 KiB.');
   const lines=code.value.replace(/\r\n?/g,'\n').split('\n').map(s=>s.replace(/\t/g,'    '));
   if(lines.length>60)throw new Error('Use at most 60 lines, including a trailing blank line.');
   if(lines.some(s=>Array.from(s).length>140))throw new Error('Use at most 140 characters per line after expanding tabs.');
   if(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u202a-\u202e\u2066-\u2069]/.test(code.value))throw new Error('Remove control characters and bidirectional formatting controls before creating an image.');
   const font=Number(find('#ovt-image-font').value),scale=Number(find('#ovt-image-scale').value),theme=themes[find('#ovt-image-theme').value];
   if(![14,16,18,20].includes(font)||![1,2].includes(scale)||!theme)throw new Error('Choose valid image settings.');
   const title=find('#ovt-image-title').value;
   if(Array.from(title).length>80||/[\x00-\x1f\x7f\u202a-\u202e\u2066-\u2069]/.test(title))throw new Error('Use a title of at most 80 characters without control characters.');
   const ctx=canvas.getContext('2d');if(!ctx)throw new Error('Canvas is unavailable in this browser.');
   const family='ui-monospace, SFMono-Regular, Menlo, Consolas, monospace';
   ctx.font=font+'px '+family;
   const numbers=find('#ovt-image-lines').checked,gutter=numbers?44:0,pad=40,inner=28,lineHeight=font*1.55,signature=find('#ovt-image-brand').checked;
   const longest=Math.max(...lines.map(s=>ctx.measureText(s).width));
   ctx.font='600 14px system-ui, sans-serif';const titleWidth=ctx.measureText(title).width;
   const width=Math.ceil(Math.max(640,longest+2*pad+2*inner+gutter,titleWidth+2*pad+140));
   const height=Math.ceil(2*pad+76+lines.length*lineHeight+inner+(signature?34:0));
   if(width>1800||height>1800||width*height*scale*scale>13000000)throw new Error('Image is too large. Shorten long lines, reduce the font size or use a shorter example.');
   canvas.width=width*scale;canvas.height=height*scale;ctx.scale(scale,scale);
   const gradient=ctx.createLinearGradient(0,0,width,height);gradient.addColorStop(0,theme.top);gradient.addColorStop(1,theme.bottom);ctx.fillStyle=gradient;ctx.fillRect(0,0,width,height);
   ctx.shadowColor='rgba(8,20,45,.18)';ctx.shadowBlur=24;ctx.shadowOffsetY=12;ctx.fillStyle=theme.panel;rounded(ctx,pad,pad,width-2*pad,height-2*pad,14);ctx.fill();ctx.shadowColor='transparent';ctx.shadowBlur=0;ctx.shadowOffsetY=0;
   for(let i=0;i<3;i++){ctx.fillStyle=['#ff7a78','#eabd60','#64cfa1'][i];ctx.beginPath();ctx.arc(pad+24+i*17,pad+25,4.5,0,2*Math.PI);ctx.fill();}
   ctx.textBaseline='middle';ctx.textAlign='right';ctx.font='600 14px system-ui, sans-serif';ctx.fillStyle=theme.muted;ctx.fillText(title,width-pad-24,pad+25);
   ctx.strokeStyle=theme.line;ctx.beginPath();ctx.moveTo(pad+1,pad+51);ctx.lineTo(width-pad-1,pad+51);ctx.stroke();
   ctx.font=font+'px '+family;ctx.textBaseline='top';
   lines.forEach((line,i)=>{const y=pad+76+i*lineHeight;if(numbers){ctx.textAlign='right';ctx.fillStyle=theme.muted;ctx.fillText(String(i+1),pad+inner+gutter-16,y)}ctx.textAlign='left';ctx.fillStyle=theme.ink;ctx.fillText(line,pad+inner+gutter,y)});
   if(signature){ctx.textAlign='right';ctx.font='600 11px system-ui, sans-serif';ctx.fillStyle=theme.muted;ctx.fillText('OpenViST · Build something useful.',width-pad-inner,height-pad-25)}
   const png=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
   if(ticket!==generation)return;
   if(!png)throw new Error('PNG export is unavailable. Try a smaller image.');
   if(png.size>10*1024*1024)throw new Error('PNG exceeds 10 MiB. Choose a smaller example or 1× resolution.');
   blob=png;url=URL.createObjectURL(blob);download.href=url;result.hidden=false;copy.hidden=!(navigator.clipboard?.write&&typeof ClipboardItem==='function');message(canvas.width+' × '+canvas.height+' px PNG ready. Generated locally.');
  }catch(e){if(ticket===generation){reset();message(e.message||'Unable to create this image.',true)}}
  finally{busy=false;render.disabled=false;}
 });
 copy.addEventListener('click',async()=>{const current=blob,ticket=generation;if(!current)return;try{await navigator.clipboard.write([new ClipboardItem({'image/png':current})]);if(ticket===generation)message('Image copied.')}catch(_){if(ticket===generation)message('Image copying was blocked. Use Download PNG instead.',true)}});
 window.addEventListener('pagehide',reset);render.disabled=typeof canvas.getContext!=='function';
})();
