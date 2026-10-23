from __future__ import annotations
import argparse
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw

def main():
    p=argparse.ArgumentParser(description="从 MP4 提取带时间标签的帧并制作联系表 / Render labeled frames from an MP4 into a contact sheet")
    p.add_argument("--input",required=True,help="输入 MP4 路径 / Input MP4 path")
    p.add_argument("--output",required=True,help="联系表输出路径 / Contact sheet output path")
    p.add_argument("--times",default="0,1,2,3,4,5,6,7",help="以逗号分隔的秒数 / Comma-separated times in seconds")
    a=p.parse_args(); src=Path(a.input); dst=Path(a.output)
    if not src.is_file(): raise FileNotFoundError(f"找不到输入视频 / Input video not found: {src}")
    if dst.exists(): raise FileExistsError(f"为保护现有文件，不会覆盖 / Refusing to overwrite: {dst}")
    times=[float(x) for x in a.times.split(",")]
    r=imageio_ffmpeg.read_frames(str(src),pix_fmt="rgb24",bpp=3); m=next(r)
    w,h=m["size"]; fps=float(m["fps"]); wanted={round(t*fps):t for t in times}
    frames={}
    try:
        for i,b in enumerate(r):
            if not b: break
            if i in wanted: frames[wanted[i]]=np.frombuffer(b,dtype=np.uint8).reshape(h,w,3).copy()
            if len(frames)==len(wanted): break
    finally: r.close()
    if len(frames)!=len(wanted): raise ValueError("部分指定时间超出视频时长 / Some requested times exceed the video duration")
    cols=3; tile=(640,360); rows=(len(times)+cols-1)//cols
    sheet=Image.new("RGB",(cols*tile[0],rows*(tile[1]+26)),"#080d1b"); d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        x=(i%cols)*tile[0]; y=(i//cols)*(tile[1]+26)
        sheet.paste(Image.fromarray(frames[t]).resize(tile),(x,y+24)); d.text((x+8,y+4),f"t={t:.2f}s",fill="white")
    dst.parent.mkdir(parents=True,exist_ok=True); sheet.save(dst)
    print(f"已保存 / Saved {dst}; {w}x{h}，{fps:g} fps")
if __name__=="__main__": main()
