import assert from 'node:assert/strict';
import {GestureGate,installCamera} from './camera-interaction.mjs';
const gate=new GestureGate();
assert.equal(gate.update('Open_Palm',.9,0),null);
assert.equal(gate.update('Open_Palm',.9,900),'Open_Palm');
assert.equal(gate.update('Open_Palm',.9,10000),null);
gate.update('None',1,11000);gate.update('Thumb_Up',.95,12000);
assert.equal(gate.update('Thumb_Up',.95,12900),'Thumb_Up');
assert.equal(gate.update('Open_Palm',.2,14000),null);
class El {
 constructor(){this.style={};this.children=[];this.handlers={};this.paused=true;this.readyState=2;this.currentTime=1;}
 append(...els){this.children.push(...els);}after(){}setAttribute(k,v){this[k]=v;}
 addEventListener(k,f){this.handlers[k]=f;}play(){return Promise.resolve();}
}
function setup(getUserMedia,loadModel){
 const controls=new El(),stop=new El(),events={},wevents={};let scheduled,stopped=0,closed=0;
 const doc={hidden:false,querySelector:()=>controls,createElement:()=>new El(),getElementById:()=>stop,addEventListener:(k,f)=>events[k]=f};
 const win={setTimeout:f=>{scheduled=f;return 1;},clearTimeout:()=>{scheduled=null;},performance:{now:()=>0},addEventListener:(k,f)=>wevents[k]=f};
 const stream={getTracks:()=>[{stop:()=>stopped++}]};
 const model={close:()=>closed++,recognizeForVideo:()=>({gestures:[]})};
 const ui=installCamera({document:doc,window:win,navigator:{mediaDevices:{getUserMedia:getUserMedia|| (async()=>stream)}},loadModel:loadModel||(async()=>model)});
 return {ui,events,wevents,doc,stream,model,counts:()=>({stopped,closed}),hasTimer:()=>Boolean(scheduled)};
}
let s=setup();await s.ui.button.onclick();assert.equal(s.ui.button['aria-pressed'],'true');assert(s.hasTimer());
s.doc.hidden=true;s.events.visibilitychange();assert.deepEqual(s.counts(),{stopped:1,closed:1});assert.equal(s.ui.preview.srcObject,null);assert(!s.hasTimer());
let release;s=setup(()=>new Promise(r=>release=r));const starting=s.ui.button.onclick();await s.ui.button.onclick();release(s.stream);await starting;assert.equal(s.counts().stopped,1);assert.equal(s.ui.button['aria-pressed'],'false');
s=setup(async()=>{throw Object.assign(new Error(),{name:'NotAllowedError'});});await s.ui.button.onclick();assert.equal(s.ui.button['aria-pressed'],'false');
console.log('PASS: gesture stability/cooldown, camera release, tab hide, cancel during permission prompt, denied permission. Camera and model are simulated.');
