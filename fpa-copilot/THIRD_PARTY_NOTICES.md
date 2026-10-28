# Third-party and asset notices

The project includes third-party source under its original notices. No blanket license in this package overrides individual source/model terms.

## Bundled code

- LivePortrait source: copyright Kuaishou Visual Generation and Interaction Center; MIT code license retained in `third_party/LivePortrait/LICENSE`. Its license separately states that **InsightFace models are restricted to non-commercial research**, and that commercial use requires replacing the detection models. Model weights are not bundled.
- MuseTalk source and Apple Silicon port: Tencent Music Entertainment Group and Glen Barnhardt. Original MIT notices and dependency-license information are preserved in `third_party/MuseTalk-Mac/LICENSE` and `third_party/MuseTalk-Mac/upstream/LICENSE`. The restored `vae.py` and `unet.py` wrappers are derived from official MuseTalk code under that notice.
- The copied `working-runtime/musetalk/` wrapper/utility files retain the MuseTalk upstream attribution and are covered by the notices included above. Local patches are described in `MODEL_ASSETS.md`.

## Installed or downloaded, not bundled

Kokoro, Misaki, PyTorch, transformers, spaCy, NumPy, soundfile, FFmpeg, MediaPipe, OpenCV, Diffusers, the voice/language models and neural checkpoints each retain their own licenses. The package provides requirements and download instructions, not an all-in-one offline redistribution of those products. FFmpeg build license obligations depend on the actual build. Model usage terms must be checked independently of the wrapper code's MIT license.

Kokoro project: https://github.com/hexgrad/kokoro (Apache-2.0 source declaration); model card: https://huggingface.co/hexgrad/Kokoro-82M. Misaki: https://github.com/hexgrad/misaki. LivePortrait: https://github.com/KlingAIResearch/LivePortrait. MuseTalk: https://github.com/TMElyralab/MuseTalk. Apple port: https://github.com/barnent1/musetalk-mac.

## Project-owned inputs and generated outputs

The approved ARIA portrait and generated videos/audio were provided and approved by the project owner and are included unchanged. This archive does not establish or grant third-party likeness, trademark or commercial-model rights. No alternative face, private driver recording, personal photo backup, user screenshot or account credential is included.

## Reference lookup attribution

The interface identifies Wikipedia when displaying retrieved reference content and links to the source article. Retrieved material remains subject to Wikipedia's applicable attribution/license requirements. A reference lookup is not independent validation of financial data.
