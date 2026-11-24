"""Story cafe mix (2026-11-24). Mix dialogue clips (aud/<key>_f.wav, placed per timeline.json cues) + simple synthesized SFX onto silent.mp4 -> final.mp4.
Usage: run inside the work dir that holds silent.mp4, timeline.json and aud/. Adjust SFX event keys to the scenario."""
import json,subprocess
tl=json.load(open('timeline.json')); c=tl['cfg']['cues']; E=tl['cfg']['ev']; T=tl['total']
inp=[];f=[];lab=[]; i=1
for k,(s,d) in c.items():
    inp+=['-i',f'aud/{k}_f.wav']; f.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=mono,adelay={int(s*1000)}[s{i}]"); lab.append(f"[s{i}]"); i+=1
def sfx(expr,dur,at,vol):
    global i
    inp.extend(['-f','lavfi','-t',str(dur),'-i',f"aevalsrc='{expr}':s=44100"])
    f.append(f"[{i}:a]volume={vol},afade=t=out:st={dur*0.6:.3f}:d={dur*0.4:.3f},aformat=channel_layouts=mono,adelay={int(at*1000)}[s{i}]"); lab.append(f"[s{i}]"); i+=1
CLICK="sin(2*PI*2200*t)*exp(-60*t)"; ERR="(sin(2*PI*160*t)+0.5*sin(2*PI*240*t))*0.5"
for ck in ['add','tap']: sfx(CLICK,0.06,E[ck],0.5)
for p in ['s1','s2','s3','p4']: sfx("sin(2*PI*(500+700*t)*t)*0.35",0.25,E[p],0.2)
for ek in [k for k in E if k.startswith('err')]: sfx(ERR,0.35,E[ek],0.35)
if 'ok' in E:  # POS approval beep (soft double)
    sfx("sin(2*PI*880*t)*exp(-6*t)",0.18,E['ok'],0.35); sfx("sin(2*PI*1320*t)*exp(-5*t)",0.4,E['ok']+0.13,0.35)
if 'b1s' in E: sfx("sin(2*PI*1200*t)*exp(-25*t)",0.12,E['b1s'],0.3)
if 'cta' in E: sfx("sin(2*PI*(300+900*t)*t)*0.4",0.4,E['cta'],0.25)
f.append(''.join(lab)+f"amix=inputs={len(lab)}:normalize=0,apad,atrim=0:{T:.2f},alimiter=limit=0.95[a]")
subprocess.run(['ffmpeg','-y','-v','error','-i','silent.mp4',*inp,'-filter_complex',';'.join(f),'-map','0:v','-map','[a]','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-profile:v','high','-level','4.1','-c:a','aac','-b:a','160k','-ar','44100','-shortest','-movflags','+faststart','final.mp4'],check=True)
