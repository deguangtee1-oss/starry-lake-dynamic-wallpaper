# Starry Lake Dynamic Wallpaper

A small, source-video-based workflow for refining the Starry Lake animated wallpaper. The repository contains the available Python processing scripts and project notes. It does not contain the wallpaper videos or reference image: they are derived from a supplied image/video whose redistribution rights have not been verified.

## Current result

The latest local version is **V11**, 1280×720, 30 FPS, 8 seconds, H.264, intended to loop in Lively Wallpaper. V11 adds one tiny, tail-free point star that drifts slowly down-left in the dark sky to the right of the moon. The source video and archived versions are kept locally in the user's Obsidian vault; they are not committed here.

## What is and is not reproducible

- Existing scripts cover a conservative water-reflection pass (V8 candidate), two meteor paths (V9), unified meteor direction (V10), and a new slow point star (V11).
- V7 is a rendered MP4, not a layered source project. Cats, tail, lantern, moon, stars, lake and scenery are already composited into it. No independent cat-tail or lantern source code was found.
- The exact original layered artwork and its redistribution license are not available. Provide your own authorized V7 MP4 to rebuild locally.
- The recommended `build_all.py` pipeline has been run against the supplied V7 source. The regenerated V8, V9, V10 and V11 MP4s had SHA-256 hashes identical to the archived local versions. The old early V8 attempt is preserved for provenance and is not used by the recommended pipeline.

## Requirements

Python 3.12 was used for verification. Install packages from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`imageio-ffmpeg` supplies FFmpeg; no separate FFmpeg installation is required for these scripts.

## Rebuild V8–V11

Use a V7 MP4 you are authorized to process. Outputs are created in a new directory; the script refuses to overwrite any existing V8–V11 filename.

```powershell
python scripts/build_all.py --v7-input "D:\Media\my_v7.mp4" --output-dir "D:\Media\starry-lake-build"
```

To regenerate only one version, call its script with explicit paths. For example:

```powershell
python scripts/create_v11.py --input "D:\Media\Starry_Lake_Wallpaper_V10.mp4" --output "D:\Media\Starry_Lake_Wallpaper_V11.mp4"
```

Each script rejects an existing output path. Use a fresh name or output directory when iterating.

## Lively Wallpaper

1. Download a V11 MP4 from a release if one is published, or build it locally from an authorized source.
2. In Lively Wallpaper, choose **Add wallpaper** and select the MP4.
3. Select the imported wallpaper and apply it to the desired display. Lively supports video looping; check scaling and monitor selection in Lively's controls.

No MP4 release is included while the image/media redistribution rights remain unconfirmed. See [asset rights](docs/asset-rights.md).

## Publication status

The project is prepared locally for `deguangtee1-oss/starry-lake-dynamic-wallpaper`. The target has no publicly visible repository at the time of this check; GitHub CLI is not installed and no GitHub account is available through the configured Git credential helper, so the repository has not yet been created or pushed. An authenticated check is needed to rule out a private repository with the same name.

## License scope

The MIT license in this repository applies to the included scripts and documentation only. No wallpaper image, video, extracted frame, thumbnail, or other visual asset is included or licensed here. See [asset rights](docs/asset-rights.md).
