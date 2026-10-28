# ARIA feature and test status

Verified working version: October 28, 2026. This report separates direct user acceptance on an Apple M4 Mac from automated checks in the packaging workspace.

| Feature | Status | Runtime / limitation |
|---|---|---|
| Exact approved Black female android portrait, black executive suit, long wavy black hair, subtle robotic details | Included and checksum verified | No replacement avatar generated |
| Heart voice (`af_heart`) | Confirmed by user for introduction and new finance answer | Kokoro CPU service for new speech; WAVs/MP4 audio included |
| Natural mouth motion matching words | User confirmed for introduction and generated variance answer | MuseTalk V1.5; not a general guarantee for every future utterance |
| Teeth, smiles, eye and head motion | User reported visible teeth and facial/eye motion in source animation | Source motion is cycled/reversed to cover longer replies |
| Blinking quality | Not separately confirmed in final acceptance | Driven by the source animation; no distinct blink rig or 3D model |
| Intro and verified finance clip on GitHub Pages | Included, playable without backend | Static recorded videos, identified as such |
| Newly generated spoken and lip-synced replies | Confirmed by user on Mac | Local Python environments, model downloads, mounted USB and Apple GPU required; minutes per render |
| Audio-only replies | Implemented and service transport tested with synthetic audio | Real Heart synthesis tested separately; no mouth synchronization in this mode |
| Actual-versus-budget calculation | Confirmed 120,000 minus 100,000 = 20,000 and 20% | Browser calculation; zero-budget percentage handled |
| Department FP&A example and materiality slider | Existing deterministic engine retained and tested | Synthetic sample data; `index.html` |
| Financial modeling, budgeting, forecasting, scenarios and strategic analysis | Implemented as explanatory topic responses | No automatic spreadsheet, integrated financial model or company forecast builder |
| Company/general research | Wikipedia reference lookup implemented | Requires network; packaging does not establish current data accuracy or endpoint availability |
| Arbitrary AI reasoning | Optional OpenAI backend source included | Requires `OPENAI_API_KEY`, secret demo token and backend deployment; not connected to or verified in the working Heart page |
| Microphone recognition | Browser implementation retained | Browser/service permission dependent; not separately verified in final acceptance |
| Stop/mute/replay controls | Implemented; syntax and service checks completed | Stop ends playback/polling; an existing render can finish in background |
| Instant real-time streaming conversation | Not implemented | Videos render before playback |
| Document/spreadsheet upload, persistent chat memory, public voice backend | Not implemented in working flow | No claims of production deployment |

## Packaging validation

See `VALIDATION_REPORT.json` for actual results. Includes archive integrity, uploaded checksums, portrait identity, MP4 stream/decoding checks, WAV inspection, JavaScript syntax, finance engine tests, local service tests with a synthetic pipeline, LivePortrait portable tests, and syntax checks on application/install Python. Workspace checks do not claim Apple GPU inference ran here. The user separately confirmed the actual Mac end-to-end render and playback.

Model weights are external downloads. See `MODEL_ASSETS.md` and `THIRD_PARTY_NOTICES.md` for licensing boundaries, including InsightFace model restrictions. This package is a portfolio/demo handoff, not a commercial-model clearance or certification of finance advice.
