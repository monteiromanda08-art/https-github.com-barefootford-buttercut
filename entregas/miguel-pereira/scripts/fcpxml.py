import json, subprocess, wave, numpy as np, os
from fractions import Fraction as F
from xml.sax.saxutils import escape, quoteattr
E=json.load(open('edl.json'))
FULL={'5F185EE0.mov':'5F185EE0-9371-49D7-AE0F-C156493430C3.mov','449F6C65.mov':'449F6C65-DDA0-4EC3-BE63-2DDF1A225D75.mov',
'4D6AB734.mov':'4D6AB734-FE69-45E3-B665-926E4C66FDA4.mov','0A66FB80.mov':'0A66FB80-5EEF-4138-971B-134CE743D7C3.mov',
'1DA2D215.mov':'1DA2D215-7006-4077-91D2-2ED42A815279.mov','E8297F3E.mov':'E8297F3E-189F-48B3-B096-B60BC0DA18F8.mov',
'5838BD9C.mov':'5838BD9C-7CD6-4E89-A1E0-889660E025D7.mov','94AF54F7.mov':'94AF54F7-DA87-4DFD-853A-34FE5EAEF59D.mov',
'772A1458.mov':'772A1458-25F9-41BE-992B-BE3FCEED3154.mov','7A69483E.mov':'7A69483E-7E7C-4399-A8B5-48E4393D88CD.mov',
'ScreenRecording.mp4':'ScreenRecording_10-10-2026 4-03-36 PM_1.mp4','DDED3DA4.mov':'DDED3DA4-52F0-4BBD-BF98-7003BE161E2E.mov',
'8838CEB4.mov':'8838CEB4-323E-43B5-A69B-8F80ED6EEB89.mov','335742B9.mov':'335742B9-A107-4CD3-880C-CA21C22355C1.mov',
'DD455817.mov':'DD455817-748E-4C4F-9CEA-23582823C52A.mov','4A409023.mov':'4A409023-72FB-4EA4-A0BF-A9417894A022.mov',
'A609BD42.mov':'A609BD42-4392-4818-AEBB-CB8D91AD9CFD.mov','8880A6A4.mov':'8880A6A4-DEED-4201-AD2C-AAAEBD9A3188.mov',
'54C82C29.mov':'54C82C29-5554-4A2B-95AF-5FBD35EA1F49.mov','519DDDB0.mov':'519DDDB0-F963-4E12-9DFA-56D8B3F7C119.mov',
'EFB8C000.mov':'EFB8C000-08F0-40E3-BBC7-41C6FEA4E314.mov','D1A00AAA.mov':'D1A00AAA-5FF1-441E-A9FA-09AAC6942AC2.mov'}
def full(n): return FULL.get(n,n)
def t(x, den=60):  # rational seconds
    fr=F(round(x*den),den); return f"{fr.numerator}/{fr.denominator}s" if fr.denominator!=1 else f"{fr.numerator}s"
def tl(x): return t(x,30)
def probe(p):
    o=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',p],capture_output=True,text=True).stdout)
    v=[s for s in o['streams'] if s['codec_type']=='video'][0]; a=[s for s in o['streams'] if s['codec_type']=='audio']
    rot=0
    for sd in v.get('side_data_list',[]): rot=int(sd.get('rotation',0))
    w,h=int(v['width']),int(v['height'])
    if abs(rot)==90: w,h=h,w
    return dict(dur=float(o['format']['duration']),w=w,h=h,fps=v['r_frame_rate'],ach=int(a[0]['channels']) if a else 0,ar=int(a[0]['sample_rate']) if a else 48000)
srcs=sorted(set(e['src'] for e in E))
fmts={}; res=['<format id="r0" name="FFVideoFormat1080p30" frameDuration="1/30s" width="1920" height="1080"/>']
assets={}
for i,s in enumerate(srcs):
    p=probe('../src/'+s); n,d=map(int,p['fps'].split('/')); key=(p['w'],p['h'],n,d)
    if key not in fmts:
        fid=f"f{len(fmts)+1}"; fmts[key]=fid
        res.append(f'<format id="{fid}" frameDuration="{d}/{n}s" width="{p["w"]}" height="{p["h"]}"/>')
    aid=f"a{i+1}"; assets[s]=(aid,p)
    nm=full(s)
    res.append(f'<asset id="{aid}" name={quoteattr(nm)} start="0s" duration="{t(p["dur"],600)}" hasVideo="1" hasAudio="1" format="{fmts[key]}" audioSources="1" audioChannels="{p["ach"]}" audioRate="{p["ar"]}">'
               f'<media-rep kind="original-media" src={quoteattr("file:./MIDIA/"+nm.replace(" ","%20"))}/></asset>')
res.append('<asset id="aT" name="titulo_MIGUEL_PEREIRA_alpha.mov" start="0s" duration="4.8s" hasVideo="1" format="r0"><media-rep kind="original-media" src="file:./titulo_MIGUEL_PEREIRA_alpha.mov"/></asset>')
total=sum(e['dur'] for e in E)
res.append(f'<asset id="aM" name="trilha_musica.wav" start="0s" duration="{t(total,30)}" hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000"><media-rep kind="original-media" src="file:./trilha_musica.wav"/></asset>')
def gain_db(i,e):
    subprocess.run(['ffmpeg','-v','error','-y','-i',f'seg/{i:03d}.mov','-vn','-ac','2','-ar','48000','-c:a','pcm_s16le','tmpx.wav'],check=True)
    w=wave.open('tmpx.wav'); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    rms=np.sqrt((a**2).mean())+1e-6; target=10**((-19 if e['nat']>=0.9 else -30)/20)
    g=min(target/rms,10**(14/20))*(e['nat'] if e['nat']<0.9 else 1.0)
    return 20*np.log10(max(g,1e-4))
spine=[]
for i,e in enumerate(E):
    aid,p=assets[e['src']]
    xf=''
    if e['mode']=='rot':
        # portrait-stored landscape footage: fit (0.28125) then rotate 90 CCW and scale to fill 16:9
        xf='<adjust-transform position="0 0" scale="1.77778 1.77778" rotation="90"/>'
    inner=f'<adjust-conform type="fit"/>{xf}<adjust-volume amount="{gain_db(i,e):+.1f}dB"/>'
    if i==0:
        inner+=f'<asset-clip ref="aM" lane="-1" offset="{t(e['in'],60)}" name="trilha_musica.wav" start="0s" duration="{tl(total)}" audioRole="music"/>'
    if i==1:
        inner+=f'<asset-clip ref="aT" lane="1" offset="{t(e["in"],60)}" name="titulo MIGUEL PEREIRA" start="0s" duration="4.8s"/>'
    nm=full(e['src'])
    spine.append(f'<asset-clip ref="{aid}" offset="{tl(e["rec"])}" name={quoteattr(nm)} start="{t(e["in"],60)}" duration="{tl(e["dur"])}" tcFormat="NDF">{inner}</asset-clip>')
xml=f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.9">
<resources>
{chr(10).join(res)}
</resources>
<library>
<event name="Miguel Pereira">
<project name="Miguel Pereira - viagem (90s)">
<sequence format="r0" duration="{tl(total)}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
<spine>
{chr(10).join(spine)}
</spine>
</sequence>
</project>
</event>
</library>
</fcpxml>
'''
open('../deliver/Miguel_Pereira_timeline.fcpxml','w').write(xml)
print('ok', len(spine))
