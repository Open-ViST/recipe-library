'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {execFileSync} = require('node:child_process');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '..');
const tools = ['json-compare','base64','url-encoder','sha256-checksum','json-validator','csv-comparator','duplicate-finder','text-diff','csv-json-converter','sitemap-inspector'];
const server = http.createServer((req,res) => {
  const url = new URL(req.url,'http://localhost');
  if (url.pathname.startsWith('/assets/')) {
    const file=path.resolve(root,'.'+url.pathname);
    if (!file.startsWith(root+path.sep)||!fs.existsSync(file)) {res.writeHead(404);res.end();return;}
    res.setHeader('Content-Type',file.endsWith('.css')?'text/css':'application/javascript');res.end(fs.readFileSync(file));return;
  }
  const slug=url.pathname.slice(1)||'index';
  if (slug!=='index'&&!tools.includes(slug)&&slug!=='code-to-image') {res.writeHead(404);res.end();return;}
  const html=execFileSync('php',[path.join(__dirname,'integration.test.php'),'--render',slug],{encoding:'utf8'});
  res.setHeader('Content-Type','text/html; charset=utf-8');
  res.end('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="/assets/tools.css"><body>'+html+'<script>window.ovtConfig={worker:"/assets/tools-worker.js?ver=0.2.0"}</script><script src="/assets/sitemap-dom.js"></script><script src="/assets/tools-ui.js"></script><script src="/assets/code-image.js"></script></body></html>');
});

