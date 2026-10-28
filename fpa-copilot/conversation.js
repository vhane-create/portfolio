/* A separate conversation page: original approved demo and media remain unchanged. */
(() => {
  const $ = id => document.getElementById(id);
  const audio = new Audio();
  const video = $('aria-heart-video');
  const portrait = document.createElement('img');
  portrait.src = 'liveportrait/aria-approved.png';
  portrait.alt = video.getAttribute('aria-label');
  portrait.hidden = true;
  video.after(portrait);
  let history = [], pending = false, muted = false, generation = 0, controller, mediaURL;
  function stop() {
    generation++; controller?.abort(); audio.pause(); video.pause();
    pending = false; $('send').disabled = false;
    $('screen').dataset.state = 'idle';
    status('Stopped');
  }
  function releaseAudio() { if (mediaURL) URL.revokeObjectURL(mediaURL); mediaURL = null; }
  async function replay() {
    if (!mediaURL) return;
    video.pause(); video.hidden = true; portrait.hidden = false;
    audio.muted = muted;
    try { await audio.play(); $('screen').dataset.state = 'speaking'; status('Speaking with Heart'); }
    catch { status('Answer ready — click Play latest reply to hear it'); }
  }
  const replayButton = document.createElement('button');
  replayButton.textContent = 'Play latest reply'; replayButton.disabled = true;
  replayButton.onclick = replay;
  document.querySelector('.overlay .actions').append(replayButton);
  ask = async function() {
    const question = $('question').value.trim();
    if (!question || pending) return;
    audio.pause(); video.pause();
    video.hidden = true; portrait.hidden = false;
    releaseAudio(); replayButton.disabled = true;
    add('You', question); $('question').value = '';
    pending = true; $('send').disabled = true;
    const own = ++generation;
    controller = new AbortController();
    status('Thinking and preparing Heart speech…');
    const timer = setTimeout(() => controller.abort(), 180000);
    try {
      const response = await fetch('/api/chat', {method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question, history}), signal: controller.signal});
      const result = await response.json();
      if (own !== generation) return;
      if (!response.ok) throw Error(result.error || 'Conversation service unavailable');
      if (typeof result.answer !== 'string' || !result.answer.trim()) throw Error('ARIA returned an empty answer');
      add('ARIA', result.answer);
      history = [...history, {role: 'user', content: question}, {role: 'assistant', content: result.answer}].slice(-12);
      if (result.audio && result.voice === 'af_heart' && result.audio_type === 'audio/wav') {
        const bytes = Uint8Array.from(atob(result.audio), c => c.charCodeAt(0));
        mediaURL = URL.createObjectURL(new Blob([bytes], {type: 'audio/wav'}));
        audio.src = mediaURL; replayButton.disabled = false;
        await replay();
      } else { status(result.speech_error || 'Text answer ready; Heart speech is unavailable'); }
    } catch (error) {
      if (own !== generation) return;
      const message = error.name === 'AbortError' ? 'The reply took too long. Please retry.' : error.message;
      add('ARIA', message); status('Reply unavailable');
    } finally {
      clearTimeout(timer);
      if (own === generation) { pending = false; $('send').disabled = false; }
    }
  };
  $('send').onclick = ask;
  $('stop').onclick = () => { stop(); recognizer?.stop(); };
  $('clear').onclick = () => { stop(); history = []; releaseAudio(); replayButton.disabled = true; $('history').replaceChildren(); status('New conversation'); };
  $('mute').textContent = 'Voice: on';
  $('mute').onclick = () => {
    muted = !muted; audio.muted = muted; video.muted = muted;
    $('mute').textContent = muted ? 'Voice: off' : 'Voice: on';
    $('mute').setAttribute('aria-pressed', String(muted));
  };
  $('intro').onclick = async () => {
    stop(); portrait.hidden = true; video.hidden = false;
    video.src = 'assets/ARIA_Heart_Introduction.mp4'; video.muted = muted;
    try { await video.play(); } catch { status('Introduction could not play'); }
  };
  const sampleButton = [...document.querySelectorAll('button')].find(b => b.textContent === 'Play verified finance reply');
  if (sampleButton) sampleButton.onclick = async () => {
    stop(); portrait.hidden = true; video.hidden = false; video.muted = muted;
    video.src = 'assets/ARIA_Variance_Reply.mp4';
    try { await video.play(); } catch { status('Finance sample could not play'); }
  };
  document.querySelectorAll('[data-aria-topic]').forEach(button => {
    // Replace the old canned topic listener without changing the approved design.
    const replacement = button.cloneNode(true); button.replaceWith(replacement);
    replacement.onclick = () => { $('question').value = 'Explain ' + replacement.textContent.trim(); ask(); };
  });
  // The original speech recognizer calls ask() after a final transcript.
  audio.onended = () => { $('screen').dataset.state = 'idle'; status('Ready for your next question'); };
  audio.onerror = () => status('Heart audio could not play. The text answer is available.');
  const note = document.querySelector('main > .note');
  if (note) note.textContent = 'Ask ARIA a question, then follow up. New replies use Heart speech with her approved portrait. New speech does not yet have matching lip movements. The introduction remains lip-synced.';
  document.querySelectorAll('.aria-topic-note').forEach(el => { el.textContent = 'Choose a topic or ask your own question.'; });
  document.querySelector('footer').textContent = 'ARIA conversation demo · Questions and recent turns are sent to the AI provider to answer you. Conversation memory stays in this tab; Clear conversation resets it. Avoid confidential information.';
  $('history').replaceChildren();
  add('ARIA', "Hello, I'm ARIA. What would you like to talk about?");
  status('Checking conversation service…');
  fetch('/health').then(r => r.json()).then(result => status(result.status === 'ready' ? 'Ready to converse with Heart' : 'Conversation service needs setup')).catch(() => status('Conversation service is not connected'));
})();
