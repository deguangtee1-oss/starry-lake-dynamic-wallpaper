from __future__ import annotations

import argparse

import math
import os

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE = os.path.join(ROOT, "outputs", "Starry_Lake_Wallpaper_V9.mp4")
OUTPUT = os.path.join(ROOT, "outputs", "Starry_Lake_Wallpaper_V10.mp4")
WIDTH, HEIGHT = 1280, 720
SOURCE_FPS = 30.0
OUTPUT_FPS = 30.0
SKY_HEIGHT = 330


def read_sky_median() -> np.ndarray:
    reader = imageio_ffmpeg.read_frames(SOURCE, pix_fmt="rgb24", bpp=3)
    metadata = next(reader)
    if metadata["size"] != (WIDTH, HEIGHT):
        raise ValueError(f"Unexpected V9 dimensions: {metadata['size']}")
    frames = []
    try:
        for raw in reader:
            if not raw:
                break
            frames.append(np.frombuffer(raw, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3)[:SKY_HEIGHT].copy())
    finally:
        reader.close()
    if len(frames) != round(metadata["duration"] * metadata["fps"]):
        raise ValueError(f"Unexpected frame count: {len(frames)}")
    return np.median(np.stack(frames, axis=0), axis=0).astype(np.uint8)


def erase_meteor(frame: np.ndarray, median_sky: np.ndarray, t: float, event) -> bool:
    """Erase a known V9 meteor footprint using a narrow, soft trajectory mask."""
    p = (t - event["start"]) / event["duration"]
    if p <= 0.0 or p >= 1.0:
        return False
    pos, tangent = bezier(event, p)
    hx, hy = float(pos[0]), float(pos[1])
    ux, uy = float(tangent[0]), float(tangent[1])
    px, py = -uy, ux
    tail_length = event["tail"] * min(1.0, p / 0.22)
    tail_x, tail_y = hx - ux * tail_length, hy - uy * tail_length
    pad = 10
    x0 = max(0, int(min(hx, tail_x) - pad))
    x1 = min(WIDTH, int(max(hx, tail_x) + pad) + 1)
    y0 = max(0, int(min(hy, tail_y) - pad))
    y1 = min(SKY_HEIGHT, int(max(hy, tail_y) + pad) + 1)
    if x1 <= x0 or y1 <= y0:
        return False
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    along = (xx - hx) * ux + (yy - hy) * uy
    across = (xx - hx) * px + (yy - hy) * py
    active = (along <= 2.5) & (along >= -tail_length - 3.0)
    rise = np.clip(p / 0.10, 0.0, 1.0)
    fall = np.clip((1.0 - p) / 0.19, 0.0, 1.0)
    envelope = (rise * rise * (3 - 2 * rise)) * (fall * fall * (3 - 2 * fall))
    tail_profile = np.exp(along / event["decay"])
    core = np.exp(-0.5 * (across / 1.25) ** 2)
    glow = 0.24 * np.exp(-0.5 * (across / 2.75) ** 2)
    mask = np.clip((core + glow) * tail_profile * envelope, 0.0, 1.0) * active
    if float(mask.max()) < 0.01:
        return False
    patch = frame[y0:y1, x0:x1].astype(np.float32)
    clean = median_sky[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = np.clip(patch * (1 - mask[..., None]) + clean * mask[..., None], 0, 255).astype(np.uint8)
    return True


def bezier(event, progress: float):
    p0, p1, p2, p3 = event["points"]
    u = 1.0 - progress
    pos = (u**3) * p0 + 3 * (u**2) * progress * p1 + 3 * u * (progress**2) * p2 + (progress**3) * p3
    tangent = 3 * (u**2) * (p1 - p0) + 6 * u * progress * (p2 - p1) + 3 * (progress**2) * (p3 - p2)
    tangent /= max(1e-6, float(np.linalg.norm(tangent)))
    return pos, tangent


def draw_meteor(frame: np.ndarray, t: float, event) -> None:
    start, duration = event["start"], event["duration"]
    p = (t - start) / duration
    if p <= 0.0 or p >= 1.0:
        return
    pos, tangent = bezier(event, p)
    hx, hy = float(pos[0]), float(pos[1])
    ux, uy = float(tangent[0]), float(tangent[1])
    px, py = -uy, ux
    tail_length = event["tail"] * min(1.0, p / 0.22)
    pad = 8
    tail_x, tail_y = hx - ux * tail_length, hy - uy * tail_length
    x0 = max(0, int(min(hx, tail_x) - pad))
    x1 = min(WIDTH, int(max(hx, tail_x) + pad) + 1)
    y0 = max(0, int(min(hy, tail_y) - pad))
    y1 = min(SKY_HEIGHT, int(max(hy, tail_y) + pad) + 1)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    along = (xx - hx) * ux + (yy - hy) * uy  # negative values trail behind the head
    across = (xx - hx) * px + (yy - hy) * py
    active = (along <= 0.0) & (along >= -tail_length)

    # A narrow luminous line with a slowly fading tail; there is no radial head.
    rise = np.clip(p / 0.10, 0.0, 1.0)
    fall = np.clip((1.0 - p) / 0.19, 0.0, 1.0)
    envelope = (rise * rise * (3 - 2 * rise)) * (fall * fall * (3 - 2 * fall))
    tail_profile = np.exp(along / event["decay"])
    core = np.exp(-0.5 * (across / 0.67) ** 2)
    glow = np.exp(-0.5 * (across / 1.8) ** 2)
    line_alpha = (0.56 * core * tail_profile + 0.065 * glow * tail_profile) * envelope * active
    # The last few pixels blend brighter into the same line rather than forming a ball.
    line_alpha *= 0.78 + 0.22 * np.exp(along / 7.0)

    patch = frame[y0:y1, x0:x1].astype(np.float32)
    tail_color = np.array([177.0, 204.0, 244.0], dtype=np.float32)
    front_color = np.array([235.0, 243.0, 255.0], dtype=np.float32)
    front_mix = np.clip(1.0 + along / 22.0, 0.0, 1.0)
    color = tail_color[None, None, :] * (1 - front_mix[..., None]) + front_color[None, None, :] * front_mix[..., None]
    patch = patch * (1 - line_alpha[..., None]) + color * line_alpha[..., None]
    frame[y0:y1, x0:x1] = np.clip(patch, 0, 255).astype(np.uint8)


def main() -> None:
    global SOURCE, OUTPUT
    parser = argparse.ArgumentParser(description='Rebuild V10 meteor direction from V9')
    parser.add_argument("--input", required=True, help="Input MP4 path")
    parser.add_argument("--output", required=True, help="New MP4 output path (must not already exist)")
    args = parser.parse_args()
    SOURCE = os.path.abspath(args.input)
    OUTPUT = os.path.abspath(args.output)
    if os.path.exists(OUTPUT):
        raise FileExistsError(f"Refusing to overwrite existing output: {OUTPUT}")
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    if not os.path.isfile(SOURCE):
        raise FileNotFoundError(SOURCE)
    if os.path.exists(OUTPUT):
        raise FileExistsError(f"Refusing to overwrite an existing V10: {OUTPUT}")

    median_sky = read_sky_median()
    events = [
        {
            "start": 0.95,
            "duration": 1.55,
            "tail": 76.0,
            "decay": 36.0,
            "points": np.asarray([(615.0, 18.0), (590.0, 75.0), (520.0, 155.0), (475.0, 212.0)], dtype=np.float32),
        },
        {
            "start": 4.30,
            "duration": 1.68,
            "tail": 82.0,
            "decay": 40.0,
            "points": np.asarray([(552.0, 18.0), (522.0, 78.0), (442.0, 155.0), (390.0, 215.0)], dtype=np.float32),
        },
    ]

    old_events = [
        {
            "start": 0.95,
            "duration": 1.55,
            "tail": 76.0,
            "decay": 36.0,
            "points": np.asarray([(615.0, 18.0), (590.0, 75.0), (520.0, 155.0), (475.0, 212.0)], dtype=np.float32),
        },
        {
            "start": 4.30,
            "duration": 1.68,
            "tail": 82.0,
            "decay": 40.0,
            "points": np.asarray([(390.0, 18.0), (420.0, 78.0), (500.0, 155.0), (552.0, 215.0)], dtype=np.float32),
        },
    ]

    reader = imageio_ffmpeg.read_frames(SOURCE, pix_fmt="rgb24", bpp=3)
    meta = next(reader)
    writer = imageio_ffmpeg.write_frames(
        OUTPUT,
        (WIDTH, HEIGHT),
        fps=OUTPUT_FPS,
        codec="libx264",
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        quality=9,
        macro_block_size=1,
        ffmpeg_log_level="error",
        output_params=["-movflags", "+faststart"],
    )
    writer.send(None)
    source_index = 0
    repaired_frames = 0
    try:
        for raw in reader:
            if not raw:
                break
            base = np.frombuffer(raw, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3).copy()
            t = source_index / SOURCE_FPS
            repaired_frames += any(erase_meteor(base, median_sky, t, old_event) for old_event in old_events)
            output_frame = base.copy()
            for event in events:
                draw_meteor(output_frame, t, event)
            writer.send(output_frame.tobytes())
            source_index += 1
    finally:
        writer.close()
        reader.close()
    print(f"Wrote {OUTPUT}; {source_index} frames at {OUTPUT_FPS:g} fps; cleared old V9 meteor tracks in {repaired_frames} source frames")


if __name__ == "__main__":
    main()


