"""2026-11-28 story (F1 dialogue, سفر, restaurant dinner). Usage: build_story_dinner.py <workdir> preview <t1,t2,..> | video
Workdir needs scene.html (copy of scene_story_dinner.html), font/, aud/<key>_f.wav."""
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
K=['n1','k1','g1','w1','k2','g2','c1']
D={k:dur(k) for k in K}
cues={};E={}
t=0.3; cues['n1']=[t,D['n1']]; t+=D['n1']+0.15
E['k1']=t; cues['k1']=[t,D['k1']]; t=max(t+D['k1'],E['k1']+1.8)+0.15
E['g1']=t; cues['g1']=[t,D['g1']]; t=max(t+D['g1'],E['g1']+2.2)+0.1
E['w1']=t; cues['w1']=[t,D['w1']]; E['tap']=t+max(1.3,D['w1']*0.8); E['ok']=E['tap']+0.9; t=max(t+D['w1'],E['ok'])+0.2
E['k2']=t; cues['k2']=[t,D['k2']]; t+=D['k2']+0.15
E['g2']=t; cues['g2']=[t,D['g2']]; t=max(t+D['g2'],E['g2']+1.8)+0.3
E['cta']=t; cues['c1']=[t+0.25,D['c1']]
total=cues['c1'][0]+D['c1']+1.0
KV={'who':'کاوه','col':'#0C8599'}; GN={'who':'گلناز','col':'#E8590C'}; WT={'who':'گارسون','col':'#495057'}
lines={'n1':{'who':'','t':'شامِ آخرِ سفر...<br>و صورتحساب رسید!'},
'k1':{**KV,'t':'وای! کارت بانکی ایرانی‌مون<br>که اینجا کار نمی‌کنه. حالا چطوری حساب کنیم؟'},
'g1':{**GN,'t':'نگران نباش! قبل از سفر،<br>ویزا کارت زودکارت رو به گوگل‌پی اضافه کردم.'},
'w1':{**WT,'t':'بفرمایید، گوشی‌تون رو<br>نزدیک دستگاه بگیرید.'},
'k2':{**KV,'t':'به همین راحتی؟ پرداخت شد؟ عالیه!'},
'g2':{**GN,'t':'تازه بلیط موزه‌ی فردا رو هم،<br>با همین کارت آنلاین خریدم!'}}
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
