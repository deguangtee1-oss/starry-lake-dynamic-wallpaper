# 流程与版本沿革 | Pipeline and Version Lineage

## 中文

### 素材清单

Obsidian 项目档案包含 V7、V8、V9、V10 和 V11 MP4。V7 源视频也曾保存在 Downloads。档案中有一张扁平参考图，没有可编辑的分层工程。V7 源视频、V8–V11 成品、参考图及现有关键帧预览现作为 GitHub Release 附件公开下载；没有把媒体放进普通 Git 历史。

### 脚本职责

- scripts/create_v8_refined.py：读取 V7；只在内缩水面遮罩内加入低幅度、随时间周期变化的反光亮度场，不移动像素。
- scripts/create_v9.py：读取 V8；计算天空时间中值以检测和修补旧流星痕迹，再绘制两次流星运动。输出 30 FPS。
- scripts/create_v10.py：读取 V9；使两条新流星都沿右上至左下的总体方向移动。
- scripts/create_v11.py：读取 V10；添加一颗小型无尾迹点星。
- scripts/historical/create_v8_early_attempt.py：保存早期实验版本；宽水面遮罩和附加闪烁逻辑不用于推荐重建。

没有找到独立控制猫尾巴、灯笼、月亮或背景动画的原始代码。这些元素已经合并在输入视频中，后续版本沿用该画面。

### 重建参数

目标输出为 1280×720、30 FPS、8 秒、H.264 yuv420p，可在 Lively 中循环。V7/V8 为 15 FPS；V9 在生成流星时按 30 FPS 采样，背景帧成对沿用；后续版本保持 30 FPS。视频使用有损编码，因此重复编码可能造成轻微差异。

推荐命令会把用户提供的 V7 路径作为输入，并在一个新目录中依序生成 V8–V11。如果输出目录内已有同名文件，脚本会拒绝覆盖。

### 重建验证记录

完整流程曾对提供的 V7 MP4 运行，生成的四个视频 SHA-256 与本地归档一致：

| 版本 | SHA-256 |
|---|---|
| V8 | A54571C3AD15ABBB0551B9362B22F896F16DDB109F6E929A180F327FF36587D8 |
| V9 | 6FD90B746A88C2A4F4E5DEB35301827890DCE05B250AC581060B0ADE28F42507 |
| V10 | C97AC292887422E5EB2D9A071C6159E8CDD514C12E3AD916C839A1A764565E56 |
| V11 | 8DB080BF5D5FB0E97B586AECC01A603692A84B7EC290D4877A4E3F455F2FDCF0 |

V11 测试脚本通过了 3 项检查：星点沿左下方向单调移动、循环接缝处无星点、修改区域保持局部且点状。

## English

### Asset inventory

The Obsidian project archive contains V7, V8, V9, V10, and V11 MP4s. The V7 source was also present in Downloads. The archive contains a flattened reference still but no editable layered project. The V7 source, V8–V11 outputs, reference still, and available keyframe previews are now public GitHub Release assets; media is not stored in normal Git history.

### Script responsibilities

- scripts/create_v8_refined.py reads V7 and adds a low-amplitude, time-periodic reflection-brightness field only inside an inset water mask. It does not shift pixels.
- scripts/create_v9.py reads V8, computes a temporal sky median to detect and repair old meteor traces, then draws two meteor events. Output is 30 FPS.
- scripts/create_v10.py reads V9 and makes both new meteors travel in the same overall upper-right-to-lower-left direction.
- scripts/create_v11.py reads V10 and adds a small point star without a tail.
- scripts/historical/create_v8_early_attempt.py preserves an early experiment. Its broad water mask and extra shimmer logic are not used by the recommended rebuild.

No original code was found to animate the cat tail, lantern, moon, or background independently. These elements are baked into the input video and carried through later versions.

### Rebuild properties

The target output is 1280×720, 30 FPS, 8 seconds, H.264 yuv420p, and suitable for looping in Lively. V7/V8 use 15 FPS. V9 samples meteor rendering at 30 FPS while reusing each background frame pair; later versions remain at 30 FPS. The video uses lossy encoding, so repeated encoding may introduce small differences.

The recommended command accepts a user-provided V7 path and generates V8–V11 sequentially in a new directory. Scripts refuse to overwrite same-named files already present in that output directory.

### Rebuild verification

The full pipeline was run on the supplied V7 MP4. The SHA-256 hashes of the four generated videos matched the local archive:

| Version | SHA-256 |
|---|---|
| V8 | A54571C3AD15ABBB0551B9362B22F896F16DDB109F6E929A180F327FF36587D8 |
| V9 | 6FD90B746A88C2A4F4E5DEB35301827890DCE05B250AC581060B0ADE28F42507 |
| V10 | C97AC292887422E5EB2D9A071C6159E8CDD514C12E3AD916C839A1A764565E56 |
| V11 | 8DB080BF5D5FB0E97B586AECC01A603692A84B7EC290D4877A4E3F455F2FDCF0 |

The V11 test script passed three checks: monotone down-left travel, absence at the loop seam, and a compact point-sized edit region.
