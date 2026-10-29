import { KokoroTTS } from 'https://cdn.jsdelivr.net/npm/kokoro-js@1.2.1/dist/kokoro.web.js';
let model, loading, busy = false;
async function load() {
  if (!loading) loading = KokoroTTS.from_pretrained('onnx-community/Kokoro-82M-v1.0-ONNX', {
    dtype: 'q8', device: 'wasm', progress_callback: p => {
      if (p.status === 'progress') postMessage({type: 'progress', progress: Math.round(p.progress || 0)});
    }
  }).then(m => model = m).catch(e => { loading = null; throw e; });
  return loading;
}
function wav(samples, rate) {
  const buffer = new ArrayBuffer(44 + samples.length * 2), v = new DataView(buffer);
  const text = (offset, s) => [...s].forEach((c, i) => v.setUint8(offset + i, c.charCodeAt(0)));
  text(0, 'RIFF'); v.setUint32(4, buffer.byteLength - 8, true); text(8, 'WAVE'); text(12, 'fmt ');
  v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
  v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
  text(36, 'data'); v.setUint32(40, samples.length * 2, true);
  for (let i = 0; i < samples.length; i++) { const s = Math.max(-1, Math.min(1, samples[i])); v.setInt16(44 + i * 2, s * (s < 0 ? 32768 : 32767), true); }
  return buffer;
}
self.onmessage = async ({data}) => {
  const {type, id, text} = data;
  if (busy) { postMessage({type: 'error', id, message: 'Heart is still preparing a reply. Please wait.'}); return; }
  busy = true;
  try {
    await load();
    if (type === 'init') { postMessage({type: 'ready', id}); return; }
    // Bound chunks to avoid the model token truncation that affects long paragraphs.
    const chunks = text.match(/[^.!?]+[.!?]*/g) || [text];
    for (const sentence of chunks) {
      const words = sentence.trim().split(/\s+/); let part = '';
      for (const word of [...words, '']) {
        if (part && (part.length + word.length > 240 || !word)) {
          const output = await model.generate(part, {voice: 'af_heart', speed: 1});
          const buffer = wav(output.audio, output.sampling_rate);
          postMessage({type: 'audio', id, buffer}, [buffer]); part = '';
        }
        if (word) part += (part ? ' ' : '') + word;
      }
    }
    postMessage({type: 'done', id});
  } catch { postMessage({type: 'error', id, message: 'Heart voice could not load or generate speech. Check your connection and try again.'}); }
  finally { busy = false; }
};
