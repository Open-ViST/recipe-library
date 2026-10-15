const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('playwright-core');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 try{
  const page=await browser.newPage();
  const css=fs.readFileSync(path.join(__dirname,'../assets/pilot.css'),'utf8')+'\n'+fs.readFileSync(path.join(__dirname,'fixtures/recipe-actions.css'),'utf8');
  for(const width of [320,375,390,680,768,1280]){
   await page.setViewportSize({width,height:900});
   await page.setContent(`<style>*{box-sizing:border-box}body{margin:0}.ovr-shell{padding:20px}button{background:gold}button[hidden]{display:none}</style><style>${css}</style><body class="openvist-public-ui"><main class="ovla-shell"><div class="ov-share"><button>Share</button></div><section><button>Add website</button><button>Refresh status</button><button>Remove website and reports</button><a class="ovla-download">Download self-hosted tool (ZIP) ↓</a><button hidden>Hidden</button></section></main><main class="ovr-shell"><div class="ovr-code-head"><strong>Rust example</strong><button>Copy code</button><button>Download .rs</button></div></main></body>`);
   const actions=await page.locator('.ovla-shell section :is(button:not([hidden]),a)').evaluateAll(es=>es.map(e=>{let b=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:b.x,right:b.right,w:b.width,h:b.height,bg:s.backgroundColor,color:s.color}}));
   assert(actions.every(b=>b.w===actions[0].w&&b.h===56&&b.x>=0&&b.right<=width));
   assert(actions.every(b=>b.bg==='rgb(37, 99, 235)'&&b.color==='rgb(255, 255, 255)'));
   assert.equal(await page.locator('.ov-share button').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(255, 215, 0)');
   assert.equal(await page.locator('[hidden]').isVisible(),false);
   const recipe=await page.locator('.ovr-code-head>*').evaluateAll(es=>es.map(e=>{let b=e.getBoundingClientRect();return {x:b.x,y:b.y,w:b.width,h:b.height,right:b.right}}));
   assert.equal(recipe[1].w,recipe[2].w);assert.equal(recipe[1].y,recipe[2].y);assert.equal(recipe[1].h,48);
   assert(recipe.every(b=>b.x>=0&&b.right<=width));
   if(width<=680)assert(recipe[0].y+recipe[0].h<=recipe[1].y);
  }
  console.log('PASS consistent auditor actions, share isolation and recipe button alignment at 320–1280px');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
