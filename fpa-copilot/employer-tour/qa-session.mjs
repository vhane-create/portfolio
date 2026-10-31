export const QA_LIMIT_MS = 5 * 60 * 1000;
export const REPEAT_QUESTION = 'Can you repeat that? I couldn’t hear your question clearly.';
export function voiceAction(transcript) {
  const text = String(transcript || '').toLowerCase().replace(/[.,!?—–-]/g, ' ').replace(/\s+/g, ' ').trim();
  return /^(?:hey )?aria (?:please )?(?:come (?:and )?)?(?:please )?shake my hand(?: please)?$/.test(text) ? 'virtual-handshake' : null;
}

export class QASession {
  constructor({clock = () => performance.now(), ask, speak, gesture, stopMedia = () => {}, stopListening = () => {}, onState = () => {}}) {
    this.clock = clock;
    this.askProvider = ask;
    this.speakProvider = speak;
    this.gestureProvider = gesture;
    this.stopMedia = stopMedia;
    this.stopListening = stopListening;
    this.onState = onState;
    this.history = [];
    this.epoch = 0;
    this.active = false;
    this.busy = false;
    this.state = 'off';
  }
  setState(state) { this.state = state; this.onState(state); }
  start() {
    this.stop('restarted');
    this.history = [];
    this.deadline = this.clock() + QA_LIMIT_MS;
    this.active = true;
    this.setState('listening');
    return this.deadline;
  }
  remainingMs() { return this.active ? Math.max(0, this.deadline - this.clock()) : 0; }
  checkDeadline() {
    if (this.active && this.clock() >= this.deadline) this.stop('expired');
    return this.active;
  }
  stop(reason = 'stopped') {
    this.active = false;
    this.epoch++;
    this.controller?.abort();
    this.controller = null;
    this.busy = false;
    this.stopListening();
    this.stopMedia();
    this.setState(reason);
  }
  clear() { this.stop('cleared'); this.history = []; }
  async gesture(action) {
    if (!this.checkDeadline()) return {status: 'expired'};
    if (!this.gestureProvider) return {status: 'unavailable', action};
    this.controller?.abort();
    this.stopListening();
    this.stopMedia();
    const own = ++this.epoch;
    const controller = new AbortController();
    this.controller = controller;
    this.busy = true;
    this.setState('gesturing');
    try {
      await this.gestureProvider(action, {signal: controller.signal});
      return this.checkDeadline() && own === this.epoch ? {status: 'gesture', action} : {status: 'expired'};
    } catch (error) {
      return !this.checkDeadline() || error.name === 'AbortError' ? {status: 'expired'} : {status: 'error', message: error.message};
    } finally {
      if (own === this.epoch) {
        this.busy = false;
        this.controller = null;
        if (this.checkDeadline()) this.setState('listening');
      }
    }
  }
  async heard(transcript, confidence) {
    if (!this.checkDeadline()) return {status: 'expired'};
    const action = voiceAction(transcript);
    if (action && !(Number.isFinite(confidence) && confidence > 0 && confidence < .55)) return this.gesture(action);
    if (this.busy) return {status: 'busy'};
    const question = String(transcript || '').trim();
    // Zero/missing confidence often means the browser did not provide a score.
    const unclear = !question || (Number.isFinite(confidence) && confidence > 0 && confidence < .55);
    const own = this.epoch;
    const controller = new AbortController();
    this.controller = controller;
    this.busy = true;
    this.stopListening();
    const current = () => this.checkDeadline() && own === this.epoch && !controller.signal.aborted;
    try {
      if (unclear) {
        this.setState('clarifying');
        // Renderer receives an explicit action, never an unrelated saved answer.
        await this.speakProvider(REPEAT_QUESTION, {signal: controller.signal, action: 'approach-and-repeat'});
        return current() ? {status: 'repeat'} : {status: 'expired'};
      }
      if (question.length > 500) return {status: 'too-long'};
      this.setState('thinking');
      const answer = await this.askProvider(question, this.history.slice(-20), controller.signal);
      if (!current()) return {status: 'expired'};
      if (typeof answer !== 'string' || !answer.trim()) throw new Error('ARIA returned no answer.');
      this.history.push({role: 'user', content: question}, {role: 'assistant', content: answer});
      this.history = this.history.slice(-20);
      this.setState('speaking');
      await this.speakProvider(answer, {signal: controller.signal, action: 'seated-answer'});
      return current() ? {status: 'answered', answer} : {status: 'expired'};
    } catch (error) {
      if (!current() || error.name === 'AbortError') return {status: 'expired'};
      return {status: 'error', message: error.message || 'The answer is unavailable.'};
    } finally {
      if (own === this.epoch) {
        this.busy = false;
        this.controller = null;
        if (this.checkDeadline()) this.setState('listening');
      }
    }
  }
}

export function attachHardLimit(session, {requestFrame = requestAnimationFrame, schedule = setTimeout, cancel = clearTimeout, documentRef = document} = {}) {
  let timeout;
  const begin = session.start.bind(session);
  session.start = () => {
    cancel(timeout);
    const deadline = begin();
    timeout = schedule(() => session.checkDeadline(), QA_LIMIT_MS);
    return deadline;
  };
  const frame = () => { session.checkDeadline(); requestFrame(frame); };
  requestFrame(frame);
  documentRef.addEventListener('visibilitychange', () => {
    // Hidden/suspended tabs cannot continue listening or resume a stale session.
    if (documentRef.hidden && session.active) session.stop('paused');
    else session.checkDeadline();
  });
  documentRef.defaultView?.addEventListener('pagehide', () => session.stop('closed'));
  return session;
}
