import json, subprocess, wave, numpy as np, os
E=json.load(open('edl.json')); SR=48000
total=round(sum(e['dur'] for e in E),3); N=int(total*SR)
open_d=E[0]['dur']
# ---------- audio ----------
def rd(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    return a.reshape(-1,w.getnchannels())
nat=np.zeros((N,2),np.float32)
duckenv=np.ones(N,np.float32)
for i,e in enumerate(E):
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'seg/{i:03d}.mov','-vn','-ac','2','-ar','48000','-c:a','pcm_s16le','tmp.wav'],check=True)
    a=rd('tmp.wav'); n=int(e['dur']*SR); a=a[:n]
    if len(a)<n: a=np.pad(a,((0,n-len(a)),(0,0)))
    rms=np.sqrt((a**2).mean())+1e-6
    target=10**((-19 if e['nat']>=0.9 else -30)/20)
    g=min(target/rms, 10**(14/20))*(e['nat'] if e['nat']<0.9 else 1.0)
    a=a*g
    f=int(0.012*SR); ramp=np.linspace(0,1,f)[:,None]   # tiny fades to avoid clicks
    a[:f]*=ramp; a[-f:]*=ramp[::-1]
    s=int(round(e['rec']*SR)); nat[s:s+n]+=a[:N-s]
    if e['duck'] and e['sec']!='open': duckenv[s:s+n]=0.2
# smooth duck envelope (150 ms)
k=int(0.15*SR); ker=np.ones(k)/k; duckenv=np.convolve(duckenv,ker,mode='same')
# music
subprocess.run(['python3','-I','music.py','music.wav',str(total-open_d+0.5)],check=True)
mus=rd('music.wav'); mus=mus*10**(-6/20)
M=np.zeros((N,2),np.float32); s=int(open_d*SR); m=mus[:N-s]; M[s:s+len(m)]=m
M*=duckenv[:,None]
# final fade-out of music over last 2.5s + whole mix last 0.6s
fo=int(2.5*SR); M[-fo:]*=np.linspace(1,0,fo)[:,None]
mix=nat+M
fo=int(0.6*SR); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
mix=np.clip(mix,-1,1)
w=wave.open('mix_raw.wav','w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix*32767).astype(np.int16).tobytes()); w.close()
# music-only (ducked) and nat-only stems for DaVinci
for nm,arr in (('stem_musica.wav',M),('stem_som_direto.wav',nat)):
    w=wave.open(nm,'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(arr,-1,1)*32767).astype(np.int16).tobytes()); w.close()
# ---------- video ----------
inputs=[]; fc=[]
for i,e in enumerate(E):
    inputs+=['-i',f'seg/{i:03d}.mov']
    fc.append(f"[{i}:v]tpad=stop_mode=clone:stop_duration=0.2,trim=duration={e['dur']},setpts=PTS-STARTPTS[v{i}]")
fc.append(''.join(f'[v{i}]' for i in range(len(E)))+f"concat=n={len(E)}:v=1:a=0[base]")
# title states
states=sorted(os.listdir('title')); ns=len(states)
t0=E[1]['rec']; flash_end=t0+0.2*12; hold_end=flash_end+E[13]['dur']
step=(flash_end-t0)/ns
cur='base'
for j,p in enumerate(states):
    idx=len(E)+j; inputs+=['-loop','1','-t',str(total),'-i',f'title/{p}']
    a=t0+j*step; b=(t0+(j+1)*step) if j<ns-1 else hold_end
    if j==ns-1:
        fc.append(f"[{idx}:v]format=rgba,fade=t=out:st={hold_end-0.35}:d=0.35:alpha=1[t{j}]")
    else:
        fc.append(f"[{idx}:v]format=rgba[t{j}]")
    fc.append(f"[{cur}][t{j}]overlay=enable='between(t,{a:.3f},{b:.3f})'[o{j}]"); cur=f'o{j}'
fc.append(f"[{cur}]fade=t=in:st=0:d=0.25,fade=t=out:st={total-0.6}:d=0.6,format=yuv420p[vout]")
import re
o=subprocess.run(['ffmpeg','-i','mix_raw.wav','-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
j=json.loads(o[o.rindex('{'):o.rindex('}')+1])
LN=f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
inputs+=['-i','mix_raw.wav']
cmd=['ffmpeg','-v','error','-y',*inputs,'-filter_complex',';'.join(fc),'-map','[vout]','-map',f'{len(E)+ns}:a',
     '-af',LN,'-ar','48000',
     '-c:v','libx264','-preset','slow','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-r','30',
     '-c:a','aac','-b:a','256k','-movflags','+faststart','-t',str(total),'out.mp4']
subprocess.run(cmd,check=True)
print('total',total)
