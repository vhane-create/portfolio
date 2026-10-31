// Integration candidate. Not imported by the published tour. Requires a trained,
// approved custom ARIA face and a server-issued token; no API keys in this file.
// Official SDK contract: https://github.com/simliai/simli-client
export class SimliAvatar {
  constructor({SimliClient, logLevel, video, audio, mintToken, clock=()=>performance.now()}) {
    Object.assign(this,{SimliClient,logLevel,video,audio,mintToken,clock});
  }
  async start({deadline,signal}) {
    if (!Number.isFinite(deadline) || deadline<=this.clock() || deadline-this.clock()>300000)
      throw new Error('A Q&A deadline of at most five minutes is required.');
    this.deadline=deadline;
    const {session_token}=await this.mintToken(signal);
    if(signal?.aborted || this.clock()>=deadline) throw new DOMException('Session ended','AbortError');
    this.client=new this.SimliClient(session_token,this.video,this.audio,null,this.logLevel);
    // Schedule before connection so startup cannot extend the five-minute window.
    this.timer=setTimeout(()=>{this.stop().catch(()=>{});},Math.max(0,deadline-this.clock()));
    this.startAbort=()=>{this.stop().catch(()=>{});};
    this.startSignal=signal;
    signal?.addEventListener('abort',this.startAbort,{once:true});
    try { await this.client.start(); }
    catch(error) { await this.stop(); throw error; }
    if(signal?.aborted || this.clock()>=deadline) {await this.stop();throw new DOMException('Session ended','AbortError');}
  }
  async speakPCM16(pcm,{signal}={}) {
    if(!this.client || this.clock()>=this.deadline) throw new Error('The question session has ended.');
    if(!(pcm instanceof Uint8Array) || pcm.length%2) throw new Error('Heart audio must be PCM16, 16 kHz, mono.');
    if(signal?.aborted) throw new DOMException('Answer cancelled','AbortError');
    const client=this.client;
    await new Promise((resolve,reject)=>{
      let speaking=false;
      const cleanup=()=>{client.off('speaking',onSpeaking);client.off('silent',onSilent);client.off('stop',onStop);signal?.removeEventListener('abort',onAbort);clearTimeout(timer);};
      const finish=(error)=>{cleanup();error?reject(error):resolve();};
      const onSpeaking=()=>{speaking=true;};
      const onSilent=()=>{if(speaking)finish();};
      const onStop=()=>finish(new DOMException('Session ended','AbortError'));
      const onAbort=()=>{client.ClearBuffer();finish(new DOMException('Answer cancelled','AbortError'));};
      const timer=setTimeout(()=>{client.ClearBuffer();finish(new DOMException('Session ended','AbortError'));},Math.max(0,this.deadline-this.clock()));
      client.on('speaking',onSpeaking);client.on('silent',onSilent);client.on('stop',onStop);
      signal?.addEventListener('abort',onAbort,{once:true});
      try {client.sendAudioData(pcm);} catch(error) {finish(error);}
    });
  }
  async stop() {
    clearTimeout(this.timer);
    this.startSignal?.removeEventListener('abort',this.startAbort);
    const client=this.client;
    this.client=null;
    this.audio.pause();
    this.video.pause();
    for(const element of [this.audio,this.video]) {
      for(const track of element.srcObject?.getTracks?.() || [])track.stop();
    }
    if(client) {
      try {client.ClearBuffer();} catch {} // Local media must stop even if signaling has already closed.
      await client.stop();
    }
  }
}
