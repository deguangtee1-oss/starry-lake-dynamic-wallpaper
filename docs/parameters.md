# 动画参数 | Animation Parameters

## 中文

### 湖水（V8 精细版候选）

create_v8_refined.py 使用保守的多边形遮罩，并通过向内收缩和柔化边缘保证编辑区域落在湖面内部。反光亮度由三个正弦空间项组成，振幅为 1.6%（factor = 1 + 0.016 * field * alpha）。它不位移湖岸。如果输入 V7 的裁切或对齐发生变化，必须重新检查遮罩；该多边形仅适用于当前 1280×720 构图。

### 流星（V9/V10）

在 create_v9.py 中编辑 events 记录：start、duration、tail、decay 和四个 Bézier 控制点。绘制函数将尾迹放在切线方向的反侧。create_v10.py 的 events 中，两个轨迹的 x 坐标递减、y 坐标递增。只有在清理已知的 V9 输入时，才将 old_events 与旧流星轨迹对应起来。

### 点星（V11）

在 create_v11.py 中调整 P0、P1、START、END、淡入淡出时间、COLOR 以及核心/光晕强度。当前轨迹在片段期间从 (730,35) 移动到 (700,65)，并在进入与离开时淡入淡出。tests/test_v11_star.py 检查向左下单调移动、循环接缝处缺席，以及叠加修改范围保持局部。

现有源文件无法单独调节猫尾巴或灯笼动画；这些像素已经合并在源 MP4 中。

## English

### Water (V8 refined candidate)

create_v8_refined.py uses a conservative polygon mask, an inward min-filter, and a soft edge to keep edits inside the lake. Reflection brightness uses three sinusoidal spatial terms with a 1.6% amplitude (factor = 1 + 0.016 * field * alpha). It does not displace the shoreline. If the input V7 crop or alignment changes, recheck the mask; this polygon is specific to the current 1280×720 composition.

### Meteors (V9/V10)

Edit the events records in create_v9.py: start, duration, tail, decay, and the four Bézier control points. The render function places the tail opposite the travel tangent. In create_v10.py, both event paths have decreasing x coordinates and increasing y coordinates. Keep old_events aligned with old tracks only when cleaning a known V9 input.

### Point star (V11)

In create_v11.py, adjust P0, P1, START, END, fade times, COLOR, and core/halo strengths. The current path moves from (730,35) to (700,65) during the clip, with entry and exit fades. tests/test_v11_star.py checks monotone down-left travel, absence at the loop seam, and a compact local overlay.

The available source files cannot independently tune the cat-tail or lantern animation; those pixels are already composited into the source MP4.
