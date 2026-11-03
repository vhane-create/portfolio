// Camera frames stay on this device. Only an intentional gesture triggers a reply.
export class GestureGate {
 constructor(){this.reset();}
 reset(){this.name='';this.since=0;this.fired=false;this.last=-Infinity;}
 update(name,score,now){
  if(!['Open_Palm','Thumb_Up'].includes(name)||score<0.8){this.name='';this.fired=false;return null;}
  if(name!==this.name){this.name=name;this.since=now;this.fired=false;return null;}
  if(this.fired||now-this.since<800||now-this.last<8000)return null;
  this.fired=true;this.last=now;return name;
 }
}

export function installCamera({document,window,navigator,loadModel}){
 const controls=document.querySelector('.overlay .actions');
 if(!controls)return;
 const button=document.createElement('button');button.id='aria-camera';button.textContent='Enable camera';button.setAttribute('aria-pressed','false');controls.append(button);
 const panel=document.createElement('section');panel.className='muted';
 const message=document.createElement('p');message.setAttribute('role','status');message.textContent='Camera off. Enable it to greet ARIA with a held open palm or thumbs-up. Video is processed on this device; model files download on first use.';
 const preview=document.createElement('video');preview.muted=true;preview.autoplay=true;preview.playsInline=true;preview.hidden=true;preview.setAttribute('aria-label','Your camera preview');preview.style.cssText='width:160px;max-height:120px;object-fit:cover;transform:scaleX(-1);border-radius:10px';
 panel.append(message,preview);controls.after(panel);
 let generation=0,stream=null,model=null,timer=null,enabled=false,pending=false,lastFrame=-1;
 const gate=new GestureGate();
 function stop(text='Camera off.'){
  generation++;enabled=false;pending=false;window.clearTimeout(timer);timer=null;
  stream?.getTracks().forEach(track=>track.stop());stream=null;
  model?.close();model=null;preview.srcObject=null;preview.hidden=true;gate.reset();
  button.textContent='Enable camera';button.setAttribute('aria-pressed','false');message.textContent=text;
 }
 function scan(own){
  if(own!==generation||!enabled)return;
  if(window.ARIAQA&&!window.ARIAQA.canContinue()){stop('Camera off: session ended.');return;}
  try{
   if(preview.readyState>=2&&preview.currentTime!==lastFrame){
    lastFrame=preview.currentTime;
    const result=model.recognizeForVideo(preview,window.performance.now());
    const category=result.gestures?.[0]?.[0];
    const gesture=gate.update(category?.categoryName,category?.score||0,window.performance.now());
    if(gesture){
     const text=gesture==='Open_Palm'?'I can see your open hand. Hello! What would you like to work on together?':'I can see your thumbs-up. What would you like to do next?';
     const accepted=window.ARIAHeart?.reactToGesture?.(text);
     message.textContent=accepted?'Gesture detected — ARIA is responding.':'Gesture detected. Let ARIA finish, then lower your hand and try again.';
    }
   }
   timer=window.setTimeout(()=>scan(own),200);
  }catch{stop('Camera recognition stopped. Select Enable camera to retry.');}
 }
 button.onclick=async()=>{
  if(enabled||pending){stop();return;}
  if(window.ARIAQA&&!window.ARIAQA.canContinue())return;
  if(!navigator.mediaDevices?.getUserMedia){message.textContent='Camera access is unavailable. Open ARIA in a secure browser tab and use Speak meanwhile.';return;}
  const own=++generation;pending=true;button.textContent='Cancel camera setup';message.textContent='Allow camera access when your browser asks.';
  try{
   const acquired=await navigator.mediaDevices.getUserMedia({video:{facingMode:'user',width:{ideal:640},height:{ideal:480}},audio:false});
   if(own!==generation){acquired.getTracks().forEach(t=>t.stop());return;}
   stream=acquired;preview.srcObject=stream;preview.hidden=false;await preview.play();
   if(own!==generation)return;
   message.textContent='Camera preview on. Loading hand recognition…';
   const loaded=await loadModel();
   if(own!==generation){loaded.close();return;}
   model=loaded;pending=false;enabled=true;lastFrame=-1;button.textContent='Turn camera off';button.setAttribute('aria-pressed','true');
   message.textContent='Camera on. Hold an open palm or thumbs-up for one second, then lower your hand. Microphone input uses Speak.';scan(own);
  }catch(error){if(own!==generation)return;stop(error.name==='NotAllowedError'?'Camera permission denied. Allow it in your browser settings to retry.':'Camera setup failed. Check camera availability and internet, then retry.');}
 };
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stop('Camera off while the page is hidden.');});
 window.addEventListener('pagehide',()=>stop());
 document.getElementById('stop')?.addEventListener('click',()=>stop());
 return {stop,button,preview};
}

if(typeof window!=='undefined'&&typeof document!=='undefined')installCamera({document,window,navigator,loadModel:async()=>{
 const {GestureRecognizer,FilesetResolver}=await import('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.32/vision_bundle.mjs');
 const files=await FilesetResolver.forVisionTasks('https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.32/wasm');
 return GestureRecognizer.createFromOptions(files,{baseOptions:{modelAssetPath:'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'},runningMode:'VIDEO',numHands:1});
}});
