import test from 'node:test';
import assert from 'node:assert/strict';
import {SimliAvatar} from './simli-avatar.mjs';

class FakeClient {
  constructor(...args){this.args=args;this.events=new Map();this.cleared=0;this.stopped=false;FakeClient.latest=this;}
  async start(){}
  on(name,fn){if(!this.events.has(name))this.events.set(name,new Set());this.events.get(name).add(fn);}
  off(name,fn){this.events.get(name)?.delete(fn);}
  emit(name){for(const fn of this.events.get(name)||[])fn();}
  sendAudioData(bytes){this.sent=bytes;this.emit('speaking');if(!this.hold)this.emit('silent');}
  ClearBuffer(){this.cleared++;}
  async stop(){this.stopped=true;this.emit('stop');}
}
function make(){
  const tracks=[{stopped:false,stop(){this.stopped=true;}}];
  const media=()=>({paused:false,pause(){this.paused=true;},srcObject:{getTracks:()=>tracks}});
  const video=media(),audio=media();
  return {avatar:new SimliAvatar({SimliClient:FakeClient,video,audio,clock:()=>0,mintToken:async()=>({session_token:'test-short-lived-token'})}),video,audio,tracks};
}
test('only server-issued token reaches SDK and Heart PCM goes to avatar once',async()=>{
  const {avatar}=make();await avatar.start({deadline:300000});
  const pcm=new Uint8Array([1,0,2,0]);await avatar.speakPCM16(pcm);
  assert.equal(FakeClient.latest.args[0],'test-short-lived-token');
  assert.equal(FakeClient.latest.sent,pcm);await avatar.stop();
});
test('a longer-than-five-minute window is rejected before connecting',async()=>{
  const {avatar}=make();await assert.rejects(avatar.start({deadline:300001}),/at most five minutes/);
});
test('interrupting an answer flushes audio and rejects the pending answer',async()=>{
  const {avatar}=make();await avatar.start({deadline:300000});
  const client=FakeClient.latest;client.hold=true;
  const controller=new AbortController();
  const speech=avatar.speakPCM16(new Uint8Array([0,0]),{signal:controller.signal});
  controller.abort();await assert.rejects(speech,{name:'AbortError'});
  assert.equal(client.cleared,1);await avatar.stop();
});
test('stop closes local media and connection even when buffer flushing fails',async()=>{
  const {avatar,video,audio,tracks}=make();await avatar.start({deadline:300000});
  const client=FakeClient.latest;client.ClearBuffer=()=>{throw Error('signaling already closed');};
  await avatar.stop();assert.ok(video.paused&&audio.paused&&tracks.every(t=>t.stopped));assert.ok(client.stopped);
});
