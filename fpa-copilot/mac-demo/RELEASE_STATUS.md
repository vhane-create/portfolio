# Release hold — conversation and facial motion

The earlier installer ZIPs are superseded development packages. Do not present
them as a finished, tested-on-Mac product. No new download is being requested
while the remaining hardware validation is unresolved.

The remote software audit fixed explicit local-model selection, malformed model
responses, interrupted installation writes, video byte-range delivery, and recovery
when a canceled answer’s render is still active. See `VALIDATION_REPORT.json` for
the exact checks and the unverified capabilities. The report covers source release
`8b13db6cc48e90222418dc1aac87b90ffbcce427`.

The release cannot pass its final gate in this Linux workspace: it requires the
configured Apple Silicon Mac, its actual LM Studio model, the existing Kokoro and
MuseTalk environments, and the model USB. The following still need direct evidence:

1. A new answer, then a relevant follow-up, using a real local model and Heart.
2. A newly rendered reply with the approved face, audible Heart, correct lip timing,
   and acceptable eye/head/neck movement. Existing prerecorded media does not count.
3. Microphone input and the next listening turn after video playback.
4. Measured cold/warm response times short enough for the intended conversation.

The current render-before-playback design may take minutes. The audit has not
removed that architectural limitation or established natural conversation speed.
Full-body movement is outside this repair and no paid service is enabled.
