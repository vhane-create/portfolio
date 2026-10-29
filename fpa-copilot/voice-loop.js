/* Heart stays af_heart; no browser-voice substitution and no unrelated video for new speech. */
(() => {
 const $ = id => document.getElementById(id), video = $('aria-heart-video');
 const controls = document.querySelector('.overlay .actions');
 const enable = document.createElement('button'); enable.textContent = 'Enable Heart voice'; controls.append(enable);
 const talk = document.createElement('button'); talk.textContent = 'Start voice conversation'; talk.disabled = true; controls.append(talk);
 const replay = document.createElement('button'); replay.textContent = 'Play latest spoken reply'; replay.disabled = true; controls.append(replay);
 const portrait = document.createElement('img'); portrait.src = 'assets/aria-full-body-approved.png'; portrait.alt = video.getAttribute('aria-label'); portrait.hidden = true; video.after(portrait);
 const audio = new Audio(); let worker, enabled = false, loop = false, muted = false, version = 0;
 let queue = [], recorded = [], objectURL, playing = false, finished = false;
 function stopAudio() {
  version++; audio.pause(); playing = false; queue = []; finished = false;
  if (objectURL) URL.revokeObjectURL(objectURL); objectURL = null;
  video.pause(); $('screen').dataset.state = 'idle';
 }
 function endLoop(message) { loop = false; talk.textContent = 'Start voice conversation'; recognizer?.stop(); status(message); }
 function listen() {
  if (!loop || !enabled || muted || $('send').disabled) return;
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { endLoop('Voice input is unavailable in this browser. You can type and hear Heart replies.'); return; }
  recognizer = new SR(); recognizer.lang = 'en-US'; recognizer.interimResults = false;
  recognizer.onstart = () => { $('screen').dataset.state = 'listening'; status('Listening — speak to ARIA'); };
  recognizer.onresult = e => { $('question').value = e.results[0][0].transcript; ask(); };
  recognizer.onerror = e => endLoop(e.error === 'not-allowed' ? 'Microphone permission is needed to speak with ARIA.' : 'Microphone stopped. Click Start voice conversation to retry.');
  // No blind restart: avoid feedback loops and repeated microphone permission prompts.
  recognizer.onend = () => { if ($('screen').dataset.state === 'listening') $('screen').dataset.state = 'idle'; };
  try { recognizer.start(); } catch { endLoop('Microphone could not start. Please retry.'); }
 }
 async function playNext() {
  if (playing) return;
  if (!queue.length) { if (finished) { status('Ready for your next question'); if (loop) listen(); } return; }
  const own = version; playing = true;
  if (objectURL) URL.revokeObjectURL(objectURL);
  objectURL = URL.createObjectURL(new Blob([queue.shift()], {type: 'audio/wav'})); audio.src = objectURL; audio.muted = muted;
  video.hidden = true; portrait.hidden = false;
  try { await audio.play(); if (own === version) { $('screen').dataset.state = 'speaking'; status('Speaking with Heart'); } }
  catch { if (own === version) { playing = false; endLoop('Speech ready — click Play latest spoken reply to hear it.'); } }
 }
 audio.onended = () => { playing = false; $('screen').dataset.state = 'idle'; playNext(); };
 audio.onerror = () => { playing = false; endLoop('Audio could not play. Your text answer is still available.'); };
 enable.onclick = () => {
  if (enabled) return;
  if (worker) worker.terminate();
  stopAudio(); worker = new Worker('heart-worker.js', {type: 'module'});
  enable.disabled = true; status('Loading Heart voice for this browser — first setup may take a few minutes');
  worker.onmessage = ({data}) => {
   if (data.type === 'progress') { if (!enabled) status('Loading Heart voice: '+data.progress+'%'); return; }
   if (data.type === 'ready') { enabled = true; enable.textContent = 'Heart voice ready'; talk.disabled = false; status('Heart ready — click Start voice conversation or ask a question'); return; }
   if (data.id !== version) return;
   if (data.type === 'audio') { recorded.push(data.buffer); queue.push(data.buffer); replay.disabled = false; playNext(); }
   if (data.type === 'done') { finished = true; if (!playing) playNext(); }
   if (data.type === 'error') { enable.disabled = false; endLoop(data.message); }
  };
  worker.onerror = () => { enable.disabled = false; enabled = false; talk.disabled = true; endLoop('Heart voice could not start in this browser. Please retry or use Chrome.'); };
  worker.postMessage({type: 'init', id: version});
 };
 say = function(text) {
  stopAudio(); recognizer?.stop(); recorded = []; replay.disabled = true;
  if (!enabled) { status('Text answer ready — click Enable Heart voice for spoken replies'); return; }
  if (muted) { endLoop('Voice is off. Your text answer is available.'); return; }
  status('Preparing Heart speech…'); worker.postMessage({type: 'speak', id: version, text});
 };
 talk.onclick = () => {
  if (loop) { stopAudio(); endLoop('Voice conversation stopped'); return; }
  loop = true; talk.textContent = 'End voice conversation'; listen();
 };
 replay.onclick = () => { if (!recorded.length) return; stopAudio(); queue = [...recorded]; finished = true; playNext(); };
 const originalStop = $('stop').onclick;
 $('stop').onclick = () => { stopAudio(); endLoop('Stopped'); originalStop?.(); };
 $('clear').addEventListener('click', () => { stopAudio(); recorded = []; replay.disabled = true; endLoop('Conversation cleared'); });
 $('mute').textContent = 'Voice: on';
 $('mute').onclick = () => { muted = !muted; audio.muted = muted; video.muted = muted; $('mute').textContent = muted ? 'Voice: off' : 'Voice: on'; if (muted) endLoop('Voice is off'); };
 const originalIntro = $('intro').onclick;
 $('intro').onclick = () => { stopAudio(); endLoop('Playing introduction'); portrait.hidden = true; video.hidden = false; originalIntro(); };
 const sample = [...controls.querySelectorAll('button')].find(b => b.textContent === 'Play verified finance reply');
 if (sample) { const playSample = sample.onclick; sample.onclick = () => { stopAudio(); endLoop('Playing saved finance reply'); portrait.hidden = true; video.hidden = false; playSample(); }; }
 const note = document.createElement('p'); note.className = 'muted'; note.textContent = 'Voice conversation: enable Heart once, then start speaking. New replies use her approved portrait with Heart audio; new lip movements are not yet connected. Microphone availability depends on your browser.'; controls.after(note);
})();
