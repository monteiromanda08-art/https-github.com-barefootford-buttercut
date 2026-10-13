import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
font = ImageFont.truetype(sys.argv[1], 150)
text = "MIGUEL PEREIRA"
out = sys.argv[2]
W,H = 1920,1080
full_w = font.getbbox(text)[2]
x0 = (W-full_w)//2
states = []
for i in range(1, len(text)+1):
    s = text[:i]
    if s.endswith(' '): continue
    states.append(s)
for n,s in enumerate(states):
    img = Image.new('RGBA',(W,H),(0,0,0,0))
    # soft shadow
    sh = Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(sh)
    d.text((x0+6,H//2+8), s, font=font, fill=(0,0,0,150), anchor='lm')
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, sh)
    d = ImageDraw.Draw(img)
    d.text((x0,H//2), s, font=font, fill=(236,232,48,255), anchor='lm', stroke_width=5, stroke_fill=(52,50,10,255))
    img.save(f"{out}/t{n:02d}.png")
print(len(states))
