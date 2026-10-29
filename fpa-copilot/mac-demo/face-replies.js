/* Local Mac only: match each new answer to a newly rendered Heart/MuseTalk video. */
(() => {
 const panel=document.querySelector('[aria-label="Voice and playback controls"]');
 const note=document.createElement('p');note.className='muted';note.setAttribute('role','status');
 note.textContent='Mac facial replies selected. Checking the existing Heart and MuseTalk installation…';panel?.prepend(note);
 let controller;
 async function json(url, options={}){
  const response=await fetch(url,options);const data=await response.json();
  if(!response.ok)throw Error(data.detail||data.error||'Local animation request failed.');
  return data;
 }
 window.ARIAHeart.setReplyRenderer({
  cancel(){controller?.abort();controller=null;},
  async speak(text, progress){
   const own=new AbortController();controller=own;
   const options={signal:own.signal};
   const started=await json('/api/reply',{...options,method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
   const deadline=Date.now()+65*60*1000;
   while(!own.signal.aborted){
    if(Date.now()>deadline)throw Error('The Mac render exceeded the waiting limit. Check its Terminal log.');
    const job=await json('/api/job/'+started.id,options);
    if(job.state==='error')throw Error(job.error||'Mac rendering failed.');
    if(job.state==='ready'){
     if(!new RegExp('^/api/media/[a-f0-9]{32}\\.mp4$').test(job.url))throw Error('Invalid animated-reply URL.');
     return job.url;
    }
    progress(job.state==='rendering'?'Rendering your answer’s lip movements on the Mac. This may take minutes.':'Generating this answer in Heart voice on the Mac…');
    await new Promise(resolve=>setTimeout(resolve,1500));
   }
   const error=Error('Canceled');error.name='AbortError';throw error;
  }
 });
 fetch('/animation-health').then(response=>response.json()).then(state=>{
  note.textContent=state.missing?.length?'Animated replies need setup: '+state.missing.join(' '):'Mac facial renderer components found. Each new answer renders before playback; speed and visual quality still require testing.';
  const caption=document.getElementById('aria-caption');if(caption)caption.textContent=state.missing?.length?'Facial replies need setup. Open Voice & controls for the missing components.':'Mac facial replies selected. Ask “Hello” to test a short Heart-and-lip-sync reply. Rendering may take minutes.';
  const old=[...panel.querySelectorAll('p')].find(p=>p.textContent.startsWith('New Heart speech uses the approved portrait.'));
  if(old)old.textContent='New replies in this Mac mode request rendered lip sync. Eye and head/neck movement uses the approved source animation. Body gestures and walking are not connected.';
 }).catch(()=>{note.textContent='Could not check the Mac facial renderer. Keep the local server running.';});
})();
