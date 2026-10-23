from __future__ import annotations

import argparse

import math
import os

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


SOURCE = ""
OUTPUT = ""
WIDTH, HEIGHT = 1280, 720


def build_safe_lake_core() -> tuple[tuple[int, int, int, int], np.ndarray]:
    """构造完全位于湖面内部并避开岸线的保守遮罩。 / Make a conservative mask wholly inside the lake, inset from the shore."""
    hard = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(hard).polygon(
        [
            (585, 497), (690, 489), (850, 488), (1015, 489), (1164, 491),
            (1185, 510), (1182, 565), (1142, 601), (1070, 619), (920, 628),
            (780, 623), (670, 599), (610, 562), (590, 530),
        ],
        fill=255,
    )
    # 仅向内羽化，遮罩不会超出已核对的水域核心。 / Feather inward only; the mask never extends past the checked water core.
    inset = hard.filter(ImageFilter.MinFilter(31)).filter(ImageFilter.GaussianBlur(9))
    hard_array = np.asarray(hard, dtype=np.float32) / 255.0
    soft_array = np.asarray(inset, dtype=np.float32) / 255.0
    alpha = np.minimum(hard_array, soft_array)
    bounds = hard.getbbox()
    x0, y0, x1, y1 = bounds
    return bounds, alpha[y0:y1, x0:x1]


def main() -> None:
    global SOURCE, OUTPUT
    parser = argparse.ArgumentParser(description='从 V7 MP4 生成仅作用于水面的 V8 精细版。 / Create the water-only V8 refinement from a V7 MP4.')
    parser.add_argument("--input", required=True, help="输入 MP4 路径 / Input MP4 path")
    parser.add_argument("--output", required=True, help="新的 MP4 输出路径，文件必须不存在 / New MP4 output path; must not already exist")
    args = parser.parse_args()
    SOURCE = os.path.abspath(args.input)
    OUTPUT = os.path.abspath(args.output)
    if os.path.exists(OUTPUT):
        raise FileExistsError(f"为保护现有文件，不会覆盖输出 / Refusing to overwrite existing output: {OUTPUT}")
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    if not os.path.isfile(SOURCE):
        raise FileNotFoundError(f"找不到输入视频 / Input video not found: {SOURCE}")

    reader = imageio_ffmpeg.read_frames(SOURCE, pix_fmt="rgb24", bpp=3)
    metadata = next(reader)
    if metadata["size"] != (WIDTH, HEIGHT):
        raise ValueError(f"输入尺寸不符合预期 / Unexpected input dimensions: {metadata['size']}")
    fps = metadata["fps"]
    bounds, alpha = build_safe_lake_core()
    x0, y0, x1, y1 = bounds
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)

    writer = imageio_ffmpeg.write_frames(
        OUTPUT,
        (WIDTH, HEIGHT),
        fps=fps,
        codec="libx264",
        pix_fmt_in="rgb24",
        pix_fmt_out="yuv420p",
        quality=9,
        macro_block_size=1,
        ffmpeg_log_level="error",
        output_params=["-movflags", "+faststart"],
    )
    writer.send(None)

    frame_index = 0
    period = float(metadata["duration"])
    try:
        for raw in reader:
            if not raw:
                break
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(HEIGHT, WIDTH, 3).copy()
            t = frame_index / fps
            phase = 2.0 * math.pi * t / period

            # 低幅度反光缓慢移动，不平移像素；周期场在视频循环点平滑衔接。
            # Low-amplitude reflection bands move slowly without shifting pixels;
            # the periodic field closes smoothly at the video loop point.
            field = (
                0.52 * np.sin(0.095 * yy + 0.035 * xx + phase)
                + 0.30 * np.sin(0.14 * yy - 0.018 * xx - 2.0 * phase)
                + 0.18 * np.sin(0.07 * xx + 0.025 * yy + 3.0 * phase)
            )
            factor = 1.0 + 0.016 * field * alpha
            patch = frame[y0:y1, x0:x1].astype(np.float32)
            frame[y0:y1, x0:x1] = np.clip(patch * factor[..., None], 0, 255).astype(np.uint8)

            # V7 原有天空、流星时间、猫咪、灯笼和星星保持为底图内容。
            # The existing V7 sky, meteor timing, cat, lantern, and stars remain the source.
            writer.send(frame.tobytes())
            frame_index += 1
    finally:
        writer.close()
        reader.close()

    print(f"已写入 / Wrote {OUTPUT}: {frame_index} 帧 / frames，{fps:g} fps")


if __name__ == "__main__":
    main()
