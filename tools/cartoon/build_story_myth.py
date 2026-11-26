"""2026-11-26 story (F4 myth-vs-fact quiz, آنلاین). Usage: build_story_trip.py <workdir> preview <t1,t2,..> | video
Workdir needs scene.html (copy of scene_story_myth.html), font/, aud/<key>_f.wav."""
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
K=['n1','b1','t1','b2','t2','n2']
D={k:dur(k) for k in K}
cues={};E={}
t=0.3; cues['n1']=[t,D['n1']]; t+=D['n1']+0.2
E['m1']=t; cues['b1']=[t,D['b1']]; t+=D['b1']+0.15
E['stamp']=t; cues['t1']=[t,D['t1']]; E['f1']=t+1.0; E['pay']=max(E['f1']+2.2,t+D['t1']*0.8); t=max(t+D['t1'],E['pay']+0.6)+0.2
E['g1']=t; cues['b2']=[t,D['b2']]; E['gift']=t+max(1.0,D['b2']*0.55); t=max(t+D['b2'],E['gift']+0.8)+0.15
E['s1']=t; cues['t2']=[t,D['t2']]; t=max(t+D['t2'],E['s1']+2.6)+0.3
E['cta']=t; cues['n2']=[t+0.25,D['n2']]
total=cues['n2'][0]+D['n2']+1.1
BH={'who':'بهراد','col':'#E67700'}; TR={'who':'ترانه','col':'#0CA678'}
lines={'n1':{'who':'','t':'باور یا واقعیت؟<br>بیا با هم ببینیم!'},
'b1':{**BH,'t':'اشتراک هوش مصنوعی و دوره‌ی خارجی؟<br>بدون کارت خارجی که نمی‌شه!'},
't1':{**TR,'t':'باور غلطه! ویزا کارت مجازی زودکارت رو<br>با ریال می‌خری و شارژ می‌کنی،<br>بعد سایت‌ها و اپ‌های خارجی رو پرداخت می‌کنی.'},
'b2':{**BH,'t':'واقعاً؟ پس برای تولد دوستم<br>گیفت کارت بین‌المللی می‌گیرم!'},
't2':{**TR,'t':'فقط حواست به لینک‌های مشکوک باشه؛<br>سفارش رو از خود سایت زودکارت ثبت کن.'}}
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
