const fs=require('fs'),vm=require('vm'),assert=require('assert');
(async()=>{
 let release,entered;const enteredPromise=new Promise(r=>entered=r),barrier=new Promise(r=>release=r),messages=[];let first=true;
 const ctx={self:{},Float32Array,ArrayBuffer,DataView,Math,Number,postMessage:m=>messages.push(m),KokoroTTS:{from_pretrained:async()=>({generate:async()=>{if(first){first=false;entered();await barrier;}return{audio:new Float32Array([.1,-.1]),sampling_rate:24000}}})}};
 vm.runInNewContext(fs.readFileSync(__dirname+'/heart-worker.js','utf8').replace(/^import .*;\n/,''),ctx);
 const running=ctx.self.onmessage({data:{type:'speak',id:1,text:'Old response.'}});await enteredPromise;
 ctx.self.onmessage({data:{type:'cancel'}});ctx.self.onmessage({data:{type:'speak',id:2,text:'New response.'}});release();await running;
 assert(!messages.some(m=>m.id===1));assert(messages.some(m=>m.id===2&&m.type==='audio'));assert(messages.some(m=>m.id===2&&m.type==='done'));
 console.log('PASS: canceled in-flight synthesis emits no stale audio; newer reply completes');
})().catch(e=>{console.error(e);process.exit(1)});
