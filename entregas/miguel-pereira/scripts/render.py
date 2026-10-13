import json, subprocess, sys, os
S=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(S,'..','src'); SEG=os.path.join(S,'seg'); os.makedirs(SEG,exist_ok=True)
edl=json.load(open(sys.argv[1]))
GRADE="eq=contrast=1.05:saturation=0.9:gamma=0.98,colorbalance=rs=0.03:gs=0.0:bs=-0.03:rh=0.02:bh=-0.02,vignette=angle=PI/9"
def vf(mode, zoom):
    z = f",scale=iw*{zoom}:ih*{zoom},crop=1920:1080" if zoom and zoom!=1 else ""
    if mode=='rot':  return f"transpose=2,scale=1920:1080{z},{GRADE}"
    if mode=='land': return f"scale=1920:1080{z},{GRADE}"
    if mode=='crop': # vertical source, crop central 16:9 band (y position offset in 'cy' 0..1)
        return None
    if mode=='vert':
        return ("split[a][b];[a]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=30:3,eq=brightness=-0.08[bg];"
                f"[b]scale=-2:1080[fg];[bg][fg]overlay=(W-w)/2:0,{GRADE}")
procs=[]
for i,s in enumerate(edl):
    out=os.path.join(SEG,f"{i:03d}.mp4")
    if os.path.exists(out) and not s.get('force'): continue
    mode=s['mode']; f=vf(mode,s.get('zoom',1))
    if mode=='crop':
        cy=s.get('cy',0.5)
        f=f"scale=1920:-2,crop=1920:1080:0:(ih-1080)*{cy},{GRADE}"
    speed=s.get('speed',1.0)
    if speed!=1.0: f+=f",setpts=PTS/{speed}"
    f+=",fps=30,format=yuv420p"
    af=f"aresample=48000,aformat=channel_layouts=stereo"
    if speed!=1.0: af+=f",atempo={speed}"
    cmd=['ffmpeg','-v','error','-y','-ss',str(s['in']),'-t',str(s['dur']*speed),'-i',os.path.join(SRC,s['src']),
         '-filter_complex',f"[0:v]{f}[v];[0:a]{af}[a]",'-map','[v]','-map','[a]','-t',str(s['dur']),
         '-c:v','libx264','-preset','fast','-crf','16','-c:a','pcm_s16le',out.replace('.mp4','.mov')]
    cmd[-1]=out=out.replace('.mp4','.mov')
    procs.append(subprocess.Popen(cmd))
    if len(procs)>=3:
        procs.pop(0).wait()
for p in procs: p.wait()
print('done', len(edl))
