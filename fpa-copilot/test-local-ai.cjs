const fs=require('fs'),vm=require('vm'),assert=require('assert');
class E{constructor(){this.children=[];this.listeners={};this.value='';this.disabled=false;}append(e){this.children.push(e)}prepend(e){this.children.unshift(e)}setAttribute(){}addEventListener(n,f){(this.listeners[n]??=[]).push(f)}click(){this.onclick?.();for(const f of this.listeners.click||[])f()}}
const panel=new E(),ids={};for(const id of ['clear','stop','aria-remove-information','aria-information'])ids[id]=new E();
const ctx={window:{},navigator:{},document:{querySelector:()=>panel,createElement:()=>new E(),getElementById:id=>ids[id]},console};
vm.createContext(ctx);vm.runInContext(fs.readFileSync(__dirname+'/local-ai.js','utf8'),ctx);
(async()=>{
 const api=ctx.window.ARIALocalAI;assert.equal(api.selected,false);
 await assert.rejects(()=>api.ask('hello',[],''),/Enable free AI/);
 const button=panel.children[0].children.find(e=>e.id==='aria-local-start');await button.onclick();
 assert.equal(api.selected,true);assert(panel.children[0].children.some(e=>/does not support WebGPU/.test(e.textContent||'')));
 assert(!fs.readFileSync(__dirname+'/local-ai.js','utf8').includes('fetch('));
 ctx.navigator.gpu={requestAdapter:async()=>null};
 await button.onclick();
 assert.equal(api.selected,true);assert.equal(button.disabled,false);
 assert(panel.children[0].children.some(e=>/compatible graphics adapter/.test(e.textContent||'')));
 let complete;ctx.navigator.gpu={requestAdapter:()=>new Promise(resolve=>{complete=resolve})};
 const pending=button.onclick();assert.equal(button.disabled,true);
 const off=panel.children[0].children.find(e=>e.textContent==='Use connected AI instead');
 off.onclick();complete(null);await pending;
 assert.equal(api.selected,false);assert.equal(button.disabled,false);
 assert(panel.children[0].children.some(e=>/Connected AI selected/.test(e.textContent||'')));
 console.log('PASS: opt-in, unavailable graphics, recoverable controls, canceled setup cannot reactivate free mode, no silent cloud fallback');
})().catch(e=>{console.error(e);process.exit(1)});
