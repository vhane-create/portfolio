# ARIA body animation — development path, not deployed

Netta’s target is a humanlike full-body colleague: direct conversational attention,
natural blinks, facial reactions, relaxed posture and smooth hand/arm/body movement.
Keep the exact approved ARIA face, hair, suit, android details and `af_heart` voice.
The supplied `aria-approved--d0.mp4` remains the appearance/motion baseline;
`IMG_2601.mp4` illustrates physical delivery, not a replacement identity or voice.
Do not add a repeating clip and call it live conversation.

## Implemented here

`render_body.py` prepares an **offline experimental render**, using ARIA’s exact
full-body image and an existing Heart WAV as inputs to EchoMimicV3 Flash. It checks
the source image hash, rejects unsupported long replies, verifies the upstream
checkout, reports missing runtime/models, and uses a unique directory per run.
It pads only the model-conditioning audio to the temporal grid, then copies the
original Heart audio stream into the final MKV. It does not create a new voice.
No new paid API, subscription, downloads, hosting or public endpoints are enabled.

Input identity checks do not guarantee generated identity. A successful render
must be reviewed for face/suit consistency, eyes, fingers, posture, movement,
lip timing and temporal artifacts before being added to the public application.

## Current blocker

The development workspace has no available NVIDIA CUDA GPU, PyTorch installation,
animation model weights or animation worker. No animation has been generated or
visually approved with this integration. The website remains unchanged.

The upstream documents Linux/CUDA and NVIDIA GPUs. Its Flash release advertises a
12 GB VRAM path, but this runner’s actual peak memory and latency are unmeasured;
do not assume this exact command fits a 12 GB GPU. No Apple Silicon support is
verified. Existing free Render reasoning hosting is not an animation GPU worker.

## Runtime preparation on a compatible GPU machine

Follow the official project installation/model instructions, then check out the
reviewed code revision:

```bash
git clone https://github.com/antgroup/echomimic_v3.git
git -C echomimic_v3 checkout 7e89489ca51c0d008fc1963ec6c03fc5bd0b9397
```

Use a dedicated environment for the upstream requirements. Prepare these model
components in one weights directory, using the model links in the upstream README:

```
weights/
  Wan2.1-Fun-V1.1-1.3B-InP/
  chinese-wav2vec2-base/
  transformer/diffusion_pytorch_model.safetensors
```

The runner pins code but does not yet pin/checksum every model component. Review
and record model revisions and all dependent licenses before production use.

From `fpa-copilot/`, with a short WAV produced by the existing Heart generator:

```bash
python body-animation/render_body.py --repo /path/echomimic_v3 --weights /path/weights --heart-audio /path/heart.wav --check
```

Remove `--check` to attempt an offline render after the environment is ready.
Initial supported audio duration is **0.5–3.2 seconds**. Longer answer rendering,
seamless chunk stitching, live service integration, interruption handling and
streaming are not implemented. Walking is not guaranteed by this talking-body
experiment; directed locomotion requires a separately validated motion pipeline
or rigged character.

## Validation completed

Three automated checks passed: changed source identity is rejected, overlong
speech is rejected rather than truncated, and a short answer fits the model’s
temporal grid. A real generated 3.05-second Heart greeting passed input checks;
environment checking correctly reported missing runtime/models. Neural rendering,
English lip synchronization, movement quality, memory use and latency were not run.

## Primary sources reviewed October 29, 2026

- https://github.com/antgroup/echomimic_v3 — audio-driven animation, Flash requirements and license information.
- https://github.com/Wan-Video/Wan-Animate-2 — reference-image/driving-video animation candidate for whole-body motion; its documented multi-GPU setup is not connected to ARIA.

These are development candidates, not a claim that ARIA has real-time walking or
conversation animation. Self-hosting can avoid a software subscription while
still requiring compute hardware, electricity and maintenance.
