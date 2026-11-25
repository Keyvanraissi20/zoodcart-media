"""2026-11-25 REEL "grocery-tap" (حضوری, supermarket checkout abroad). Usage: build_2026-11-25-grocery-tap.py <workdir> preview <t1,..> | video
Workdir needs scene.html (copy of scene_2026-11-25-grocery-tap.html), font/, aud/<key>_f.wav."""
import json,sys,subprocess,wave,array,math,os
S=sys.argv[1]; mode=sys.argv[2]
A=S+'/aud/'
def dur(k):
    p=A+k+'_f.wav'
    if not os.path.exists(p): return 2.6
    w=wave.open(p); return w.getnframes()/w.getframerate()
def amps(k):
    p=A+k+'_f.wav'
    if not os.path.exists(p): return [0]
    w=wave.open(p); sr=w.getframerate(); d=array.array('h',w.readframes(w.getnframes()))
    n=sr//30; out=[]
    for i in range(0,len(d),n):
        c=d[i:i+n]; out.append(math.sqrt(sum(x*x for x in c)/max(1,len(c)))/32768)
    m=max(out) or 1; out=[min(1,(x/m)**0.8) for x in out]
    return [round((out[max(0,i-1)]+out[i]*2+out[min(len(out)-1,i+1)])/4,3) for i in range(len(out))]
K=['hook','r1','c1','m1','r2','m2','r3','cta']
D={k:dur(k) for k in K}
cues={};E={}
t=0.25; cues['hook']=[t,D['hook']]; E['dec1']=t+D['hook']*0.8; t+=D['hook']+0.1
E['r1s']=t; cues['r1']=[t,D['r1']]; E['retry']=t+0.2; E['dec2']=t+min(1.3,D['r1']*0.4); t+=D['r1']+0.1
E['c1s']=t; cues['c1']=[t,D['c1']]; t+=D['c1']
E['minaIn']=t-0.2; t=E['minaIn']+0.45
E['m1s']=t; cues['m1']=[t,D['m1']]; E['wal']=t+D['m1']*0.45; t+=D['m1']+0.1
E['r2s']=t; cues['r2']=[t,D['r2']]; t+=D['r2']+0.1
E['m2s']=t; cues['m2']=[t,D['m2']]; E['add']=t+0.25; E['pos2']=max(E['add']+1.2,t+D['m2']*0.55); E['tap']=max(t+D['m2'],E['pos2']+1.0); E['ok']=E['tap']+0.8
t=E['ok']+0.25
E['r3s']=t; cues['r3']=[t,D['r3']]; t+=D['r3']+0.5
E['cta']=t; cues['cta']=[t+0.3,D['cta']]
total=cues['cta'][0]+D['cta']+1.1
RZ={'who':'رضا','col':'#0C8599'}; MN={'who':'مینا','col':'#12B886'}; KS={'who':'صندوق‌دار','col':'#E03131'}
lines={'hook':{'who':'','t':'سبد خرید پُره، صف پشت سرت طولانیه...<br>و کارتت قبول نمی‌شه!'},
'r1':{**RZ,'t':'ای وای! دوباره رد شد!<br>این کارت اینجا کار نمی‌کنه!'},
'c1':{**KS,'t':'ببخشید، پرداخت انجام نشد.<br>کارت دیگه‌ای دارید؟'},
'm1':{**MN,'t':'نگران نباش رضا! کارت ویزای مجازی<br>زودکارت رو بزن توی ولت گوشیت.'},
'r2':{**RZ,'t':'با گوشی؟ چطوری؟'},
'm2':{**MN,'t':'ببین، اضافه شد!<br>حالا گوشی رو بگیر روی کارتخوان.'},
'r3':{**RZ,'t':'پرداخت شد! چقدر راحت بود!'}}
cfg={'cues':cues,'ev':E,'lines':lines}
AM={k:amps(k) for k in D}
json.dump({'cfg':cfg,'total':total},open(S+'/timeline.json','w'),ensure_ascii=False,indent=1)
html=open(S+'/scene.html').read().replace('<script>',f'<script>window.CUES={json.dumps(cfg,ensure_ascii=False)};window.AMPS={json.dumps(AM)};</script><script>',1)
open(S+'/scene_built.html','w').write(html)
print('total',round(total,2),{k:round(v,2) for k,v in E.items()})
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920}); pg.goto('file://'+S+'/scene_built.html'); pg.wait_for_timeout(500)
    pg.evaluate("document.fonts.ready")
    pg.on('console',lambda m:print('JS',m.text))
    if mode=='preview':
        for t in [float(x) for x in sys.argv[3].split(',')]:
            pg.evaluate(f"render({t})"); pg.screenshot(path=f"{S}/pv_{t}.png")
    else:
        n=int(total*30)
        ff=subprocess.Popen(['ffmpeg','-y','-v','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',S+'/silent.mp4'],stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i/30})"); ff.stdin.write(pg.screenshot(type='jpeg',quality=93))
        ff.stdin.close(); ff.wait()
    b.close()
