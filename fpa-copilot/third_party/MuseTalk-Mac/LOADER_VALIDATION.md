# Animation loader validation — October 30, 2026

The UNet loader now constructs its model on the meta device and assigns the checkpoint tensors directly, avoiding a second initialized parameter allocation. ZIP checkpoints use memory mapping; legacy checkpoints load without mmap. Both retain weights_only=True and strict state validation. Missing or mismatched weights fail. The returned model has no meta tensors, is in evaluation mode, and does not track parameter gradients.

Verified locally on Linux with Python 3.12, PyTorch 2.6.0+cpu, Diffusers 0.30.2, and NumPy 1.26.4:

- ZIP and legacy PyTorch checkpoints preserve a small model's output exactly; construction occurs on meta and mmap selection matches checkpoint format.
- Missing keys and incorrect tensor shapes fail.
- The production UNet wrapper, with a small real Diffusers UNet2DConditionModel, preserves its predicted output exactly (zero tolerance).

Command: `OMP_NUM_THREADS=2 python scripts/test_weight_loading.py`. Result: three tests passed. These tests use generated small checkpoints, not ARIA's full production model. Peak memory and performance on the user's Mac are unmeasured.

No approved image, video, Heart voice configuration, portfolio layout, public speech runtime, or installer pin was changed. Existing Mac installations are not automatically updated by this repository patch. The installer remains on release hold; see ../../mac-demo/RELEASE_STATUS.md. This change does not establish a completed neural facial render, natural blinking, new conversation audio, full-body animation, or conversational latency.
