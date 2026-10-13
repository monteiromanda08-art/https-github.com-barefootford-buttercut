import json
R,L,V='rot','land','vert'
def c(src,i,d,mode,nat=0.25,duck=False,sec=''): return dict(src=src,**{'in':i},dur=d,mode=mode,nat=nat,duck=duck,sec=sec)
E=[]
E.append(c('4A409023.mov',8.45,4.2,R,1.0,True,'open'))
for src,i,m in [('IMG_2852.MOV',2.6,L),('449F6C65.mov',2.5,R),('IMG_2850.MOV',4.3,L),('54C82C29.mov',1.2,R),('519DDDB0.mov',1.0,R),('IMG_2979.MOV',2.5,L),
                ('8838CEB4.mov',10.0,R),('1DA2D215.mov',4.5,R),('IMG_2933.MOV',91.0,L),('DD455817.mov',20.0,R),('0A66FB80.mov',1.0,R),('5838BD9C.mov',5.0,R)]:
    E.append(c(src,i,0.2,m,0.0,False,'flash'))
E.append(c('IMG_2857.MOV',0.5,2.4,L,0.2,False,'titlehold'))
M=[('54C82C29.mov',6.0,1.2,R),('519DDDB0.mov',2.0,1.2,R),('4A409023.mov',4.4,1.2,R),
   ('IMG_2850.MOV',1.8,3.6,L,0.9,True),('449F6C65.mov',1.0,1.2,R),('IMG_2852.MOV',1.6,1.2,L),('DDED3DA4.mov',1.0,1.2,R),
   ('D1A00AAA.mov',3.0,1.2,V),('IMG_2852.MOV',10.8,4.2,L,1.0,True),('IMG_2858.MOV',26.0,1.2,V),('IMG_2878.MOV',4.0,1.2,L,0.6),
   ('IMG_2853.MOV',16.6,2.4,V,1.0,True),
   ('IMG_2924.MOV',0.0,3.0,L,1.0,True),('5838BD9C.mov',5.0,1.2,R),('772A1458.mov',14.2,3.6,R,1.0,True),
   ('A609BD42.mov',1.0,1.2,R),('8880A6A4.mov',1.0,1.2,V),('5F185EE0.mov',20.0,1.2,V),
   ('IMG_2933.MOV',2.0,1.2,L),('4D6AB734.mov',31.0,3.0,R,1.0,True),('94AF54F7.mov',25.4,4.8,R,1.0,True),
   ('94AF54F7.mov',16.0,1.2,R),('IMG_2933.MOV',90.5,1.2,L),('1DA2D215.mov',10.5,3.6,R,1.0,True),('IMG_2933.MOV',93.5,1.2,L),
   ('IMG_2970.MOV',1.5,1.2,V),('VIDEO-2026-10-11-19-00-26.mp4',1.0,1.2,V),('8838CEB4.mov',8.0,1.2,R),('DD455817.mov',20.0,1.2,R),
   ('VIDEO-2026-10-11-18-44-17.mp4',0.0,3.0,V,1.0,True),('IMG_2979.MOV',1.0,2.4,L,0.6),('IMG_2980.MOV',3.0,1.2,L),
   ('0A66FB80.mov',1.0,1.2,R),('7A69483E.mov',1.0,1.2,R),('335742B9.mov',3.5,1.2,R),('IMG_3066.MOV',6.0,1.2,V),
   ('IMG_3082.MOV',21.0,2.4,V,0.7),('IMG_3093.MOV',2.0,1.2,V)]
for x in M:
    src,i,d,m=x[:4]; nat=x[4] if len(x)>4 else 0.25; duck=x[5] if len(x)>5 else False
    E.append(c(src,i,d,m,nat,duck,'montage'))
E.append(c('IMG_2933.MOV',104.8,5.4,L,1.0,True,'outro'))
t=0
for e in E: e['rec']=round(t,3); t+=e['dur']
json.dump(E,open('edl.json','w'),indent=1)
print(len(E),'segments, total',round(t,2),'s')
