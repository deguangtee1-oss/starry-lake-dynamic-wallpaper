# Pipeline and version lineage

## Local inventory

The Obsidian project archive contains V7, V8, V9, V10 and V11 MP4 files. V7 is also present in Downloads. A still reference exists in the archive, but it is a flattened reference image rather than an editable layered project. The public repository intentionally omits all visual files until redistribution rights are confirmed.

## Script coverage

- `scripts/create_v8_refined.py`: reads V7; adds a low-amplitude, time-periodic brightness/reflection field inside an inset water mask. It does not shift pixels. The source video supplies the rest of the scene and its baked motion.
- `scripts/create_v9.py`: uses V8 as its source; computes temporal sky median to detect/repair old streaks and draws two meteor events. Output is 30 FPS.
- `scripts/create_v10.py`: uses V9; aligns the two new meteor paths to the same upper-right to lower-left trend.
- `scripts/create_v11.py`: uses V10; adds a small point-star with no streak.
- `scripts/historical/create_v8_early_attempt.py`: preserved early attempt; its broader mask and extra shimmer/glint code are not used by `build_all.py`.

No independent cat-tail, lantern, moon, or background animation source code was found. Those elements are baked into the input video and pass through later versions.

## Rebuild properties

The intended output is 1280×720, 30 FPS, 8 seconds, H.264 in yuv420p, looping in Lively. V7/V8 appear at 15 FPS; V9 resamples meteor overlays at 30 FPS while preserving source background frames by pairing frames, and later versions retain 30 FPS. The video output is lossy, so rerenders may differ slightly at codec level.

The recommended command uses a private/user-provided V7 path. The orchestrator creates V8–V11 in one new output directory and refuses to overwrite any version filenames already there.

## Rebuild verification evidence

The full pipeline was run on the available V7 MP4 and generated all four versions. Each output SHA-256 matched the corresponding archived local file:

| Version | SHA-256 |
|---|---|
| V8 | `A54571C3AD15ABBB0551B9362B22F896F16DDB109F6E929A180F327FF36587D8` |
| V9 | `6FD90B746A88C2A4F4E5DEB35301827890DCE05B250AC581060B0ADE28F42507` |
| V10 | `C97AC292887422E5EB2D9A071C6159E8CDD514C12E3AD916C839A1A764565E56` |
| V11 | `8DB080BF5D5FB0E97B586AECC01A603692A84B7EC290D4877A4E3F455F2FDCF0` |

The V11 test suite also passed 3 checks for monotone down-left travel, loop-boundary absence, and a compact point-sized edit region.
