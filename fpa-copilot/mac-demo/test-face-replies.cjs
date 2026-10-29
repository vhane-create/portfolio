const fs=require('fs'),vm=require('vm'),assert=require('assert');
const oldId='a'.repeat(32),newId='b'.repeat(32);
function fixture(route){
 let renderer;const requests=[];
 const element=()=>({textContent:'',setAttribute(){},prepend(){},querySelectorAll(){return[];}});
 const panel=element(),caption=element();
 const context={window:{ARIAHeart:{setReplyRenderer:value=>renderer=value}},
  document:{querySelector:()=>panel,createElement:element,getElementById:()=>caption},
  AbortController,Date,console,clearTimeout,
  setTimeout:(fn,ms)=>setTimeout(fn,ms===1500?0:ms),
  fetch:async(url,options={})=>{
   requests.push({url,options});
   const result=url==='/animation-health'?{missing:[]}:await route(url,options);
   return{ok:!(result.http>=400),status:result.http||200,json:async()=>result};
  }};
 vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/face-replies.js','utf8'),context);
 return{renderer,requests};
}
(async()=>{
 let submissions=0;
 const busy=fixture(async(url,options)=>{
  if(url==='/api/reply')return ++submissions===1?{http:409,detail:'busy',active_job:oldId}:{id:newId};
  if(url==='/api/job/'+oldId)return{state:'ready',url:'/api/media/'+oldId+'.mp4'};
  if(url==='/api/job/'+newId)return{state:'ready',url:'/api/media/'+newId+'.mp4'};
  throw Error('Unexpected request '+url);
 });
 assert.equal(await busy.renderer.speak('My new answer.',()=>{}),'/api/media/'+newId+'.mp4');
 assert.equal(submissions,2);
 assert.equal(JSON.parse(busy.requests.findLast(x=>x.url==='/api/reply').options.body).text,'My new answer.');
 const invalid=fixture(async url=>url==='/api/reply'?{id:newId}:{state:'ready',url:'https://other.invalid/voice.mp4'});
 await assert.rejects(()=>invalid.renderer.speak('Hello',()=>{}),/Invalid animated-reply URL/);
 let started=false,aborted=false,posted=0;
 const canceled=fixture(async(url,options)=>{
  if(url==='/api/reply')return{id:++posted===1?oldId:newId};
  if(url==='/api/job/'+oldId&&!aborted){
   started=true;return new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>{
    aborted=true;const error=Error('Canceled');error.name='AbortError';reject(error);
   },{once:true}));
  }
  return{state:'ready',url:'/api/media/'+(url.endsWith(oldId)?oldId:newId)+'.mp4'};
 });
 const pending=canceled.renderer.speak('Old answer.',()=>{});
 await new Promise(setImmediate);assert(started);
 const rejection=assert.rejects(()=>pending,error=>error.name==='AbortError');
 canceled.renderer.cancel();await rejection;
 assert.equal(await canceled.renderer.speak('Replacement answer.',()=>{}),'/api/media/'+newId+'.mp4');
 assert(!canceled.requests.some(x=>x.url.startsWith('https:')));
 console.log('PASS: busy-render recovery, correct reply pairing, cancellation recovery and rejection of external media');
})().catch(error=>{console.error(error);process.exit(1);});
