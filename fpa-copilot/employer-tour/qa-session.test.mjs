import test from 'node:test';
import assert from 'node:assert/strict';
import {QASession, QA_LIMIT_MS, REPEAT_QUESTION, voiceAction} from './qa-session.mjs';

function setup(overrides = {}) {
  let time = 0;
  const calls = {asked: [], spoken: [], mediaStops: 0, micStops: 0};
  const session = new QASession({clock: () => time,
    ask: async (q,h) => { calls.asked.push({q,h}); return 'A new answer to ' + q; },
    speak: async (text,opts) => { calls.spoken.push({text,action: opts.action}); },
    stopMedia: () => calls.mediaStops++, stopListening: () => calls.micStops++, ...overrides});
  return {session,calls,setTime: n => {time = n;}};
}

test('the hard limit stops media, microphone, and all new questions at exactly five minutes', async () => {
  const {session,calls,setTime} = setup(); session.start();
  setTime(QA_LIMIT_MS-1); assert.equal(session.checkDeadline(),true);
  setTime(QA_LIMIT_MS); assert.equal(session.checkDeadline(),false); assert.equal(session.state,'expired');
  assert.equal(calls.mediaStops,2); assert.equal(calls.micStops,2);
  assert.equal((await session.heard('Another question',.9)).status,'expired'); assert.equal(calls.asked.length,0);
});
test('an answer finishing after the deadline is never spoken', async () => {
  let finish; const {session,calls,setTime} = setup({ask: () => new Promise(r => {finish = r;})});
  session.start(); const pending = session.heard('What is NPV?',.9);
  setTime(QA_LIMIT_MS); session.checkDeadline(); finish('Late answer');
  assert.equal((await pending).status,'expired'); assert.equal(calls.spoken.length,0);
});
test('expiry aborts an answer that is currently speaking', async () => {
  let signal; const {session,setTime} = setup({speak: (_text,opts) => new Promise(resolve => {
    signal = opts.signal; signal.addEventListener('abort',resolve,{once:true});
  })});
  session.start(); const pending = session.heard('Explain cash flow',.9); await Promise.resolve();
  assert.equal(session.state,'speaking'); setTime(QA_LIMIT_MS); session.checkDeadline();
  assert.equal(signal.aborted,true); assert.equal((await pending).status,'expired');
});
test('unclear input asks for repetition without inventing a question or calling the model', async () => {
  const {session,calls} = setup(); session.start();
  assert.equal((await session.heard('uncertain words',.2)).status,'repeat');
  assert.equal(calls.asked.length,0); assert.equal(calls.spoken[0].text,REPEAT_QUESTION);
  assert.equal(calls.spoken[0].action,'approach-and-repeat'); assert.equal(session.history.length,0);
});
test('a missing browser confidence score does not reject a clear transcript', async () => {
  const {session,calls} = setup(); session.start();
  assert.equal((await session.heard('What is IRR?',0)).status,'answered'); assert.equal(calls.asked.length,1);
});
test('follow-up history stays in this session and a fresh session clears it', async () => {
  const a = setup(), b = setup(); a.session.start(); b.session.start();
  await a.session.heard('What is NPV?',.9); await a.session.heard('Explain that more simply',.9);
  assert.equal(a.calls.asked[1].h.length,2); assert.equal(b.session.history.length,0);
  a.session.start(); assert.equal(a.session.history.length,0);
});
test('the handshake command dispatches the gesture and leaves the original deadline intact', async () => {
  const gestures=[];
  const {session,calls,setTime}=setup({gesture:async action=>gestures.push(action)});
  session.start(); const deadline=session.deadline; setTime(50000);
  assert.equal((await session.heard('ARIA, come shake my hand!',.95)).status,'gesture');
  assert.deepEqual(gestures,['virtual-handshake']); assert.equal(calls.asked.length,0);
  assert.equal(session.deadline,deadline); assert.equal(session.remainingMs(),250000);
});
test('a missing gesture connection reports unavailable instead of claiming a handshake', async () => {
  const {session,calls}=setup();session.start();
  assert.equal((await session.heard('ARIA come shake my hand',.9)).status,'unavailable');
  assert.equal(calls.spoken.length,0);assert.equal(calls.asked.length,0);
});
test('the five-minute stop interrupts a gesture too', async () => {
  let signal;
  const {session,setTime}=setup({gesture:(_a,opts)=>new Promise(resolve=>{signal=opts.signal;signal.addEventListener('abort',resolve,{once:true});})});
  session.start();setTime(QA_LIMIT_MS-1000);const p=session.heard('ARIA shake my hand',.9);
  setTime(QA_LIMIT_MS);session.checkDeadline();assert.equal(signal.aborted,true);assert.equal((await p).status,'expired');
});
test('ordinary questions mentioning a handshake are not mistaken for an action request',()=>{
 assert.equal(voiceAction('What does a handshake agreement mean?'),null);
 assert.equal(voiceAction('ARIA, explain a handshake agreement'),null);
 assert.equal(voiceAction('Hey ARIA please come and shake my hand please'),'virtual-handshake');
});
test('uncertain recognition of a gesture requests clarification instead of moving',async()=>{
 const gestures=[];const {session,calls}=setup({gesture:async a=>gestures.push(a)});session.start();
 assert.equal((await session.heard('ARIA come shake my hand',.3)).status,'repeat');
 assert.equal(gestures.length,0);assert.equal(calls.spoken[0].text,REPEAT_QUESTION);
});
