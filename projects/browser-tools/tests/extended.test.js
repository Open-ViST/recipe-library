'use strict';
const test = require('node:test'), assert = require('node:assert/strict');
const core = require('../assets/tools-extended.js');
const diff = (input,second) => core.run({tool:'text-diff',input,second});
const convert = (input,direction,columns='',spreadsheetSafe=true) => core.run({tool:'csv-json-converter',input,direction,columns,spreadsheetSafe});
const entry = (url,date=[]) => ({locations:[url],lastmods:date,priorities:[],frequencies:[]});
const inspect = (entries, kind='urlset') => JSON.parse(core.run({tool:'sitemap-inspector',input:'<test/>',sitemap:{kind,entries,issues:[]}}).text);

test('Text Diff identifies removal, addition and unchanged lines with positions',()=>{
  const r=diff('a\nb\nc\n','a\nB\nc\nd\n');assert.match(r.summary,/2 added · 1 removed · 2 unchanged/);
  assert.match(r.text,/- \[2:-\] b/);assert.match(r.text,/\+ \[-:2\] B/);
});
test('Text Diff normalizes line separators and reports final newline separately',()=>{
  assert.match(diff('a\r\nb\r\n','a\nb\n').summary,/0 added · 0 removed · 2 unchanged/);
  assert.match(diff('a\n','a').text,/before: true; after: false/);
});
test('Text Diff handles empty files, repeated lines, spaces and Unicode',()=>{
  assert.match(diff('','').summary,/0 added · 0 removed · 0 unchanged/);
  assert.match(diff('x\nx','x').summary,/0 added · 1 removed · 1 unchanged/);
  assert.match(diff('é','e\u0301').summary,/1 added · 1 removed/);
  assert.match(diff('x ','x').summary,/1 added · 1 removed/);
});
test('Text Diff refuses excessive line counts',()=>assert.throws(()=>diff('x\n'.repeat(2001),''),/2,000/));
test('CSV to JSON preserves leading zeros, booleans as text and quoted cells',()=>{
  const rows=JSON.parse(convert('id,name,flag\n001,"a,b",true','csv-json').text);
  assert.deepEqual(rows,[{id:'001',name:'a,b',flag:'true'}]);
});
test('Converter selects literal fields using a JSON array',()=>{
  assert.deepEqual(JSON.parse(convert('a.b,"x,y"\n1,2','csv-json','["x,y"]').text),[{'x,y':'2'}]);
  assert.throws(()=>convert('id\n1','csv-json','["missing"]'),/missing/);
  for(const columns of ['["x","x"]','{"x":1}','[""]'])assert.throws(()=>convert('id\n1','csv-json',columns));
});
test('JSON to CSV retains exact numeric tokens and quotes separators',()=>{
  const r=convert('[{"id":900719925474099312345,"value":"a,b","n":-0,"e":1e400}]','json-csv');
  assert.equal(r.extension,'csv');assert.match(r.text,/900719925474099312345,"a,b",-0,1e400/);
});
test('JSON to CSV includes union columns and makes null or absent fields empty',()=>{
  assert.equal(convert('[{"a":"x","b":null},{"a":"y","c":true}]','json-csv').text,'a,b,c\r\nx,,\r\ny,,true\r\n');
});
test('Spreadsheet protection applies to strings and headers, not numeric tokens',()=>{
  const r=convert('[{"=header":" =1+1","n":-5}]','json-csv');assert.match(r.text,/^'=header,n/);assert.match(r.text,/' =1\+1,-5/);
  assert.match(convert('[{"a":"=1+1"}]','json-csv','',false).text,/\r\n=1\+1/);
});
test('Converter rejects nested selected values and malformed arrays',()=>{
  for(const input of ['{}','[null]','[1]','[{"x":{}}]','[{"x":[]}]'])assert.throws(()=>convert(input,'json-csv'));
  assert.equal(convert('[]','json-csv','["id"]').text,'id\r\n');
});
test('Ignored nested fields and prototype-like column names do not modify prototypes',()=>{
  const r=convert('[{"__proto__":"safe","ignored":{}}]','json-csv','["__proto__"]');
  assert.equal(r.text,'__proto__\r\nsafe\r\n');assert.equal({}.safe,undefined);
});
test('Sitemap checks duplicates, date validity and absolute URL syntax',()=>{
  const r=inspect([entry('https://example.com/',['2026-02-31']),entry('https://EXAMPLE.com/'),entry('/relative'),entry('https:example.com'),entry('https://example.com/%zz')]);
  assert.equal(r.duplicate_urls.length,1);assert.deepEqual(r.duplicate_urls[0].positions,[1,2]);
  assert.ok(r.issues.some(x=>x.code==='invalid_lastmod'));assert.equal(r.issues.filter(x=>x.code==='invalid_http_url').length,3);
});
test('Sitemap accepts leap days and timezone timestamps, rejects malformed dates',()=>{
  for(const date of ['2024-02-29','2026-10-15T12:30:00Z','2026-10-15T12:30:00.123+02:00'])assert.equal(inspect([entry('https://example.com/',[date])]).issues.length,0);
  for(const date of ['2026-02-29','0000-01-01','2026-01-01T25:00:00Z','2026-01-01T00:00:00+99:00'])assert.ok(inspect([entry('https://example.com/',[date])]).issues.some(x=>x.code==='invalid_lastmod'));
});
test('Sitemap validates optional priority and frequency fields',()=>{
  const e=entry('https://example.com/');e.priorities=['1.1'];e.frequencies=['often'];
  const r=inspect([e]);assert.ok(r.issues.some(x=>x.code==='invalid_priority'));assert.ok(r.issues.some(x=>x.code==='invalid_changefreq'));
});
test('Sitemap index reports entries without crawling, and rejects credentials',()=>{
  const r=inspect([entry('https://example.com/part.xml'),entry('https://user:secret@example.com/x')],'sitemapindex');
  assert.equal(r.kind,'sitemapindex');assert.equal(r.unique_http_urls,1);assert.match(r.scope,/No URLs were requested/);
});
test('Existing tools still run through the extended dispatcher',()=>{
  assert.match(core.run({tool:'json-validator',input:'{"x":1}'}).text,/"x": 1/);
});
