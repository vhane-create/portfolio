# Post-tour question window

The `after-tour=1` conversation page now starts one five-minute countdown. At expiry it stops the existing microphone/audio/renderer, aborts in-flight reasoning, discards late replies, and blocks restarting input in that visit. Standalone prototype visits retain their existing behavior. Browsers still control microphone permission and speech-recognition availability.

Six automated tests pass, including the actual inline page wiring with controlled DOM, clocks and cancellation callbacks. JavaScript syntax checks pass. These checks do not establish live microphone recognition, public reasoning, audible Heart generation, or natural live lip synchronization.

The recorded conference-room conclusion is not yet replaced with a full approved Runway lip-sync render. The old MuseTalk conclusion was rejected and must not be appended. Runway browser sign-in is required to continue the approved Character Script to Video / Act-Two workflow.

This change adds a client-side time limit to the existing conversation page. It does not provide a live avatar service, a new server-side session limit, conversational walking or a handshake animation.

Run `node --test fpa-copilot/qa-window.test.cjs`.
