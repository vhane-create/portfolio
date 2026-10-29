/* New speech always uses af_heart. Original media remains available in playback controls. */
(() => {
 const $ = id => document.getElementById(id), video = $('aria-heart-video');
 const controls = document.querySelector('.overlay .actions');
 function button(id, title) { const b = document.createElement('button'); b.id=id; b.textContent=title; controls.append(b); return b; }
 const enable=button('aria-enable-heart','Enable Heart voice');
 const talk=button('aria-talk','Talk to ARIA');
 const replay=button('aria-replay','Play latest spoken reply'); replay.disabled=true;
 const portrait=document.createElement('img'); portrait.src='assets/aria-full-body-approved.png'; portrait.alt=video.getAttribute('aria-label'); portrait.hidden=true; video.after(portrait);
 const audio=new Audio(); audio.id='aria-heart-audio'; audio.hidden=true; document.body.append(audio);
 let worker, enabled=false, loading=false, autoStart=false, loop=false, muted=false, version=0;
 let queue=[], recorded=[], objectURL, playing=false, finished=false, listening=false;
 function cancelRecognition() {
  const r=recognizer; recognizer=null; listening=false;
  if(r) { r.onstart=r.onresult=r.onerror=r.onend=null; try { r.abort(); } catch {} }
 }
 function stopAudio() {
  version++; audio.pause(); playing=false; queue=[]; finished=false;
  worker?.postMessage({type:'cancel'});
  if(objectURL) URL.revokeObjectURL(objectURL); objectURL=null;
  video.pause(); $('screen').dataset.state='idle';
 }
 function endLoop(message) {
  loop=false; autoStart=false; talk.textContent='Talk to ARIA'; talk.setAttribute('aria-pressed','false'); cancelRecognition();
  $('screen').dataset.state='idle'; status(message);
 }
 function listen() {
  if(!loop||!enabled||muted||$('send').disabled||listening) return;
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR) { endLoop('Voice input is unavailable here. Type a question to hear Heart answer.'); return; }
  const r=new SR(); recognizer=r; r.lang='en-US'; r.interimResults=false; r.continuous=false;
  r.onstart=()=>{if(recognizer===r){listening=true;$('screen').dataset.state='listening';status('Listening — speak to ARIA');}};
  r.onresult=e=>{if(recognizer!==r)return; const text=e.results[0][0].transcript.trim(); cancelRecognition(); if(text){$('question').value=text;ask();}else endLoop('No words detected. Click Talk to ARIA to retry.');};
  r.onerror=e=>{if(recognizer===r)endLoop(e.error==='not-allowed'?'Allow microphone access in your browser to speak with ARIA.':'Microphone stopped. Click Talk to ARIA to retry.');};
  r.onend=()=>{if(recognizer===r)endLoop('Microphone paused. Click Talk to ARIA when ready.');};
  try{r.start();}catch{endLoop('Microphone could not start. Please retry.');}
 }
 async function playNext() {
  if(playing)return;
  if(!queue.length){if(finished){$('screen').dataset.state='idle';status('Ready for your next question');if(loop)setTimeout(listen,250);}return;}
  const own=version;playing=true;
  if(objectURL)URL.revokeObjectURL(objectURL);
  objectURL=URL.createObjectURL(new Blob([queue.shift()],{type:'audio/wav'}));audio.src=objectURL;audio.muted=muted;
  video.hidden=true;portrait.hidden=false;
  try{await audio.play();if(own===version){$('screen').dataset.state='speaking';status('Speaking with Heart');}}
  catch{if(own===version){playing=false;endLoop('Speech ready — click Play latest spoken reply to hear it.');}}
 }
 audio.onended=()=>{playing=false;$('screen').dataset.state='idle';playNext();};
 audio.onerror=()=>{playing=false;endLoop('Audio could not play. Your text answer is available.');};
 function loadVoice(startTalking=false) {
  if(startTalking)autoStart=true;
  if(enabled){if(autoStart){autoStart=false;loop=true;talk.textContent='End voice conversation';talk.setAttribute('aria-pressed','true');listen();}return;}
  if(loading)return;
  loading=true;enable.disabled=true;enable.textContent='Loading Heart…';
  if(worker)worker.terminate();stopAudio();worker=new Worker('heart-worker.js?v=3',{type:'module'});
  status('Loading Heart — first setup may take a few minutes');
  worker.onmessage=({data})=>{
   if(data.type==='progress'){if(loading)status('Loading Heart: '+data.progress+'%');return;}
   if(data.type==='ready'){
    enabled=true;loading=false;enable.textContent='Heart voice ready';
    if(autoStart){autoStart=false;loop=true;talk.textContent='End voice conversation';talk.setAttribute('aria-pressed','true');listen();}
    else status('Heart ready — talk to ARIA or type a question');return;
   }
   if(data.type==='load-error'){enabled=false;loading=false;enable.disabled=false;enable.textContent='Retry Heart voice';endLoop(data.message);return;}
   if(data.id!==version)return;
   if(data.type==='audio'){recorded.push(data.buffer);queue.push(data.buffer);replay.disabled=false;playNext();}
   if(data.type==='done'){finished=true;if(!playing)playNext();}
   if(data.type==='error')endLoop(data.message);
  };
  worker.onerror=()=>{enabled=false;loading=false;enable.disabled=false;enable.textContent='Retry Heart voice';endLoop('Heart could not start. Please retry or use Chrome.');};
  worker.postMessage({type:'init',id:version});
 }
 enable.onclick=()=>loadVoice();
 window.ARIAHeart={
  beginQuestion(){stopAudio();cancelRecognition();recorded=[];replay.disabled=true;},
  replyFailed(){stopAudio();endLoop('Reply unavailable. See the message in the conversation.');}
 };
 say=function(text){
  stopAudio();cancelRecognition();recorded=[];replay.disabled=true;
  if(!enabled){status('Text answer ready — enable Heart voice to hear it');return;}
  if(muted){endLoop('Voice is off. Your text answer is available.');return;}
  $('screen').dataset.state='generating';status('Preparing Heart speech…');worker.postMessage({type:'speak',id:version,text});
 };
 talk.onclick=()=>{
  if(loop||autoStart){stopAudio();endLoop('Voice conversation stopped');return;}
  // A new microphone turn must not listen to ARIA's own speaker output.
  stopAudio();cancelRecognition();muted=false;audio.muted=false;$('mute').textContent='Voice: on';
  loadVoice(true);
 };
 replay.onclick=()=>{if(!recorded.length)return;stopAudio();cancelRecognition();queue=[...recorded];finished=true;playNext();};
 const originalStop=$('stop').onclick;
 $('stop').onclick=()=>{stopAudio();endLoop('Stopped');originalStop?.();};
 $('clear').addEventListener('click',()=>{stopAudio();recorded=[];replay.disabled=true;endLoop('Conversation cleared');});
 $('mute').textContent='Voice: on';
 $('mute').onclick=()=>{muted=!muted;audio.muted=muted;video.muted=muted;$('mute').textContent=muted?'Voice: off':'Voice: on';if(muted){stopAudio();endLoop('Voice is off');}};
 const originalIntro=$('intro').onclick;
 $('intro').onclick=()=>{stopAudio();endLoop('Playing introduction');portrait.hidden=true;video.hidden=false;originalIntro();};
 const sample=[...controls.querySelectorAll('button')].find(b=>b.textContent==='Play verified finance reply');
 if(sample){const playSample=sample.onclick;sample.onclick=()=>{stopAudio();endLoop('Playing saved finance reply');portrait.hidden=true;video.hidden=false;playSample();};}
 const note=document.createElement('p');note.className='muted';note.textContent='Talk to ARIA loads Heart once, then listens for your question. After speaking, she listens for your reply. New speech currently uses the approved portrait without matching lip movements.';controls.after(note);
})();
