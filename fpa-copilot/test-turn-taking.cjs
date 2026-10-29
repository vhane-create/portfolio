const fs=require('fs'),vm=require('vm'),assert=require('assert');
class Element{
 constructor(){this.children=[];this.dataset={};this.disabled=false;this.textContent='';this.handlers={};this.hidden=false;}
 append(x){this.children.push(x);}after(){}setAttribute(k,v){this[k]=v;}getAttribute(){return 'Approved ARIA';}
 addEventListener(k,f){(this.handlers[k]??=[]).push(f);}querySelectorAll(){return this.children;}pause(){this.paused=true;}
}
const ids={};for(const id of ['screen','aria-heart-video','send','question','stop','clear','mute','intro'])ids[id]=new Element();
ids.intro.onclick=()=>{};const controls=new Element(), sample=new Element();sample.textContent='Play verified finance reply';sample.onclick=()=>{};controls.append(sample);
let audio,worker,starts=0,asks=0,lastStatus='';
class Audio extends Element{constructor(){super();audio=this;}play(){this.paused=false;this.plays=(this.plays||0)+1;return Promise.resolve();}}
class Worker{constructor(){worker=this;this.messages=[];}postMessage(m){this.messages.push(m);}terminate(){}emit(data){this.onmessage({data});}}
class Recognition{start(){starts++;this.onstart?.();}abort(){this.onerror?.({error:'aborted'});}stop(){this.onerror?.({error:'aborted'});}}
const c={window:{SpeechRecognition:Recognition},document:{body:new Element(),getElementById:id=>ids[id]||controls.children.find(x=>x.id===id),querySelector:()=>controls,createElement:()=>new Element()},Audio,Worker,recognizer:null,console,Blob,URL:{createObjectURL:()=> 'blob:test',revokeObjectURL(){}},status:s=>lastStatus=s,setTimeout:f=>f(),ask:()=>{asks++;c.window.ARIAHeart.beginQuestion();}};
vm.createContext(c);vm.runInContext(fs.readFileSync(__dirname+'/voice-loop.js','utf8'),c);
const talk=controls.children.find(x=>x.id==='aria-talk');talk.onclick();
assert(worker.messages.some(m=>m.type==='init'));assert.equal(starts,0);
worker.emit({type:'ready'});assert.equal(starts,1);assert.equal(talk.textContent,'End voice conversation');
const r=c.recognizer;r.onresult({results:[[{transcript:'What is a forecast?'}]]});assert.equal(asks,1);assert.equal(talk.textContent,'End voice conversation');
c.say('An updated expectation.');const id=worker.messages.findLast(m=>m.type==='speak').id;
worker.emit({type:'audio',id:id-1,buffer:new ArrayBuffer(48)});assert(!audio.plays);
worker.emit({type:'audio',id,buffer:new ArrayBuffer(48)});worker.emit({type:'done',id});
assert.equal(audio.plays,1);audio.onended();assert.equal(starts,2);
c.window.ARIAHeart.beginQuestion();const previous=audio.plays;
worker.emit({type:'audio',id,buffer:new ArrayBuffer(48)});assert.equal(audio.plays,previous);
ids.stop.onclick();assert.equal(talk.textContent,'Talk to ARIA');assert.equal(c.recognizer,null);
console.log('PASS: one-click load/listen, transcript handoff, programmatic microphone stop, stale-audio rejection, automatic next turn, stop cancellation');
