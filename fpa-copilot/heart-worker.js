import { KokoroTTS } from 'https://cdn.jsdelivr.net/npm/kokoro-js@1.2.1/dist/kokoro.web.js';
let model, loading, running = false, pending = null, generation = 0;
async function load() {
  if (!loading) loading = KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX', {
    dtype: 'q8', device: 'wasm', progress_callback: p => {
      if (p.status === 'progress') postMessage({type: 'progress', progress: Math.round(p.progress || 0)});
    }
  }).then(m => model = m).catch(e => { loading = null; throw e; });
  return loading;
}
function wav(samples, rate) {
  if (!(samples instanceof Float32Array) || !samples.length || !Number.isFinite(rate) || rate <= 0) throw Error('Invalid audio');
  const buffer = new ArrayBuffer(44 + samples.length * 2), v = new DataView(buffer);
  const text = (offset, s) => [...s].forEach((c, i) => v.setUint8(offset + i, c.charCodeAt(0)));
  text(0, 'RIFF'); v.setUint32(4, buffer.byteLength - 8, true); text(8, 'WAVE'); text(12, 'fmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  text(36, 'data'); v.setUint32(40, samples.length * 2, true);
  for (let i = 0; i < samples.length; i++) { const s = Math.max(-1, Math.min(1, samples[i])); v.setInt16(44 + i * 2, s * (s < 0 ? 32768 : 32767), true); }
  return buffer;
}
function splitText(text) {
  // Model input is bounded by words, with no dropped sentences or arbitrary clipping.
  const chunks = []; let part = '';
  for (const word of text.trim().split(/\s+/)) {
    if (part && part.length + word.length > 220) { chunks.push(part); part = ''; }
    part += (part ? ' ' : '') + word;
    if (/[.!?]$/.test(word)) { chunks.push(part); part = ''; }
  }
  if (part) chunks.push(part);
  return chunks;
}
async function drain() {
  if (running) return;
  running = true;
  try {
    while (pending) {
      const job = pending, own = generation; pending = null;
      try {
        await load();
        for (const text of splitText(job.text)) {
          if (own !== generation) break;
          const output = await model.generate(text, {voice: 'af_heart', speed: 1});
          if (own !== generation) break;
          const buffer = wav(output.audio, output.sampling_rate);
          postMessage({type: 'audio', id: job.id, buffer}, [buffer]);
        }
        if (own === generation) postMessage({type: 'done', id: job.id});
      } catch {
        if (own === generation) postMessage({type: 'error', id: job.id, message: 'Heart speech could not be generated. Your text answer is still available.'});
      }
    }
  } finally { running = false; }
}
self.onmessage = ({data}) => {
  if (data.type === 'init') return load().then(() => postMessage({type: 'ready', id: data.id})).catch(() => postMessage({type: 'load-error', message: 'Heart could not load. Check your connection and retry.'}));
  if (data.type === 'cancel') { generation++; pending = null; return; }
  if (data.type !== 'speak' || typeof data.text !== 'string' || !data.text.trim() || data.text.length > 6000) return;
  generation++; pending = data;
  return drain();
};
