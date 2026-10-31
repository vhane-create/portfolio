# Five-minute ARIA conclusion: integration component

This component is prepared for the interactive conclusion. It is not connected to the published tour, a public reasoning service, or a live avatar renderer yet.

Implemented and locally tested:

- A maximum 300-second session; expiry stops microphone capture, speech, gesture playback and in-flight requests.
- Session-local follow-up history; a fresh session clears it.
- Low-confidence or empty speech requests repetition rather than sending a guessed question to the model.
- The explicit voice command “ARIA, come shake my hand” dispatches a virtual-handshake action without resetting the deadline.
- Missing gesture integration reports unavailable rather than pretending the movement occurred.
- Stale replies after expiration or restart cannot play.

The integration must supply real `ask`, `speak`, `gesture`, `stopMedia` and `stopListening` adapters. `speak` must use the approved af_heart audio and drive the approved ARIA's actual facial animation; `gesture` must use an actual connected animation. Configure a maximum 300-second duration on the streaming provider too. A client timer alone is not a server-side streaming limit.

The 30-second recorded conclusion and the maximum five-minute live question session are separate. The recorded conclusion walks back to the conference table, sits down, invites questions and mentions five minutes. It is not a substitute for live Q&A.

Run: `node --test fpa-copilot/employer-tour/qa-session.test.mjs`

The tests use controlled providers and clocks. They do not establish that microphone transcription, live model inference, Heart streaming, full-body gesture rendering or lip synchronization works in production.
