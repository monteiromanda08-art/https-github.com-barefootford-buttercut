import numpy as np, wave, sys
SR=48000; BPM=100; B=60/BPM; DUR=float(sys.argv[2]); N=int(SR*DUR)
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,t,pan=0.0,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig))
    if i>=N: return
    s=sig[:j-i]*g; L[i:j]+=s*(1-pan)/1; R[i:j]+=s*(1+pan)/1
def env(n,a,d):
    t=np.arange(n)/SR; e=np.exp(-t/d); ai=int(a*SR)
    if ai>0: e[:ai]*=np.linspace(0,1,ai)
    return e
def kick():
    n=int(.35*SR); t=np.arange(n)/SR; f=50+90*np.exp(-t/.04)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.13)*0.9
def snare():
    n=int(.25*SR); t=np.arange(n)/SR
    return (rng.standard_normal(n)*np.exp(-t/.06)*0.35+np.sin(2*np.pi*190*t)*np.exp(-t/.05)*0.25)
def hat(o=False):
    n=int((.18 if o else .05)*SR); x=rng.standard_normal(n); x=np.diff(np.concatenate([[0],x]))
    return x*np.exp(-np.arange(n)/SR/(.06 if o else .015))*0.12
def note(f,dur,kind='pad'):
    n=int(dur*SR); t=np.arange(n)/SR
    if kind=='pad':
        s=sum(np.sin(2*np.pi*f*k*(1+0.002*d)*t)/k**1.6 for k in range(1,6) for d in (-1,1))/2
        e=np.minimum(1,t/.08)*np.minimum(1,(dur-t)/.25).clip(0)
        return s*e*0.06
    if kind=='bass':
        s=np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t)
        return s*env(n,.005,.35)*0.32
    if kind=='pluck':
        s=sum(np.sin(2*np.pi*f*k*t)/k**2 for k in range(1,5))
        return s*env(n,.002,.18)*0.13
m2f=lambda m:440*2**((m-69)/12)
# A major: A  E  F#m  D
prog=[(57,[57,61,64,69]),(52,[56,59,64,68]),(54,[57,61,66,69]),(50,[54,57,62,66])]
mel=[76,None,73,76,None,78,76,73, 71,None,68,71,None,73,71,68, 69,None,73,76,None,78,76,73, 74,None,73,71,None,69,68,None]
bar=4*B; nb=int(DUR/bar)+1
for b in range(nb):
    t0=b*bar; root,ch=prog[b%4]
    intro = b<2
    for c in ch: add(note(m2f(c),bar),t0,pan=0.2*((c%3)-1))
    for k in range(4):
        add(kick(),t0+k*B, g=(0.55 if intro else 1)*(1 if k%2==0 else 0.0) + (0 if intro else (0.6 if k==3 and b%2 else 0)))
        if not intro and k%2==1: add(snare(),t0+k*B,g=0.9)
        add(hat(),t0+k*B+B/2,pan=0.3,g=1 if not intro else .5)
        if not intro: add(hat(),t0+k*B,pan=-0.3,g=.5)
    if not intro:
        for k,off in enumerate([0,1.5,2,3,3.5]):
            add(note(m2f(root-12 if k!=3 else root-5),B*0.9,'bass'),t0+off*B)
    if b>=4:
        for k in range(8):
            m=mel[(b%4)*8+k]
            if m: add(note(m2f(m),B,'pluck'),t0+k*B/2,pan=-0.25)
# fade in/out
fi=int(.5*SR); fo=int(2.5*SR)
for X in (L,R): X[:fi]*=np.linspace(0,1,fi); X[-fo:]*=np.linspace(1,0,fo)
mx=max(abs(L).max(),abs(R).max()); L/=mx/0.8; R/=mx/0.8
# simple 'tape' warmth: soft clip
L=np.tanh(L*1.2)/np.tanh(1.2); R=np.tanh(R*1.2)/np.tanh(1.2)
st=(np.stack([L,R],1)*32767).astype(np.int16)
w=wave.open(sys.argv[1],'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
