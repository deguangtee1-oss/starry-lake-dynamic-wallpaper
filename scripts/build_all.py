from __future__ import annotations
import argparse, os, subprocess, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description="Rebuild V8 through V11 from a supplied V7 source MP4")
    p.add_argument("--v7-input",required=True,help="Path to your V7 source MP4")
    p.add_argument("--output-dir",default="outputs",help="New directory for generated versions")
    a=p.parse_args(); src=Path(a.v7_input).expanduser().resolve(); out=Path(a.output_dir).expanduser().resolve()
    if not src.is_file(): raise FileNotFoundError(src)
    names=[f"Starry_Lake_Wallpaper_V{i}.mp4" for i in range(8,12)]
    existing=[str(out/n) for n in names if (out/n).exists()]
    if existing: raise FileExistsError("Will not overwrite existing versions: " + ", ".join(existing))
    out.mkdir(parents=True,exist_ok=True)
    scripts=Path(__file__).parent
    def run(script, inp, name):
        target=out/name
        subprocess.run([sys.executable,str(scripts/script),"--input",str(inp),"--output",str(target)],check=True)
        return target
    v8=run("create_v8_refined.py",src,names[0])
    v9=run("create_v9.py",v8,names[1])
    v10=run("create_v10.py",v9,names[2])
    v11=run("create_v11.py",v10,names[3])
    print("Rebuilt:")
    for f in (v8,v9,v10,v11): print(f)
if __name__=="__main__": main()
