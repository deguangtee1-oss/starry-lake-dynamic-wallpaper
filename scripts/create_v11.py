from __future__ import annotations

import argparse
import os
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SOURCE = ''
OUTPUT = ''
PREVIEW = ''
WIDTH, HEIGHT = 1280, 720

# One tiny star in a dark, open patch above-right of the moon.
# It drifts monotonically left/down. It is fully absent at the loop seam.
START = 0.35
END = 7.65
P0 = np.array([730.0, 35.0], dtype=np.float32)
P1 = np.array([700.0, 65.0], dtype=np.float32)
COLOR = np.array([194.0, 215.0, 255.0], dtype=np.float32)

def star_position(t: float):
    """Return the linear down-left point-star position during its active interval."""
    if t <= START or t >= END:
        return None
    u = (t - START) / (END - START)
    return (
        float(P0[0] + u * (P1[0] - P0[0])),
        float(P0[1] + u * (P1[1] - P0[1])),
    )

def overlay_point_star(frame: np.ndarray, t: float) -> None:
    position = star_position(t)
    if position is None:
        return
    x, y = position
    u = (t - START) / (END - START)
    # Smooth step only for entry/exit envelope; motion itself stays monotone.
    fade_in = np.clip((t - START) / 0.48, 0.0, 1.0)
    fade_out = np.clip((END - t) / 0.48, 0.0, 1.0)
    fade_in = fade_in * fade_in * (3.0 - 2.0 * fade_in)
    fade_out = fade_out * fade_out * (3.0 - 2.0 * fade_out)
    envelope = min(fade_in, fade_out)
    # A tiny, independent, barely perceptible slow luminance variation.
    twinkle = 0.97 + 0.03 * np.sin(2.0 * np.pi * (t / 5.6) + 0.8)
    amp = envelope * twinkle
    # Compact subpixel point with an extremely restrained local halo; no head, trail, or streak.
    radius = 4
    x0, x1 = max(0, int(x) - radius), min(WIDTH, int(x) + radius + 2)
    y0, y1 = max(0, int(y) - radius), min(HEIGHT, int(y) + radius + 2)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    r2 = (xx - x) ** 2 + (yy - y) ** 2
    core = np.exp(-0.5 * r2 / (0.85 ** 2))
    halo = np.exp(-0.5 * r2 / (2.0 ** 2))
    alpha = np.clip(0.44 * core + 0.04 * halo, 0.0, 0.48) * amp
    patch = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = np.clip(patch * (1.0 - alpha[..., None]) + COLOR * alpha[..., None], 0, 255).astype(np.uint8)

def main() -> None:
    global SOURCE, OUTPUT, PREVIEW
    parser = argparse.ArgumentParser(description="Add the V11 slow drifting point star to a source video.")
    parser.add_argument("--input", required=True, help="V10 MP4 input")
    parser.add_argument("--output", required=True, help="New V11 MP4 output (must not already exist)")
    parser.add_argument("--preview", help="Optional keyframe contact sheet path")
    args = parser.parse_args()
    SOURCE = os.path.abspath(args.input)
    OUTPUT = os.path.abspath(args.output)
    PREVIEW = os.path.abspath(args.preview) if args.preview else os.path.splitext(OUTPUT)[0] + "_keyframes.png"
    if os.path.exists(OUTPUT):
        raise FileExistsError(f"Refusing to overwrite existing output: {OUTPUT}")
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    os.makedirs(os.path.dirname(PREVIEW), exist_ok=True)
    if not os.path.isfile(SOURCE):
        raise FileNotFoundError(SOURCE)
    if os.path.exists(OUTPUT):
        raise FileExistsError(f'Refusing to overwrite existing V11: {OUTPUT}')
    reader = imageio_ffmpeg.read_frames(SOURCE, pix_fmt='rgb24', bpp=3)
    meta = next(reader)
    width, height = meta['size']
    fps = float(meta['fps'])
    duration = float(meta['duration'])
    if (width, height) != (WIDTH, HEIGHT):
        raise ValueError(f'Unexpected V10 size: {width}x{height}')
    writer = imageio_ffmpeg.write_frames(
        OUTPUT, (width, height), fps=fps, codec='libx264', pix_fmt_in='rgb24',
        pix_fmt_out='yuv420p', quality=9, macro_block_size=1,
        ffmpeg_log_level='error', output_params=['-movflags', '+faststart']
    )
    writer.send(None)
    keyframes = {}
    frame_index = 0
    try:
        for raw in reader:
            if not raw:
                break
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(height, width, 3).copy()
            t = frame_index / fps
            overlay_point_star(frame, t)
            if frame_index in {15, 45, 90, 120, 150, 180, 210, 225}:
                keyframes[frame_index] = frame.copy()
            writer.send(frame.tobytes())
            frame_index += 1
    finally:
        writer.close()
        reader.close()
    expected = round(duration * fps)
    if frame_index != expected:
        raise RuntimeError(f'Frame count mismatch: {frame_index}, expected {expected}')
    # Compact time strip around the moon to verify actual displacement and adjacent frames.
    times = sorted(keyframes)
    tile_w, tile_h = 720, 300
    sheet = Image.new('RGB', (tile_w * 4, (tile_h + 28) * 2), (4, 8, 22))
    draw = ImageDraw.Draw(sheet)
    for i, idx in enumerate(times):
        t = idx / fps
        crop = Image.fromarray(keyframes[idx]).crop((620, 0, 980, 150)).resize((tile_w, tile_h))
        x, y = (i % 4) * tile_w, (i // 4) * (tile_h + 28)
        sheet.paste(crop, (x, y + 24))
        draw.text((x + 10, y + 4), f't={t:.2f}s | star center=({P0[0] + ((t-START)/(END-START))*(P1[0]-P0[0]):.1f}, {P0[1] + ((t-START)/(END-START))*(P1[1]-P0[1]):.1f})', fill='white')
    sheet.save(PREVIEW)
    print(f'Wrote {OUTPUT}; {frame_index} frames; {fps:g} fps; {duration:g}s')
    print(f'Wrote {PREVIEW}')

if __name__ == '__main__':
    main()

