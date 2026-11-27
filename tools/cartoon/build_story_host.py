"""2026-11-27 story (F2 host, حضوری). Usage: build_story_trip.py <workdir> preview <t1,t2,..> | video
Workdir needs scene.html (copy of scene_story_host.html), font/, aud/<key>_f.wav."""
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
K=['n1','h1','h2','h3','c1','h4','h5','n2']
D={k:dur(k) for k in K}
cues={};E={}
t=0.25; cues['n1']=[t,D['n1']]; E['no']=t+D['n1']*0.8; t+=D['n1']+0.15
E['h1']=t; cues['h1']=[t,D['h1']]; t+=D['h1']+0.1
E['w']=t; cues['h2']=[t,D['h2']]; E['add']=t+D['h2']*0.6; t=max(t+D['h2'],E['add']+1.0)+0.1
E['p1']=t; cues['h3']=[t,D['h3']]; E['t1']=t+D['h3']*0.55; E['k1']=E['t1']+0.7; t=max(t+D['h3'],E['k1']+0.2)+0.05
cues['c1']=[t,D['c1']]; t+=D['c1']+0.1
E['p2']=t; cues['h4']=[t,D['h4']]; E['t2']=t+D['h4']*0.45; E['k2']=E['t2']+0.7; t=max(t+D['h4'],E['k2']+1.1)+0.1
E['p3']=t; cues['h5']=[t,D['h5']]; E['t3']=t+D['h5']*0.35; E['k3']=E['t3']+0.7; t=max(t+D['h5'],E['k3']+0.8)+0.15
E['cta']=t; cues['n2']=[t+0.2,D['n2']]
total=cues['n2'][0]+D['n2']+1.0
HK={'who':'کیان','col':'#1C7ED6'}; CS={'who':'فروشنده','col':'#7048E8'}
lines={'n1':{'who':'','t':'کارت مجازی فقط برای خرید اینترنتیه؟<br>نه!'},
'h1':{**HK,'t':'سلام، من کیانم! سه جا نشونت می‌دم که با گوشی<br>و ویزا کارت زودکارت، حضوری پرداخت می‌کنی.'},
'h2':{**HK,'t':'اول کارت رو به اپل‌پی یا گوگل‌پی اضافه کن.'},
'h3':{**HK,'t':'یک: صندوق کتاب‌فروشی.<br>گوشی رو نزدیک کارتخوان می‌بری، تمام!'},
'c1':{**CS,'t':'پرداخت انجام شد، ممنون!'},
'h4':{**HK,'t':'دو: دستگاه فروش خودکار.<br>یه تپ، و نوشیدنیت آماده‌ست.'},
'h5':{**HK,'t':'سه: کارتخوان تاکسی توی سفر.<br>دیگه لازم نیست دنبال پول نقد بگردی.'}}
cfg={'cues':cues,'ev':E,'lines':lines}
AM={k:amps(k) for k in D}
json.dump({'cfg':cfg,'total':total},open(S+'/timeline.json','w'),ensure_ascii=False,indent=1)
html=open(S+'/scene.html').read().replace('<script>',f'<script>window.CUES={json.dumps(cfg,ensure_ascii=False)};window.AMPS={json.dumps(AM)};</script><script>',1)
open(S+'/scene_built.html','w').write(html)
print('total',round(total,2),{k:round(v,2) for k,v in E.items()})
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920}); pg.on('pageerror',lambda e:print('JSERR',e)); pg.goto('file://'+S+'/scene_built.html'); pg.wait_for_timeout(500)
    pg.evaluate("document.fonts.ready")
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
