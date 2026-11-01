/* A five-minute window for the post-tour conversation, not a live-avatar provider. */
(function (root) {
  function create({now = Date.now, monotonic = () => performance.now(), schedule = setTimeout,
    cancel = clearTimeout, onExpire = () => {}, limit = 300000} = {}) {
    const wallStart = now(), monoStart = monotonic();
    let open = true, timer;
    const remainingMs = () => Math.max(0, limit - Math.max(now() - wallStart, monotonic() - monoStart));
    function stop(reason = 'expired') {
      if (!open) return;
      open = false; cancel(timer); onExpire(reason);
    }
    function canContinue() {
      if (open && remainingMs() <= 0) stop();
      return open;
    }
    function tick() {
      if (canContinue()) timer = schedule(tick, remainingMs());
    }
    timer = schedule(tick, limit);
    return {canContinue, remainingMs: () => open ? remainingMs() : 0, stop};
  }
  if (typeof module === 'object' && module.exports) module.exports = {create};
  else root.ARIAQuestionWindow = {create};
})(typeof window === 'object' ? window : this);
