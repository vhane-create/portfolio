const test = require('node:test');
const assert = require('node:assert/strict');
const {create} = require('./qa-window.js');
const fs=require('node:fs');
const vm=require('node:vm');
function setup() {
  let wall=0, mono=0, callback, stopped=[];
  const window=create({now:()=>wall,monotonic:()=>mono,schedule:fn=>(callback=fn,1),cancel:()=>{},onExpire:reason=>stopped.push(reason)});
  return {window,stopped,time:(w,m=w)=>{wall=w;mono=m;},fire:()=>callback()};
}
test('expires at five minutes and cannot be restarted by further questions',()=>{
 const x=setup();x.time(299999);assert.equal(x.window.canContinue(),true);
 x.time(300000);assert.equal(x.window.canContinue(),false);assert.deepEqual(x.stopped,['expired']);
 assert.equal(x.window.remainingMs(),0);x.window.canContinue();x.fire();assert.equal(x.stopped.length,1);
});
test('background suspension is counted even when the timer has not fired',()=>{
 const x=setup();x.time(600000);assert.equal(x.window.canContinue(),false);assert.equal(x.stopped.length,1);
});
test('moving the system clock backward cannot extend the session',()=>{
 const x=setup();x.time(-600000,300000);assert.equal(x.window.canContinue(),false);
});
test('the scheduled cutoff stops an idle microphone with no new input',()=>{
 const x=setup();x.time(300000);x.fire();assert.equal(x.stopped.length,1);assert.equal(x.window.canContinue(),false);
});
test('leaving the page cancels the session only once',()=>{
 const x=setup();x.window.stop('closed');x.window.stop('closed');assert.deepEqual(x.stopped,['closed']);
 assert.equal(x.window.canContinue(),false);
});
test('the actual post-tour wiring stops media, aborts pending reasoning and blocks restart',()=>{
 const html=fs.readFileSync(__dirname+'/aria-final.html','utf8');
 const script=html.split('<script src="qa-window.js?v=1"></script><script>')[1].split('</script>')[0];
 let time=0, stopped=0, aborted=0, interval, handlers={};
 const elements=new Map();
 const element=id=>{if(!elements.has(id))elements.set(id,{id,disabled:false,closest(selector){return selector==='#stop'?(id==='stop'?this:null):this;}});return elements.get(id);};
 element('stop').click=()=>{let blocked=false;handlers.click?.({target:element('stop'),preventDefault(){blocked=true;},stopImmediatePropagation(){blocked=true;}});if(!blocked)stopped++;};
 const context={URLSearchParams,location:{search:'?after-tour=1'},window:{addEventListener(){}},
  document:{createElement:()=>({style:{},setAttribute(){}}),querySelector:()=>({prepend(){}}),getElementById:element,addEventListener:(name,fn)=>handlers[name]=fn},
  ARIAQuestionWindow:{create:options=>create({...options,now:()=>time,monotonic:()=>time,schedule:()=>1,cancel(){}})},
  requestVersion:0,reasoningController:{abort:()=>aborted++},status(){},setInterval:fn=>(interval=fn,1),clearInterval(){}};
 vm.runInNewContext(script,context);assert.equal(context.window.ARIAQA.canContinue(),true);
 time=300000;interval();assert.equal(stopped,1);assert.equal(aborted,1);assert.equal(context.requestVersion,1);
 assert.equal(element('aria-talk').disabled,true);assert.equal(element('send').disabled,true);
 let blocked=false;handlers.click({target:element('aria-talk'),preventDefault(){blocked=true;},stopImmediatePropagation(){}});assert.equal(blocked,true);
});
