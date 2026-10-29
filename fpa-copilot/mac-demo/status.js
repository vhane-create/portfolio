(() => {
 const panel=document.querySelector('[aria-label="Voice and playback controls"]');
 const note=document.createElement('p');note.className='muted';note.setAttribute('role','status');
 note.textContent='Checking the local Mac conversation service…';panel?.prepend(note);
 fetch('/health').then(async response=>{
  const state=await response.json();
  note.textContent=state.status==='ready'?'Mac demo: local reasoning is available. Type or speak a short question. Mac facial replies render before playback; full-body animation is not connected.':state.detail||'Load a chat model in LM Studio, then start its local server.';
 }).catch(()=>{note.textContent='Local reasoning status could not be checked. Keep the Mac demo server running.';});
 const caption=document.getElementById('aria-caption');
 if(caption)caption.textContent='Mac demo · checking local reasoning and the facial-reply renderer.';
})();
