# ARIA facial-render check — October 30, 2026

This is an actual new MuseTalk render using the approved facial-motion source and the first three seconds of the existing Heart introduction WAV. It is a technical validation clip, not a new spoken answer or live conversation demo.

The complete output decoded successfully: 75 video frames, 852×1280, 25 fps, and a three-second AAC audio stream. Audio correlation against the supplied Heart segment was 0.99875 after decoding. Sampled frames show generated mouth shapes; visual inspection of frame 66 confirms that the original blink is preserved. The source's lateral gaze remains. The generated lower face looks softer than the original and needs quality work. Pixel measurements in validation.json are diagnostics, not a perceptual synchronization score.

The full Linux CPU run took 588.49 seconds, including model/source preparation; the audio-to-video stage took 341.17 seconds. Peak process RSS was 5,382,888 KiB. These are not Mac benchmarks and do not establish conversational speed. No microphone, local language-model dialogue, newly synthesized Heart response, or full-body animation was verified in this run.

The repeatable check is third_party/MuseTalk-Mac/scripts/validate_render.py. It requires the existing model files and dependencies and refuses a changed approved source. The validation harness is committed separately; no weights are included here. The public ARIA interface, approved source assets, existing Mac installs, and installer pin were not changed. The Mac release remains on hold.
