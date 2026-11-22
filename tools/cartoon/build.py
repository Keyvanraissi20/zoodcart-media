import json,sys,subprocess,wave,array,math,os
S=sys.argv[1]; mode=sys.argv[2]  # 'preview' or 'video'
A=S+'/aud/'
def dur(k):
    p=A+k+'_f.wav'
    if not os.path.exists(p): return 3.2
    w=wave.open(p); return w.getnframes()/w.getframerate()
def amps(k):
    p=A+k+'_f.wav'
    if not os.path.exists(p): return [0]
    w=wave.open(p); sr=w.getframerate(); d=array.array('h',w.readframes(w.getnframes()))
    n=sr//30; out=[]
    for i in range(0,len(d),n):
        c=d[i:i+n]; r=math.sqrt(sum(x*x for x in c)/max(1,len(c)))/32768; out.append(r)
    m=max(out) or 1; out=[min(1,(x/m)**0.8) for x in out]
    # smooth
    return [round((out[max(0,i-1)]+out[i]*2+out[min(len(out)-1,i+1)])/4,3) for i in range(len(out))]
D={k:dur(k) for k in ['n1','a1','a2','b1','a3','a4','n2b']}
cues={};E={}
t=0.35; cues['n1']=[t,D['n1']]; t+=D['n1']
E['click1']=t+0.55; E['err1']=E['click1']+0.75
cues['a1']=[E['err1']+0.15,D['a1']]
E['click2']=cues['a1'][0]+D['a1']*0.55; E['err2']=E['click2']+0.55
t=max(cues['a1'][0]+D['a1'],E['err2']+0.3)+0.25
cues['a2']=[t,D['a2']]; E['a2s']=t; t+=D['a2']
E['bEnter']=t+0.05; t=E['bEnter']+0.6
cues['b1']=[t,D['b1']]; E['b1s']=t
E['cardShow']=t+D['b1']*0.32
t+=D['b1']+0.2
cues['a3']=[t,D['a3']]; E['a3s']=t; E['cardHide']=t-0.1; E['cardFill']=t
E['click3']=t+D['a3']+0.15; E['success']=E['click3']+0.6
cues['a4']=[E['success']+0.2,D['a4']]
E['cta']=cues['a4'][0]+D['a4']+0.35
cues['n2b']=[E['cta']+0.45,D['n2b']]
total=cues['n2b'][0]+D['n2b']+1.3
lines={'n1':{'who':'','t':'وقتی می‌خوای یه پرداخت خارجی انجام بدی، ولی...'},
'a1':{'who':'امیر','col':'#7C3AED','t':'اَه! بازم خطا داد!<br>هر کاری می‌کنم پرداخت انجام نمی‌شه!'},
'a2':{'who':'امیر','col':'#7C3AED','t':'دیگه نمی‌دونم چی‌کار کنم...'},
'b1':{'who':'سینا','col':'#0CA678','t':'چرا خودتو اذیت می‌کنی؟ از زودکارت یه ویزا کارت مجازی بخر؛ با اون پرداخت‌های بین‌المللیت رو راحت انجام می‌دی!'},
'a3':{'who':'امیر','col':'#7C3AED','t':'جدی؟ بزن بریم!'},
'a4':{'who':'امیر','col':'#7C3AED','t':'وااای! پرداخت شد!<br>مرسی رفیق!'},
'n2b':{'who':'','t':''}}
cfg={'cues':cues,'ev':E,'lines':{k:v for k,v in lines.items() if v['t']}}
AM={k:amps(k) for k in D}
json.dump({'cfg':cfg,'total':total},open(S+'/timeline.json','w'),ensure_ascii=False,indent=1)
html=open(S+'/scene.html').read().replace('<script>',f'<script>window.CUES={json.dumps(cfg,ensure_ascii=False)};window.AMPS={json.dumps(AM)};</script><script>',1)
open(S+'/scene_built.html','w').write(html)
print('total',round(total,2),{k:[round(a,2),round(b,2)] for k,(a,b) in cues.items()},{k:round(v,2) for k,v in E.items()})
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920}); pg.goto('file://'+S+'/scene_built.html'); pg.wait_for_timeout(500)
    pg.evaluate("document.fonts.ready")
    if mode=='preview':
        ts=[float(x) for x in sys.argv[3].split(',')]
        for t in ts:
            pg.evaluate(f"render({t})"); pg.screenshot(path=f"{S}/pv_{t}.png")
    else:
        n=int(total*30)
        ff=subprocess.Popen(['ffmpeg','-y','-v','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',S+'/silent.mp4'],stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f"render({i/30})"); ff.stdin.write(pg.screenshot(type='jpeg',quality=95))
        ff.stdin.close(); ff.wait()
    b.close()