(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base='http://127.0.0.1:'+server.address().port;
  const launch={headless:true};if(process.env.CHROME_PATH)launch.executablePath=process.env.CHROME_PATH;
  const browser=await chromium.launch(launch);
  try {
    const context=await browser.newContext({acceptDownloads:true,permissions:['clipboard-read','clipboard-write']});
    const page=await context.newPage();const requests=[];const errors=[];
    page.on('request',r=>requests.push({url:r.url(),method:r.method()}));page.on('pageerror',e=>errors.push(e.message));
    for (const width of [1280,375]) {
      await page.setViewportSize({width,height:1000});
      for (const slug of tools) {
        await page.goto(base+'/'+slug);
        assert.equal(await page.locator('form').count(),0);
        await page.locator('[data-ovt-sample]').click();await page.locator('[data-ovt-run]').click();
        await page.locator('[data-ovt-result]').waitFor({state:'visible',timeout:10000});
        assert.equal(await page.locator('[data-ovt-status]').getAttribute('class'),'ovt-status');
        const output=await page.locator('#ovt-output').inputValue();assert.ok(output.length);
        if(slug==='json-compare')assert.deepEqual(JSON.parse(output).counts,{added:1,removed:1,modified:2});
        if(slug==='json-validator')assert.match(output,/9007199254740993/);
        if(slug==='csv-comparator')assert.equal(JSON.parse(output).modified.length,1);
        if(slug==='duplicate-finder')assert.equal(JSON.parse(output).conflicts.length,1);
        if(slug==='text-diff')assert.match(output,/- \[2:-\] status=draft/);
        if(slug==='csv-json-converter')assert.equal(JSON.parse(output)[0].id,'001');
        if(slug==='sitemap-inspector'){const report=JSON.parse(output);assert.equal(report.duplicate_urls.length,1);assert.ok(report.issues.some(x=>x.code==='invalid_lastmod'));}
        const downloadPromise=page.waitForEvent('download');await page.locator('[data-ovt-download]').click();const download=await downloadPromise;
        assert.equal(fs.readFileSync(await download.path(),'utf8'),output);
        assert.ok(download.suggestedFilename().endsWith(['text-diff','base64','url-encoder','sha256-checksum'].includes(slug)?'.txt':'.json'));
        await page.locator('[data-ovt-copy]').click();assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),output);
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow at '+slug+' '+width);
        await page.locator('.ovt-link-button').first().hover();
        assert.equal(await page.locator('.ovt-link-button').first().evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(37, 99, 235)');
        await page.locator('[data-ovt-clear]').click();assert.equal(await page.locator('#ovt-input').inputValue(),'');assert.equal(await page.locator('[data-ovt-result]').isVisible(),false);
        console.log('PASS browser example, download, copy, clear and layout:',slug,width);
      }
    }
    await page.goto(base+'/code-to-image');
    assert.equal(await page.locator('form').count(),0);
    await page.locator('[data-image-sample]').click();
    for(const width of [375,1280]){
      await page.setViewportSize({width,height:1000});
      for(const theme of ['ocean','midnight','paper']){
        await page.locator('#ovt-image-theme').selectOption(theme);
        await page.locator('[data-image-render]').click();await page.locator('[data-image-result]').waitFor({state:'visible'});
        const dimensions=await page.locator('canvas').evaluate(c=>({w:c.width,h:c.height}));
        assert(dimensions.w>=1280&&dimensions.h>200);
        const done=page.waitForEvent('download');await page.locator('[data-image-download]').click();const png=fs.readFileSync(await (await done).path());
        assert.equal(png.subarray(1,4).toString(),'PNG');assert.equal(png.readUInt32BE(16),dimensions.w);assert.equal(png.readUInt32BE(20),dimensions.h);
        assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Code image horizontal overflow');
      }
    }
    await page.locator('#ovt-image-scale').selectOption('1');await page.locator('[data-image-render]').click();await page.locator('[data-image-result]').waitFor({state:'visible'});
    const small=await page.locator('canvas').evaluate(c=>c.width);
    await page.locator('#ovt-image-scale').selectOption('2');assert.equal(await page.locator('[data-image-result]').isVisible(),false);
    await page.locator('[data-image-render]').click();await page.locator('[data-image-result]').waitFor({state:'visible'});assert.equal(await page.locator('canvas').evaluate(c=>c.width),small*2);
    await page.locator('#ovt-image-code').fill('</script><img src=x onerror=alert(1)>');await page.locator('[data-image-render]').click();await page.locator('[data-image-result]').waitFor({state:'visible'});assert.equal(await page.locator('[data-ovt-image] img').count(),0);
    for(const invalid of ['x'.repeat(141),Array(61).fill('x').join('\n'),'a\u202eb']){
      await page.locator('#ovt-image-code').fill(invalid);await page.locator('[data-image-render]').click();await page.locator('[data-image-status].is-error').waitFor();assert.equal(await page.locator('[data-image-result]').isVisible(),false);
    }
    await page.locator('[data-image-clear]').click();assert.equal(await page.locator('#ovt-image-code').inputValue(),'');
    console.log('PASS code image styles, PNG signatures and dimensions, 1x/2x, mobile layout, invalid input rejection and inert code.');
    await page.goto(base+'/json-compare');
    await page.locator('#ovt-input').fill('{"a":1,"b":2}');await page.locator('#ovt-second').fill('{"b":2,"a":1}');
    await page.locator('[data-ovt-run]').click();await page.locator('[data-ovt-result]').waitFor({state:'visible'});
    assert.equal(JSON.parse(await page.locator('#ovt-output').inputValue()).equal,true);
    await page.locator('#ovt-second').fill('{"a":1,"a":2}');await page.locator('[data-ovt-run]').click();await page.locator('.ovt-status.is-error').waitFor();assert.equal(await page.locator('[data-ovt-result]').isVisible(),false);
    for(const slug of ['base64','sha256-checksum']){
      await page.goto(base+'/'+slug);
      const bytes=Buffer.from([0,255,239,187,191,13,10]);
      await page.locator('#ovt-file').setInputFiles({name:'sample.bin',mimeType:'application/octet-stream',buffer:bytes});
      await page.waitForFunction(()=>!document.querySelector('[data-ovt-run]').disabled);
      await page.locator('[data-ovt-run]').click();await page.locator('[data-ovt-result]').waitFor({state:'visible'});
      const result=await page.locator('#ovt-output').inputValue();
      assert.equal(result,slug==='base64'?bytes.toString('base64'):require('node:crypto').createHash('sha256').update(bytes).digest('hex'));
      if(slug==='base64'){
        await page.locator('#ovt-operation').selectOption('decode');
        await page.locator('#ovt-decoded').selectOption('binary');await page.locator('#ovt-input').fill(result);
        await page.locator('[data-ovt-run]').click();await page.locator('[data-ovt-result]').waitFor({state:'visible'});
        const done=page.waitForEvent('download');await page.locator('[data-ovt-download]').click();assert.deepEqual(fs.readFileSync(await (await done).path()),bytes);
      }
    }
    await page.goto(base+'/url-encoder');await page.locator('#ovt-operation').selectOption('parameters');await page.locator('#ovt-input').fill('?a=1&a=2&x=a+b');await page.locator('[data-ovt-run]').click();await page.locator('[data-ovt-result]').waitFor({state:'visible'});
    assert.deepEqual(JSON.parse(await page.locator('#ovt-output').inputValue()),[{name:'a',value:'1'},{name:'a',value:'2'},{name:'x',value:'a b'}]);
    await page.goto(base+'/csv-json-converter');
    await page.locator('#ovt-direction').selectOption('json-csv');
    await page.locator('#ovt-input').fill('[{"id":9007199254740993123,"value":"=1+1"}]');
    await page.locator('[data-ovt-run]').click();await page.locator('[data-ovt-result]').waitFor({state:'visible'});
    const csv=await page.locator('#ovt-output').inputValue();assert.match(csv,/9007199254740993123,'=1\+1/);
    const csvPromise=page.waitForEvent('download');await page.locator('[data-ovt-download]').click();assert.match((await csvPromise).suggestedFilename(),/\.csv$/);
    await page.goto(base+'/sitemap-inspector');
    await page.locator('#ovt-file').setInputFiles({name:'sitemap.xml',mimeType:'application/xml',buffer:Buffer.from('<s:urlset xmlns:s="http://www.sitemaps.org/schemas/sitemap/0.9"><s:url><s:loc>https://example.com/?a=1&amp;b=2</s:loc></s:url></s:urlset>')});
    await page.waitForFunction(()=>!document.querySelector('[data-ovt-run]').disabled);await page.locator('[data-ovt-run]').click();await page.locator('[data-ovt-result]').waitFor({state:'visible'});
    assert.equal(JSON.parse(await page.locator('#ovt-output').inputValue()).entries[0].url,'https://example.com/?a=1&b=2');
    for(const xml of ['<urlset><url></urlset>','<!DOCTYPE urlset SYSTEM "https://example.com/test.dtd"><urlset/>']){
      await page.locator('#ovt-input').fill(xml);await page.locator('[data-ovt-run]').click();await page.locator('.ovt-status.is-error').waitFor();assert.equal(await page.locator('[data-ovt-result]').isVisible(),false);
    }
    await page.goto(base+'/json-validator');await page.locator('#ovt-input').fill('{"x":1,"x":2}');await page.locator('[data-ovt-run]').click();await page.locator('.ovt-status.is-error').waitFor();
    assert.equal(errors.length,0,'Browser errors: '+errors.join('; '));
    assert.ok(requests.every(r=>r.method==='GET'&&(r.url.startsWith(base+'/')||r.url.startsWith('blob:'+base+'/'))),'Unexpected request or data upload');
    console.log('PASS native XML parsing, invalid XML/DTD rejection, file input, conversion safety and no data-upload requests.');
  } finally {await browser.close();server.close();}
})().catch(error=>{console.error(error);server.close();process.exitCode=1;});
