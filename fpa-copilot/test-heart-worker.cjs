const fs=require('fs'),vm=require('vm'),assert=require('assert');
const messages=[], calls=[];
const context={self:{},postMessage:m=>messages.push(m),KokoroTTS:{from_pretrained:async()=>({generate:async(text,options)=>{calls.push({text,options});return{audio:new Float32Array([0,.1,-.1,0]),sampling_rate:24000};}})},Float32Array,ArrayBuffer,DataView,Math};
vm.runInNewContext(fs.readFileSync(__dirname+'/heart-worker.js','utf8').replace(/^import .*;\n/,''),context);
(async()=>{
 await context.self.onmessage({data:{type:'init',id:1}});assert.equal(messages[0].type,'ready');
 await context.self.onmessage({data:{type:'speak',id:2,text:'Hello. '+('This is a new response with Heart voice. '.repeat(12))}});
 assert(calls.length>2);assert(calls.every(c=>c.options.voice==='af_heart'&&c.options.speed===1&&c.text.length<=240));
 for(const m of messages.filter(m=>m.type==='audio')){assert.equal(Buffer.from(m.buffer).subarray(0,4).toString(),'RIFF');assert.equal(new DataView(m.buffer).getUint32(24,true),24000);assert.equal(m.id,2);}
 assert.equal(messages.at(-1).type,'done');console.log('PASS: fixed Heart voice, bounded full-text chunks, playable WAV format, reply pairing and completion');
})().catch(e=>{console.error(e);process.exit(1)});
