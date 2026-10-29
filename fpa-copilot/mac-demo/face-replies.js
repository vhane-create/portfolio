/* Local Mac only: pair new reply text with its own Heart/MuseTalk video. */
(() => {
 const panel=document.querySelector('[aria-label="Voice and playback controls"]');
 const note=document.createElement('p');note.className='muted';note.setAttribute('role','status');
 note.textContent='Mac facial replies selected. Checking the existing Heart and MuseTalk installation…';panel?.prepend(note);
 let controller,pendingJob;
 const validId=id=>typeof id==='string'&&/^[a-f0-9]{32}$/.test(id);
 async function json(url, options={}){
  const response=await fetch(url,options);const data=await response.json();
  if(!data||typeof data!=='object'||Array.isArray(data))throw Error('Invalid local animation response.');
  if(!response.ok){const error=Error(data.detail||data.error||'Local animation request failed.');error.status=response.status;error.activeJob=data.active_job;throw error;}
  return data;
 }
 function pause(signal){
  return new Promise((resolve,reject)=>{
   const abort=()=>{clearTimeout(timer);const error=Error('Canceled');error.name='AbortError';reject(error);};
   const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve();},1500);
   if(signal.aborted)abort();else signal.addEventListener('abort',abort,{once:true});
  });
 }
 async function waitForJob(identity, signal, progress, previous=false){
  for(;;){
   const job=await json('/api/job/'+identity,{signal});
   if(job.state==='ready'||job.state==='error')return job;
   if(!['speaking','rendering'].includes(job.state))throw Error('Unknown local renderer state.');
   progress(previous?'Finishing the previous Mac render before starting your new answer…':job.state==='rendering'?'Rendering your answer’s lip movements on the Mac. This may take minutes.':'Generating this answer in Heart voice on the Mac…');
   await pause(signal);
  }
 }
 window.ARIAHeart.setReplyRenderer({
  cancel(){controller?.abort();controller=null;},
  async speak(text, progress){
   const own=new AbortController();controller=own;let expired=false;
   const timer=setTimeout(()=>{expired=true;own.abort();},65*60*1000);
   try{
    let started;
    for(;;){
     if(pendingJob){const previous=pendingJob;await waitForJob(previous,own.signal,progress,true);if(pendingJob===previous)pendingJob=null;}
     try{
      started=await json('/api/reply',{signal:own.signal,method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});break;
     }catch(error){
      if(error.status!==409)throw error;
      if(validId(error.activeJob))pendingJob=error.activeJob;
      else{progress('Waiting for the previous Mac render to release its resources…');await pause(own.signal);}
     }
    }
    if(!validId(started.id))throw Error('Invalid local animation job ID.');
    pendingJob=started.id;
    const job=await waitForJob(started.id,own.signal,progress);
    if(pendingJob===started.id)pendingJob=null;
    if(job.state==='error')throw Error(job.error||'Mac rendering failed.');
    if(typeof job.url!=='string'||!/^\/api\/media\/[a-f0-9]{32}\.mp4$/.test(job.url))throw Error('Invalid animated-reply URL.');
    return job.url;
   }catch(error){if(expired)throw Error('The Mac render exceeded the waiting limit. Check its Terminal log.');throw error;}
   finally{clearTimeout(timer);if(controller===own)controller=null;}
  }
 });
 fetch('/animation-health').then(response=>response.json()).then(state=>{
  note.textContent=state.missing?.length?'Animated replies need setup: '+state.missing.join(' '):'Mac facial renderer components found. Each new answer renders before playback; speed and visual quality still require testing.';
  const caption=document.getElementById('aria-caption');if(caption)caption.textContent=state.missing?.length?'Facial replies need setup. Open Voice & controls for the missing components.':'Mac facial replies selected. Ask “Hello” to test a short Heart-and-lip-sync reply. Rendering may take minutes.';
  const old=[...(panel?.querySelectorAll('p')||[])].find(p=>p.textContent.startsWith('New Heart speech uses the approved portrait.'));
  if(old)old.textContent='New replies in this Mac mode request rendered lip sync. Eye and head/neck movement uses the approved source animation. Body gestures and walking are not connected.';
 }).catch(()=>{note.textContent='Could not check the Mac facial renderer. Keep the local server running.';});
})();
