"""2026-11-25 story (F5 trip-day montage, سفر). Usage: build_story_trip.py <workdir> preview <t1,t2,..> | video
Workdir needs scene.html (copy of scene_story_trip.html), font/, aud/<key>_f.wav."""
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
K=['n1','a1','a2','a3','s1','a4','n2']
D={k:dur(k) for k in K}
cues={};E={}
t=0.3; cues['n1']=[t,D['n1']]; t+=D['n1']+0.15
E['s1']=t; cues['a1']=[t,D['a1']]; E['pay']=t+D['a1']*0.75; t=max(t+D['a1'],E['pay']+0.9)+0.35
E['s2']=t; cues['a2']=[t,D['a2']]; E['tap2']=t+max(1.2,D['a2']*0.8); E['ok2']=E['tap2']+0.8; t=max(t+D['a2'],E['ok2']+0.7)+0.3
E['s3']=t; cues['a3']=[t,D['a3']]; E['tap3']=t+max(1.2,D['a3']*0.8); E['ok3']=E['tap3']+0.8; t=max(t+D['a3'],E['ok3'])+0.15
cues['s1']=[t,D['s1']]; E['b1s']=t; t+=D['s1']+0.2
E['p4']=t; cues['a4']=[t,D['a4']]; t+=D['a4']+0.5
E['cta']=t; cues['n2']=[t+0.25,D['n2']]
total=cues['n2'][0]+D['n2']+1.1
AR={'who':'آرش','col':'#1098AD'}; SH={'who':'فروشنده','col':'#C2255C'}
lines={'n1':{'who':'','t':'یه روز سفر با ویزا کارت زودکارت!<br>ببین آرش چطوری حساب می‌کنه.'},
'a1':{**AR,'t':'توی فرودگاه، هتلمو آنلاین<br>با ویزا کارت زودکارت رزرو کردم!'},
'a2':{**AR,'t':'بلیط مترو: کارتم توی گوگل‌پی<br>گوشیمه، فقط نزدیکش می‌کنم...'},
'a3':{**AR,'t':'یه یادگاری قشنگ...<br>اینم با گوشی حساب می‌کنم!'},
's1':{**SH,'t':'پرداخت انجام شد!<br>سفر خوش بگذره!'},
'a4':{**AR,'t':'آنلاین، حضوری، توی سفر...<br>همه‌ش با یه ویزا کارت!'}}
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
