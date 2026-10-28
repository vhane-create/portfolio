/* Executes the actual page scripts with a minimal DOM; does not test video playback. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'), vm=require('node:vm');
function page(name,url=''){
 const elements=new Map();
 class Element{
  constructor(){this.children=[];this.listeners={};this.dataset={state:'idle'};this.value='';this.content=url;this.textContent='';this.disabled=false;}
  append(...items){this.children.push(...items);} prepend(...items){this.children.unshift(...items);}
  addEventListener(event,fn){(this.listeners[event]??=[]).push(fn);}
  replaceChildren(){this.children=[];} replaceWith(other){elements.set(other.id,other);}
  setAttribute(){} querySelector(){return new Element();}
  pause(){} async play(){this.onplay?.();} load(){}
  click(){this.onclick?.();for(const fn of this.listeners.click||[])fn();}
 }
 const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
 const document={getElementById:get,querySelector:selector=>selector.startsWith('meta')?{content:url}:get(selector),querySelectorAll:()=>[],createElement:()=>new Element(),createTextNode:text=>({textContent:text})};
 const sandbox={document,console,URL,AbortController,setTimeout,clearTimeout,location:{href:'https://example.test/fpa-copilot/'},window:{prompt:()=> 'test-access-code'},fetch:async()=>{throw Error('Network should not be needed');}};
 vm.createContext(sandbox);
 vm.runInContext(fs.readFileSync(__dirname+'/conversation.js','utf8'),sandbox);
 const source=fs.readFileSync(__dirname+'/'+name,'utf8');
 for(const match of source.matchAll(/<script>([\s\S]*?)<\/script>/g))vm.runInContext(match[1],sandbox);
 return {sandbox,get,ask:async q=>{get('question').value=q;await vm.runInContext('ask()',sandbox);},messages:()=>get('history').children.flatMap(x=>x.children||[]).map(x=>x.textContent||'').join('\n')};
}
for(const name of ['aria-final.html','aria-heart-preview.html']){
 test(name+': actual scripts retain context, switch topic, and clear',async()=>{
  const p=page(name);
  await p.ask('Budget revenue is $100,000; actual is $90,000.');
  await p.ask('Why did that happen?');
  await p.ask('What if actual revenue increases 10% from $90,000?');
  assert.match(p.messages(),/\$99,000.00/);assert.match(p.messages(),/not its cause/);
  await p.ask('Explain cash flow versus profit.');await p.ask('Explain that more simply.');
  assert.match(p.messages(),/Profit is what you earn/);
  p.get('clear').click();await p.ask('Why?');assert.match(p.messages(),/Which result/);
  assert.doesNotMatch(p.messages(),/90,000/);
 });
 test(name+': configured reasoning gets history and matching response',async()=>{
  const p=page(name,'https://reasoning.example/');let request;
  p.sandbox.fetch=async(url,options)=>{request={url:String(url),...JSON.parse(options.body)};return {ok:true,json:async()=>({answer:'A relevant business explanation.'})};};
  await p.ask('Hello');await p.ask('How should I prioritize my business goals?');
  assert.equal(request.url,'https://reasoning.example/ask');assert.equal(request.history.length,2);
  assert.match(p.messages(),/A relevant business explanation/);
 });
 test(name+': clear suppresses a pending reply',async()=>{
  const p=page(name,'https://reasoning.example/');let resolve;
  p.sandbox.fetch=()=>new Promise(r=>{resolve=r;});
  const pending=p.ask('How should I prioritize my business goals?');
  p.get('clear').click();resolve({ok:true,json:async()=>({answer:'STALE REPLY'})});await pending;
  assert.doesNotMatch(p.messages(),/STALE REPLY/);assert.equal(p.get('send').disabled,false);
 });
}
