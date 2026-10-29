# ARIA no-subscription development mode

Optional basic text reasoning runs on the visitor's device through WebLLM and Qwen2.5-0.5B-Instruct. Heart speech uses the existing fixed af_heart voice. ARIA's approved full-body portrait is unchanged.

Select Voice & controls, then Download and use free AI. Model loading is opt-in and requires WebGPU and roughly 1 GB graphics memory, plus memory for the browser and Heart. Model downloads need internet and storage. This small model is not equivalent to ChatGPT and has not been validated for enterprise financial decisions.

In selected free mode, questions are not sent to the paid reasoning API. Loading or generation failures do not silently fall back to the cloud. Supplied text is limited to 4,000 characters; recent history plus the question and supplied text must fit a smaller context. Limits are explicit rather than silently dropping information. Deterministic finance calculations remain available.

Local text reasoning and Heart generation do not make microphone transcription private: browser SpeechRecognition may use the browser provider's remote services. A fully self-hosted company version still needs local transcription, an appropriate larger model, deployment support and data controls.

Walking, body gestures, natural blink control and new speech lip sync are NOT implemented. The historic LivePortrait package includes InsightFace model restrictions; it is not commercial clearance for a company animation rollout. Full-body animation needs an appropriately licensed rigged model and animation system.

Automated checks cover opt-in state, unsupported-device handling, absence of silent cloud fallback, and JavaScript syntax. Actual on-device inference and speech integration require browser/hardware acceptance testing.

References:
- https://webllm.mlc.ai/docs/
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
- https://huggingface.co/hexgrad/Kokoro-82M
- https://github.com/deepinsight/insightface
