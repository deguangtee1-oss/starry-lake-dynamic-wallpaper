from __future__ import annotations

import argparse

import math
import os

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE = os.path.join(ROOT, "outputs", "Starry_Lake_Wallpaper_V8.mp4")
OUTPUT = os.path.join(ROOT, "outputs", "Starry_Lake_Wallpaper_V9.mp4")
WIDTH, HEIGHT = 1280, 720
SOURCE_FPS = 15.0
OUTPUT_FPS = 30.0
SKY_HEIGHT = 330


def read_sky_median() -> np.ndarray:
    reader = imageio_ffmpeg.read_frames(SOURCE, pix_fmt="rgb24", bpp=3)
    metadata = next(reader)
    if metadata["size"] != (WIDTH, HEIGHT):
        raise ValueError(f"Unexpected V8 dimensions: {metadata['size']}")
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


def components8(mask: np.ndarray):
    ys, xs = np.where(mask)
    points = set(zip(ys.tolist(), xs.tolist()))
    while points:
        seed = points.pop()
        todo = [seed]
        component = [seed]
        while todo:
            y, x = todo.pop()
            for yy in range(max(0, y - 1), min(SKY_HEIGHT, y + 2)):
                for xx in range(max(0, x - 1), min(WIDTH, x + 2)):
                    point = (yy, xx)
                    if point in points:
                        points.remove(point)
                        todo.append(point)
                        component.append(point)
        yield component


def repair_old_meteor(frame: np.ndarray, median_sky: np.ndarray, frame_index: int) -> int:
    """Replace only detected transient streak pixels with the temporal sky median."""
    current = frame[:SKY_HEIGHT].astype(np.int16)
    diff = np.abs(current - median_sky.astype(np.int16)).max(axis=2)
    luminance = current[:, :, 0] * 0.2126 + current[:, :, 1] * 0.7152 + current[:, :, 2] * 0.0722
    candidates = (diff > 8) & (luminance > 70)
    selected = []
    for component in components8(candidates):
        if len(component) < 15:
            continue
        pts = np.asarray(component, dtype=np.float32)
        centered = pts - pts.mean(axis=0, keepdims=True)
        eig = np.linalg.eigvalsh((centered.T @ centered) / max(1, len(component) - 1))
        major = float(eig[-1])
        ratio = major / max(0.01, float(eig[0]))
        if major >= 25.0 and ratio >= 5.0:
            selected.append(component)
    if not selected:
        return 0

    mask = Image.new("L", (WIDTH, SKY_HEIGHT), 0)
    pixels = mask.load()
    for component in selected:
        for y, x in component:
            pixels[x, y] = 255
    # Include the narrow codec halo; the repair stays on the measured line.
    alpha = np.asarray(mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.55)), dtype=np.float32) / 255.0
    patch = frame[:SKY_HEIGHT].astype(np.float32)
    base = median_sky.astype(np.float32)
    frame[:SKY_HEIGHT] = np.clip(patch * (1 - alpha[..., None]) + base * alpha[..., None], 0, 255).astype(np.uint8)
    return len(selected)


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
    parser = argparse.ArgumentParser(description='Rebuild V9 meteors from V8')
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
        raise FileExistsError(f"Refusing to overwrite an existing V9: {OUTPUT}")

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
            repaired_frames += bool(repair_old_meteor(base, median_sky, source_index))
            for half in (0, 1):
                output_frame = base.copy()
                t = (source_index + 0.5 * half) / SOURCE_FPS
                for event in events:
                    draw_meteor(output_frame, t, event)
                writer.send(output_frame.tobytes())
            source_index += 1
    finally:
        writer.close()
        reader.close()
    print(f"Wrote {OUTPUT}; {source_index * 2} frames at {OUTPUT_FPS:g} fps; repaired old streaks in {repaired_frames} source frames")


if __name__ == "__main__":
    main()

