"""2026-11-27 REEL "game-sofa" (آنلاین, siblings on a living-room sofa buying a game on a foreign site). Usage: build_2026-11-27-game-sofa.py <workdir> preview <t1,..> | video
Workdir needs scene.html (copy of scene_2026-11-27-game-sofa.html), font/, aud/<key>_f.wav."""
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
K=['hook','a1','p1','a2','p2','a3','cta']
D={k:dur(k) for k in K}
cues={};E={}
t=0.25; cues['hook']=[t,D['hook']]; E['f1']=t+D['hook']*0.8; t+=D['hook']+0.1
E['a1s']=t; cues['a1']=[t,D['a1']]; E['retry']=t+0.5; E['f2']=t+min(1.5,D['a1']*0.45); t+=D['a1']+0.1
E['p1s']=t; cues['p1']=[t,D['p1']]; E['zc']=t+D['p1']*0.55; t+=D['p1']+0.1
E['a2s']=t; cues['a2']=[t,D['a2']]; t+=D['a2']+0.1
E['p2s']=t; cues['p2']=[t,D['p2']]; E['k1']=t+D['p2']*0.12; E['k2']=t+D['p2']*0.4; E['k3']=t+D['p2']*0.58; E['co']=t+D['p2']*0.7
E['pay']=max(t+D['p2']+0.05,E['co']+1.6); E['ok']=E['pay']; E['dl']=E['ok']+0.5; t=E['ok']+0.35
E['a3s']=t; cues['a3']=[t,D['a3']]; E['dlEnd']=t+D['a3']+0.2; t+=D['a3']+0.4
E['cta']=t; cues['cta']=[t+0.3,D['cta']]
total=cues['cta'][0]+D['cta']+0.7
AV={'who':'آوا','col':'#E64980'}; PO={'who':'پویا','col':'#E67700'}
lines={'hook':{'who':'','t':'بازی‌ای که ماه‌ها منتظرش بودی اومده...<br>ولی پرداختت انجام نمی‌شه!'},
'a1':{**AV,'t':'پویا! سه بار زدم، باز نوشت پرداخت ناموفق!<br>این بازی رو چطوری بخرم؟'},
'p1':{**PO,'t':'آوا جان، اون سایت خارجیه. من خریدهام رو<br>با ویزا کارت مجازی زودکارت انجام می‌دم.'},
'a2':{**AV,'t':'ویزا کارت؟ گرفتنش سخت نیست؟'},
'p2':{**PO,'t':'نه! احراز هویت می‌کنی، با کارت بانکی خودت<br>شارژش می‌کنی، بعد شماره‌ی کارت رو وارد کن.'},
'a3':{**AV,'t':'وای، پرداخت شد!<br>دانلودش هم شروع شد!'}}
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
