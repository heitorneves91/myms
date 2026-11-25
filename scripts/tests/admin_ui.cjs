// Optional browser check: NODE_PATH=<temporary npm prefix>/node_modules node scripts/tests/admin_ui.cjs
// Needs playwright-core and a local Chrome/Chromium. Uses the real embedded HTML with mocked APIs.
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const root = path.resolve(__dirname, '../..');
const source = fs.readFileSync(path.join(root,'firmware/include/web_ui.h'),'utf8');
const html = source.split('R"MYMSHTML(')[1].split(')MYMSHTML"')[0];
const status = {
 version:'0.1.0',device_id:'preview-only',simulation:true,outputs_enabled:false,control_enabled:true,
 uptime_s:1320,reset_reason:1,free_heap:180000,flash_bytes:4194304,ap_ssid:'MYMS-preview',ap_ip:'192.168.4.1',
 wifi_connected:false,wifi_ip:'0.0.0.0',utc_s:null,state:'idle',fault:'',air_c:24.5,wall_c:24.2,sensors_fresh:true,
 sensor_age_ms:20,air_rom:'2800000000000001',wall_rom:'2800000000000002',target_c:45,remaining_s:0,heater:false,fan:false,
 sensors:[{rom:'2800000000000001',temperature_c:24.5},{rom:'2800000000000002',temperature_c:24.2}],
 recording:{active:false,file:'',rows:0,error:'',interval_s:5,remaining_s:0,fs_ready:true,used_bytes:0,total_bytes:2031616}
};
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--no-sandbox']});
 try {
  const page=await browser.newPage({viewport:{width:1100,height:900}}),errors=[],requests=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.route('http://myms.test/**',async route=>{
   const req=route.request(),url=new URL(req.url()),payload=req.postDataJSON();
   if(url.pathname==='/')return route.fulfill({contentType:'text/html',body:html});
   requests.push({path:url.pathname,body:payload,headers:req.headers()});
   if(url.pathname==='/api/status')return route.fulfill({json:status});
   if(url.pathname==='/api/files')return route.fulfill({json:{files:status.recording.file?[{name:status.recording.file,bytes:1024,active:status.recording.active}]:[]}});
   if(url.pathname==='/api/start'){status.state='fan-prerun';status.fan=true;status.remaining_s=payload.duration_s}
   if(url.pathname==='/api/stop'){status.state='cooldown';status.remaining_s=0;status.heater=false}
   if(url.pathname==='/api/record/start'){status.recording.active=true;status.recording.file='/session-1-preview.csv';status.recording.remaining_s=payload.duration_s}
   if(url.pathname==='/api/record/stop')status.recording.active=false;
   return route.fulfill({json:{ok:true}});
  });
  await page.goto('http://myms.test/');
  await page.waitForFunction(()=>document.getElementById('air').textContent==='24.5');
  assert.match(await page.locator('#notice').textContent(),/Simulation/);
  await page.locator('#target').fill('48');await page.locator('#cycleMinutes').fill('90');await page.locator('#start').click();
  await page.waitForFunction(()=>document.getElementById('state').textContent==='fan-prerun');
  assert.deepEqual(requests.find(r=>r.path==='/api/start').body,{target_c:48,duration_s:5400});
  assert.equal(requests.find(r=>r.path==='/api/start').headers['x-myms-request'],'1');
  await page.locator('#interval').fill('10');await page.locator('#recordMinutes').fill('360');await page.locator('#recordStart').click();
  await page.waitForFunction(()=>document.getElementById('recordStop').disabled===false);
  assert.deepEqual(requests.find(r=>r.path==='/api/record/start').body,{interval_s:10,duration_s:21600});
  await page.locator('#recordStop').click();
  await page.waitForSelector('a[download="session-1-preview.csv"]');
  await page.locator('#stop').click();
  await page.waitForFunction(()=>document.getElementById('state').textContent==='cooldown');
  await page.screenshot({path:path.join(root,'docs/firmware-admin.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'Mobile layout overflows horizontally');
  assert.deepEqual(errors,[]);
  console.log('Admin UI browser flows passed (mocked APIs, desktop + mobile)');
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
