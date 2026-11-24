"""2026-11-24 story (F3 step-by-step, حضوری, café). Usage: build_story_cafe.py <workdir> preview <t1,t2,..> | video
Workdir needs scene.html (copy of scene_story_cafe.html), font/, aud/<key>_f.wav."""
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
K=['n1','h1','h2','h3','b1','h4','n2b']
D={k:dur(k) for k in K}
cues={};E={}
t=0.3; cues['n1']=[t,D['n1']]; t+=D['n1']+0.15
E['s1']=t; cues['h1']=[t,D['h1']]; t+=D['h1']+0.5
E['s2']=t; cues['h2']=[t,D['h2']]; E['add']=t+D['h2']*0.7; t=max(t+D['h2'],E['add']+1.0)+0.25
E['s3']=t; cues['h3']=[t,D['h3']]; E['tap']=t+max(1.2,D['h3']*0.85); E['ok']=E['tap']+0.9; t=E['ok']+0.25
cues['b1']=[t,D['b1']]; E['b1s']=t; t+=D['b1']+0.2
E['p4']=t; cues['h4']=[t,D['h4']]; t+=D['h4']+0.9
E['cta']=t; cues['n2b']=[t+0.4,D['n2b']]
total=cues['n2b'][0]+D['n2b']+1.3
NG={'who':'نگار','col':'#E8590C'}; BA={'who':'باریستا','col':'#2B8A3E'}
lines={'n1':{'who':'','t':'فکر می‌کنی با کارت مجازی<br>نمی‌شه حضوری پرداخت کرد؟'},
'h1':{**NG,'t':'قدم اول: ویزا کارت مجازیمو<br>از زودکارت گرفتم.'},
'h2':{**NG,'t':'قدم دوم: کارتو به<br>اپل‌پی یا گوگل‌پی اضافه کردم.'},
'h3':{**NG,'t':'قدم سوم: گوشیمو<br>نزدیک کارتخوان می‌برم...'},
'b1':{**BA,'t':'پرداخت انجام شد!<br>بفرمایید، قهوه‌تون.'},
'h4':{**NG,'t':'هر جا پرداخت بدون تماس ویزا رو<br>قبول کنن، با گوشیم حساب می‌کنم!'}}
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
