# External model assets and source provenance

The ZIP includes the approved portrait, neural source animation, accepted speaking videos, WAV files, configurations and application/model-wrapper source. It does **not** include installed Conda/venv directories, platform binaries or multi-gigabyte checkpoints. Static playback does not need them. Generating new speech/animation does.

| Component | Source / location | Included vs external |
|---|---|---|
| Approved ARIA PNG | `liveportrait/aria-approved.png` | Included byte for byte; SHA-256 in README and manifest |
| Source expression/head motion | `assets/aria-approved--d0.mp4` | Included, 78 frames / 3.12 seconds, no audio |
| Speaking intro | `assets/ARIA_Heart_Introduction.mp4` | Included, 5.25 seconds, H.264 + AAC |
| Accepted finance answer | `assets/ARIA_Variance_Reply.mp4` | Included, 16.925 seconds, H.264 + AAC |
| Heart voice model and voice vector | https://huggingface.co/hexgrad/Kokoro-82M (`af_heart`) | Downloaded by Kokoro; not bundled |
| English text processing | spaCy `en_core_web_sm` and Misaki | Downloaded/installed in the Heart environment; not bundled |
| MuseTalk V1.5 | https://huggingface.co/TMElyralab/MuseTalk (`musetalkV15/unet.pth`, `musetalk.json`) | External; UNet about 3.4 GB |
| SD VAE | https://huggingface.co/stabilityai/sd-vae-ft-mse | External config and `diffusion_pytorch_model.bin` |
| Whisper tiny | https://huggingface.co/openai/whisper-tiny | External encoder weights/config/preprocessor |
| Face parser | https://github.com/zllrunning/face-parsing.PyTorch and port download script | External `79999_iter.pth` and ResNet18 weights |
| LivePortrait weights | https://huggingface.co/KlingTeam/LivePortrait/tree/82a4fa6735ca58432b6ce39301b4b9ee066dea47 | External, needed only to regenerate source motion; see its model terms |

## Bundled source snapshots

- `third_party/MuseTalk-Mac`: https://github.com/barnent1/musetalk-mac at `7fd019315127d7f31e2e7f9853547ddceabbeb6e`. Text/code/config/license files are bundled; sample binary media and weights are excluded.
- `third_party/LivePortrait`: https://github.com/KlingAIResearch/LivePortrait at `9b294b3d0536135442ea73cb01e6cb3ca7029dd3`. Text/code/config/license files are bundled; third-party binaries, sample media and weights are excluded.
- Missing MuseTalk VAE/UNet wrapper source was restored from https://github.com/TMElyralab/MuseTalk at `0a89dec45a0192b824e3cf4daf96c239440c5ed8`. The uploaded Mac copies, including the memory fix, are preserved in `working-runtime/` and applied to the bundled MuseTalk tree.

## Working Mac fixes and settings

`unet.py` loads checkpoint weights onto CPU with `weights_only=True`, copies them into the model, then deletes the temporary weight dictionary before device transfer. `utils.py` moves full datagen batches onto the chosen device. The exact uploaded files are retained, not reconstructed from screenshots. The run uses `--use_float16 --batch_size 1` and MPS watermarks 0.7/0.5. Audio processing uses Kokoro 0.9.4, `af_heart`, mono 24 kHz PCM WAV and CPU with two threads.

The default USB is `/Volumes/NO NAME`; model symlink under `~/ARIA-LivePortrait/MuseTalk-Mac/upstream/models` points to its `ARIA-MuseTalk-Models` directory. Keep that drive mounted for new lip-synced answers. The FAT32 device used in testing accepts the 3.4 GB UNet but cannot store individual files at or above its per-file limit; do not assume every future checkpoint will fit.

The setup script downloads required weights via the bundled port script. These endpoints may change. Initial download requires internet access; interrupted downloads may need retry. Excluding checkpoints keeps the handoff small and avoids implying redistribution or commercial clearance of every model. Review the current model cards and licenses before a business deployment.
