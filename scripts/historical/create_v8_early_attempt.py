from __future__ import annotations

import argparse

import math
import os
import sys

import imageio_ffmpeg
import numpy as np


SOURCE = ""
OUTPUT = ""
FPS = 15
W, H = 1280, 720


def gaussian_line_overlay(frame: np.ndarray, head: tuple[float, float], direction: tuple[float, float], strength: float) -> None:
    """Paint one short-lived, soft meteor with a tapered, fading tail."""
    hx, hy = head
    dx, dy = direction
    norm = math.hypot(dx, dy)
    ux, uy = dx / norm, dy / norm
    px, py = -uy, ux
    length = 148.0
    pad = 17
    x0 = max(0, int(min(hx, hx - ux * length) - pad))
    x1 = min(W, int(max(hx, hx - ux * length) + pad) + 1)
    y0 = max(0, int(min(hy, hy - uy * length) - pad))
    y1 = min(H, int(max(hy, hy - uy * length) + pad) + 1)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    along = (xx - hx) * ux + (yy - hy) * uy  # negative behind the head
    across = (xx - hx) * px + (yy - hy) * py
    tail = np.clip((-along) / length, 0.0, 1.0)
    cross_glow = np.exp(-0.5 * (across / 3.2) ** 2)
    fade = np.clip((1.0 + along / length) * 1.45, 0.0, 1.0)
    alpha = strength * cross_glow * fade * (0.22 + 0.78 * tail)
    alpha *= (along <= 1.5) & (along >= -length)
    # Broad, very soft blue-white glow behind a bright warm-white head.
    glow = strength * np.exp(-0.5 * (across / 9.0) ** 2) * np.clip((-along) / length, 0, 1) * 0.10
    patch = frame[y0:y1, x0:x1].astype(np.float32)
    trail_color = np.array([190.0, 218.0, 255.0], dtype=np.float32)
    patch = patch * (1 - (alpha + glow)[..., None]) + trail_color * (alpha + glow)[..., None]
    head_r2 = (xx - hx) ** 2 + (yy - hy) ** 2
    core = strength * np.exp(-head_r2 / 13.0)
    head_color = np.array([255.0, 249.0, 225.0], dtype=np.float32)
    patch = patch * (1 - core[..., None]) + head_color * core[..., None]
    frame[y0:y1, x0:x1] = np.clip(patch, 0, 255).astype(np.uint8)


def main() -> None:
    global SOURCE, OUTPUT
    parser = argparse.ArgumentParser(description='Historical first V8 attempt; broad water mask; not used by the recommended rebuild')
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
    reader = imageio_ffmpeg.read_frames(SOURCE, pix_fmt="rgb24", bpp=3)
    meta = next(reader)
    width, height = meta["size"]
    if (width, height) != (W, H):
        raise ValueError(f"Expected 1280x720, got {width}x{height}")
    fps = meta["fps"] or FPS
    writer = imageio_ffmpeg.write_frames(
        OUTPUT,
        (W, H),
        fps=fps,
        codec="libx264",
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        quality=8,
        macro_block_size=1,
        ffmpeg_log_level="error",
        output_params=["-movflags", "+faststart"],
    )
    writer.send(None)

    # A gentle, feathered lake mask. It excludes the prominent foreground rocks.
    from PIL import Image, ImageDraw, ImageFilter

    water = Image.new("L", (W, H), 0)
    ImageDraw.Draw(water).polygon(
        [(375, 498), (455, 477), (650, 472), (850, 474), (1040, 474), (1279, 464),
         (1279, 719), (680, 719), (585, 690), (520, 652), (465, 618), (415, 580), (382, 545)],
        fill=255,
    )
    water_mask = np.asarray(water.filter(ImageFilter.GaussianBlur(9)), dtype=np.float32) / 255.0
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)

    # Stable, natural-looking meteor events: short appearances, no lingering trails.
    events = [
        # start time, duration, start point, end point (head path)
        (0.72, 0.62, (1010.0, 72.0), (842.0, 205.0)),
        (3.36, 0.58, (526.0, 52.0), (378.0, 183.0)),
        (6.15, 0.64, (1215.0, 176.0), (1037.0, 298.0)),
    ]

    frame_no = 0
    try:
        for raw in reader:
            if not raw:
                break
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(H, W, 3).copy()
            t = frame_no / fps

            # Subtle, spatially varying horizontal/vertical displacement in the lake.
            dx = 1.35 * np.sin(Y * 0.085 - t * 2.6) + 0.55 * np.sin(X * 0.025 + t * 1.7)
            dy = 0.75 * np.sin(X * 0.019 - t * 1.9 + Y * 0.011)
            sx = np.clip(np.rint(X + dx), 0, W - 1).astype(np.int32)
            sy = np.clip(np.rint(Y + dy), 0, H - 1).astype(np.int32)
            warped = frame[sy, sx].astype(np.float32)
            # Faint travelling bands make existing reflections shimmer without moving the whole lake.
            shimmer = 1.0 + 0.025 * np.sin(Y * 0.13 + X * 0.012 + t * 2.3)
            shimmer += 0.012 * np.sin(X * 0.036 - t * 2.0)
            blend = water_mask[..., None]
            frame = np.clip(frame.astype(np.float32) * (1 - blend) + warped * shimmer[..., None] * blend, 0, 255).astype(np.uint8)

            # Quiet lantern glow and a few star glints, each with a restrained independent pulse.
            lantern = 1.0 + 0.025 * math.sin(t * 2 * math.pi * 0.72 + 0.4)
            lx, ly = 78, 354
            glow = np.exp(-(((X - lx) / 67.0) ** 2 + ((Y - ly) / 83.0) ** 2) * 1.15)
            frame = np.clip(frame.astype(np.float32) * (1 + (lantern - 1) * glow[..., None]), 0, 255).astype(np.uint8)
            for j, (sx0, sy0, phase) in enumerate(((225, 62, 0.2), (412, 125, 2.1), (590, 45, 3.6), (1112, 96, 1.1), (945, 32, 4.4), (708, 61, 2.8))):
                pulse = 0.09 * (0.5 + 0.5 * math.sin(t * (2.0 + 0.12 * j) + phase))
                star = np.exp(-(((X - sx0) / 8.0) ** 2 + ((Y - sy0) / 8.0) ** 2) * 2.0)
                frame = np.clip(frame.astype(np.float32) * (1 + pulse * star[..., None]), 0, 255).astype(np.uint8)

            for start, duration, p0, p1 in events:
                progress = (t - start) / duration
                if 0.0 <= progress <= 1.0:
                    # Ease only the head motion slightly; brightness fades in and out.
                    q = progress * progress * (3.0 - 2.0 * progress)
                    x = p0[0] + (p1[0] - p0[0]) * q
                    y = p0[1] + (p1[1] - p0[1]) * q
                    fade = min(progress / 0.14, (1.0 - progress) / 0.20, 1.0)
                    strength = max(0.0, fade) * 0.82
                    direction = (p1[0] - p0[0], p1[1] - p0[1])
                    gaussian_line_overlay(frame, (x, y), direction, strength)

            writer.send(frame.tobytes())
            frame_no += 1
    finally:
        writer.close()
        reader.close()
    print(f"Wrote {OUTPUT} ({frame_no} frames at {fps:g} fps)")


if __name__ == "__main__":
    main()
