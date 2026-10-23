# 脚本说明 | Scripts

## 中文

- build_all.py：从用户指定的 V7 MP4 依序生成 V8、V9、V10、V11；输出目录内遇到同名文件时会停止，不覆盖旧视频。
- create_v8_refined.py：在湖面内侧遮罩中添加低幅度反光变化。
- create_v9.py：检测并修补指定旧流星痕迹，然后绘制两条流星，输出 30 FPS。
- create_v10.py：从 V9 输入重新绘制两条统一向左下移动的流星。
- create_v11.py：从 V10 输入添加一颗缓慢移动的点星；默认同时生成关键帧预览。
- make_keyframes.py：按指定时间从 MP4 提取画面并生成联系表。
- historical/create_v8_early_attempt.py：保留的早期实验脚本，不属于推荐重建流程。

Python 依赖列在仓库根目录的 requirements.txt。命令行帮助同时提供中文和英文。参数及动画限制见 docs/parameters.md。

## English

- build_all.py rebuilds V8, V9, V10, and V11 sequentially from a user-supplied V7 MP4. It stops rather than overwriting same-named outputs.
- create_v8_refined.py adds low-amplitude reflection changes inside an inset water mask.
- create_v9.py detects and repairs specified old meteor traces, then draws two meteors at 30 FPS.
- create_v10.py redraws two meteors from V9 with a shared down-left direction.
- create_v11.py adds one slowly moving point star to a V10 input and creates a keyframe preview by default.
- make_keyframes.py extracts frames at specified times and creates a contact sheet.
- historical/create_v8_early_attempt.py is a preserved early experiment and is not part of the recommended rebuild.

Python dependencies are listed in the root requirements.txt. Command-line help is bilingual. See docs/parameters.md for parameters and animation limitations.
