# 星夜湖畔动态壁纸 | Starry Lake Dynamic Wallpaper

## 项目简介

这是一个基于现有 V7 合成视频继续制作和记录的动态壁纸项目。仓库包含可用的 Python 视频处理脚本、版本记录、参数说明及重新生成指南。项目媒体（V7 源视频、V8–V11 视频、参考静态图和关键帧预览）作为 [GitHub Release 附件](https://github.com/deguangtee1-oss/starry-lake-dynamic-wallpaper/releases/tag/wallpaper-media-v7-v11)提供下载，避免把大型二进制文件放入常规 Git 历史。

最新版本是 V11：1280×720、30 FPS、8 秒、H.264，适合在 Lively Wallpaper 中循环播放。V11 在月亮右侧增加了一颗小型、无尾迹、缓慢向左下漂移的点状星星。

## 功能与可重建范围

- V8：在内缩湖面遮罩内添加低幅度、局部反光亮度变化，不平移岸线。
- V9：处理检测到的旧流星痕迹，并绘制两条独立流星；输出为 30 FPS。
- V10：统一两条流星从右上向左下的总体运动方向。
- V11：在月亮右侧增加一颗缓慢向左下移动的点星。
- 推荐的 scripts/build_all.py 已使用 V7 源视频完整重建 V8–V11；输出 SHA-256 与归档文件一致。

V7 是已经合成的 MP4，不是分层工程。猫咪、尾巴、灯笼、月亮、星星、湖水和景物都已合并在视频中；没有找到可独立控制猫尾巴或灯笼的原始代码。具体流程见 docs/pipeline.md。

## 安装依赖

已用 Python 3.12 验证。以下命令从仓库根目录运行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

requirements.txt 是机器可读的依赖清单，需保持原格式。imageio-ffmpeg 会提供脚本所需的 FFmpeg；无需另行安装独立 FFmpeg。

## 重新生成 V8–V11

使用你有权处理的 V7 MP4。请指定一个新的输出目录；脚本遇到已有的同名版本文件时会停止，不会覆盖：

```powershell
python scripts/build_all.py --v7-input "D:\Media\my_v7.mp4" --output-dir "D:\Media\starry-lake-build"
```

单独重新生成一个版本时，直接调用对应脚本并传入输入与输出路径。例如：

```powershell
python scripts/create_v11.py --input "D:\Media\Starry_Lake_Wallpaper_V10.mp4" --output "D:\Media\Starry_Lake_Wallpaper_V11.mp4"
```

流星、湖水和点星参数位置见 docs/parameters.md。requirements.txt 记录 Python 依赖；.gitignore 等配置文件保留程序所需格式。

## 下载并设置 Lively Wallpaper

1. 从[壁纸媒体 Release](https://github.com/deguangtee1-oss/starry-lake-dynamic-wallpaper/releases/tag/wallpaper-media-v7-v11)下载 Starry_Lake_Wallpaper_V11.mp4。
2. 在 Lively Wallpaper 中选择 **Add wallpaper**，导入 MP4。
3. 选择导入的壁纸并应用到目标显示器；在 Lively 设置中检查缩放和显示器选项。

## 许可证与素材说明

仓库中的 MIT 许可证仅适用于 Python 脚本和文档。LICENSE 保留 MIT 的标准英文法律文本；中文说明见 docs/license.md。Release 中公开的图片和视频不受 MIT 许可覆盖，也没有在此另行授予改编、转发或商业使用许可。项目所有者已授权公开查看和下载。若 V7 输入包含第三方素材，仍须遵守该素材的权利与许可。详情见 docs/asset-rights.md。

## 常见问题

**没有原始 Python 生成脚本怎么办？**

没有找到生成 V7 的原始分层工程；仓库中的脚本从 V7 MP4 开始处理。


**能单独修改猫尾巴或灯笼吗？**

目前不能。它们已合成在 V7 MP4 中，没有独立图层或源代码。


**如何只调整流星或湖水？**

参数位置和限制见 docs/parameters.md；输出时请使用新路径，脚本不会覆盖已有文件。


**为什么视频和图片不在 MIT 许可证下？**

MIT 只适用于仓库脚本和文档。媒体公开下载的范围及许可说明见 docs/asset-rights.md。


## English

### Overview

This project continues and documents a dynamic wallpaper based on the composited V7 source video. The repository contains the available Python video-processing scripts, version history, parameter notes, and rebuild instructions. Project media (the V7 source, V8–V11 videos, reference still, and keyframe previews) are downloadable from the [GitHub Release](https://github.com/deguangtee1-oss/starry-lake-dynamic-wallpaper/releases/tag/wallpaper-media-v7-v11), keeping large binary files out of normal Git history.

The latest version is V11: 1280×720, 30 FPS, 8 seconds, H.264, intended to loop in Lively Wallpaper. V11 adds a small, tail-free point star to the right of the moon that drifts slowly down-left.

### Features and reproducibility

- V8 adds low-amplitude, local reflection-brightness variation inside an inset lake mask without shifting the shoreline.
- V9 repairs detected old meteor traces and draws two separate meteors; output is 30 FPS.
- V10 gives both meteors the same overall upper-right-to-lower-left travel direction.
- V11 adds a slowly drifting point star to the right of the moon.
- The recommended scripts/build_all.py pipeline was run on the V7 source; regenerated V8–V11 SHA-256 hashes matched the archived files.

V7 is a composited MP4, not a layered project. The cat, tail, lantern, moon, stars, lake, and scenery are already merged into the video. No original code was found to control the cat tail or lantern independently. See docs/pipeline.md for details.

### Install dependencies

Python 3.12 was used for verification. Run these commands from the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

requirements.txt is a machine-readable dependency list and must retain its format. imageio-ffmpeg provides FFmpeg for the scripts; no separate FFmpeg installation is needed.

### Rebuild V8–V11

Use a V7 MP4 that you are authorized to process. Choose a new output directory. The script stops if a same-named version already exists and does not overwrite it:

```powershell
python scripts/build_all.py --v7-input "D:\Media\my_v7.mp4" --output-dir "D:\Media\starry-lake-build"
```

To rebuild just one version, call its script with input and output paths. For example:

```powershell
python scripts/create_v11.py --input "D:\Media\Starry_Lake_Wallpaper_V10.mp4" --output "D:\Media\Starry_Lake_Wallpaper_V11.mp4"
```

See docs/parameters.md for meteor, water, and point-star parameters. requirements.txt records Python dependencies; configuration files such as .gitignore retain the formats required by tools.

### Download and set up Lively Wallpaper

1. Download Starry_Lake_Wallpaper_V11.mp4 from the [wallpaper media Release](https://github.com/deguangtee1-oss/starry-lake-dynamic-wallpaper/releases/tag/wallpaper-media-v7-v11).
2. In Lively Wallpaper, select **Add wallpaper** and import the MP4.
3. Select the imported wallpaper and apply it to the desired display. Check scaling and monitor options in Lively's settings.

### License and media

The MIT license in this repository applies only to the Python scripts and documentation. Images and videos published in the Release are not covered by MIT, and no separate rights to modify, repost, or use them commercially are granted here. The project owner has authorized public viewing and downloading. If the V7 input contains third-party material, its rights and license still apply. See docs/asset-rights.md.

### Frequently asked questions

**What if I do not have the original Python generation script?**

The original layered V7 project was not found. The repository scripts process the V7 MP4.


**Can I edit the cat tail or lantern independently?**

Not with the available files. They are composited into V7, and no separate layers or source code were found.


**How do I adjust only the meteors or water?**

See docs/parameters.md for parameter locations and limitations. Use a new output path; scripts do not overwrite existing files.


**Why are the videos and images not under the MIT license?**

MIT applies only to repository scripts and documentation. See docs/asset-rights.md for the media publication scope and terms.
