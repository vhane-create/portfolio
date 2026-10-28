# ARIA working version — October 28, 2026

## Confirmed on the user's MacBook Air M4

- The exact approved Black female android portrait, long wavy black hair, black executive suit, and subtle robotic details was retained. Approved source SHA-256: `9889d86d17f07437243204107a91ed7ab4a49a5a9d1841ec56c59d117247d958`.
- LivePortrait generated the approved source animation. The user reported facial/eye movement, smiles and visible teeth.
- MuseTalk generated the Heart introduction. The user confirmed the voice and matching mouth movements.
- Kokoro generated a new finance sentence on the Mac using `af_heart`.
- The local browser service generated and played a new actual-versus-budget answer with Heart and matching lip movements. The user confirmed both.
- Actual 120,000 minus budget 100,000 returned variance 20,000 and 20%.

## Checks completed in the development workspace

- Six HTTP/service tests passed with a synthetic audio pipeline: submission/WAV delivery, input limits, local origin and file restrictions, source preservation, serialized jobs, and renderer error propagation.
- Embedded JavaScript passed syntax checks. Preview installer refuses to overwrite files.
- These checks are not a claim that real Kokoro or MPS inference ran in this workspace; real inference was confirmed separately by the user on the Mac.

## Requires a running backend

New speech uses the local CPU Kokoro model. Matching mouth motion requires the local MuseTalk Python environment, Apple GPU and mounted USB. The successful render used float16, batch size 1, GPU high watermark 0.7 and low watermark 0.5. New replies take minutes to generate; real-time conversation is not implemented. Audio-only mode has no synchronized mouth animation. Stop ends playback/polling; an in-progress render can finish in the background.

The optional `live-backend` OpenAI service requires an API key and access token. It is separate from the working encyclopedia/finance/Heart flow and is not yet verified or deployed as part of it. GitHub Pages only serves static content; public generation needs separate hosting.

## Features limited or not implemented

Finance buttons explain modeling, budgeting, forecasts, scenarios and business analysis. They are not a spreadsheet modeling engine or automatic company-specific financial forecast. Existing encyclopedia lookup depends on Wikipedia availability. Document uploads, spreadsheet ingestion, persistent conversation memory, streaming animation and a public dynamic service are not implemented in this working flow. Microphone recognition, audio-only controls and individual blink quality were not separately confirmed in the final browser acceptance check.

## Preservation and packaging

Existing portfolio pages were not replaced. `aria-heart-preview.html` was created separately; the live local page is assembled in memory. `heart-backend` code and preview installer are committed to GitHub. The exact MP4/WAV assets and three local MuseTalk source fixes must be collected from the Mac/USB. A final downloadable deployment ZIP cannot be complete without those assets. Model weights and third-party source retain their own license terms; do not imply all model licenses are the same or that offline redistribution has been approved.

