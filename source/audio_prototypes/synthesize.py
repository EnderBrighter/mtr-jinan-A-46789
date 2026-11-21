"""Original procedural audio sketches; NOT recordings or identified Jinan Line 4 equipment.
No active resource-pack sound references are changed by this script.
"""
from pathlib import Path
import json
import numpy as np
import wave,subprocess,shutil
from scipy.signal import butter,sosfilt
R=Path(__file__).resolve().parent
FS=44100
rng=np.random.default_rng(405)

def fade(x,seconds=.015):
 n=min(int(seconds*FS),len(x)//2);w=np.sin(np.linspace(0,np.pi/2,n))**2
 x=x.copy();x[:n]*=w;x[-n:]*=w[::-1];return x

def tone(freq,dur,amp=.2):
 t=np.arange(round(dur*FS))/FS
 return fade(amp*(np.sin(2*np.pi*freq*t)+.13*np.sin(4*np.pi*freq*t)),.012)

def add(dst,src,time):
 a=round(time*FS);n=min(len(src),len(dst)-a)
 if n>0:dst[a:a+n]+=src[:n]

def noise(dur,low,high):
 x=rng.normal(0,1,round(dur*FS));x=sosfilt(butter(3,[low,high],btype='bandpass',fs=FS,output='sos'),x)
 return x/max(np.std(x),1e-9)

def click():
 t=np.arange(round(.085*FS))/FS
 return fade((.13*noise(.085,180,5000)+.12*np.sin(2*np.pi*185*t))*np.exp(-t*75),.003)

def slide(dur,closing=False):
 t=np.arange(round(dur*FS))/FS;s=t/dur
 f=160+(45 if closing else 75)*np.sin(np.pi*s)
 phase=2*np.pi*np.cumsum(f)/FS
 e=np.sin(np.pi*s)**.65
 return fade(e*(.018*noise(dur,150,2100)+.025*np.sin(phase)+.009*np.sin(2*phase)),.025)

def doors():
 op=np.zeros(round(2.25*FS))
 add(op,tone(880,.16,.15),.08);add(op,tone(660,.23,.15),.31)
 add(op,click(),.06);add(op,slide(1.25),.59);add(op,click()*.55,1.87)
 cl=np.zeros(round(4.0*FS))
 for i in range(6):add(cl,tone(1046.5,.15,.18),.12+i*.31)
 add(cl,slide(1.30,True),2.11);add(cl,click(),3.45)
 return op,cl

def traction(braking=False):
 dur=13.;t=np.arange(round(dur*FS))/FS;u=np.clip((t-.5)/11.7,0,1)
 speed=45*(1-u if braking else u)
 # Electrical fundamental and switching-band approximation, without claiming a supplier curve.
 fe=7+2.05*speed
 fc=np.interp(speed,[0,7,19,30,45],[440,700,610,1000,1300])
 if braking:fc=fc*.91+55
 pe=2*np.pi*np.cumsum(fe)/FS;pc=2*np.pi*np.cumsum(fc)/FS
 active=np.clip(speed/2.2,0,1)
 # Smooth spectral transitions stand in for asynchronous / synchronous PWM bands.
 blend1=np.clip((speed-14)/7,0,1);blend2=np.clip((speed-32)/7,0,1)
 async_band=np.sin(pc+1.0*np.sin(pe))+.28*np.sin(pc*2+.7*np.sin(pe*2))
 sync9=np.sin(pe*9+.30*np.sin(pe*2))+.25*np.sin(pe*15)
 sync3=np.sin(pe*6)+.28*np.sin(pe*12)
 whine=(1-blend1)*async_band+blend1*((1-blend2)*sync9+blend2*sync3)
 base=.018*np.sin(pe)+.014*np.sin(pe*2)+.012*np.sin(pe*4)
 rolling=.013*(speed/45)**1.4*noise(dur,55,1500)
 x=active*((.085 if braking else .10)*whine+base)+rolling
 if braking:
  x+=.035*np.exp(-((t-11.7)/.34)**2)*noise(dur,500,6500)
  x*=np.minimum(1,(dur-t)/.20)
 else:x*=np.clip((t-.48)/.30,0,1)
 return fade(x,.09),speed

def write(name,x):
 assert np.isfinite(x).all()
 peak=float(abs(x).max());x=x*(10**(-3/20)/peak if peak else 1)
 wav=R/(name+'.wav');ogg=R/(name+'.ogg')
 with wave.open(str(wav),'wb') as f:
  f.setnchannels(1);f.setsampwidth(2);f.setframerate(FS);f.writeframes((x*32767).round().astype('<i2').tobytes())
 subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(wav),'-c:a','libvorbis','-q:a','5',str(ogg)],check=True)
 return {'seconds':len(x)/FS,'sampleRate':FS,'channels':1,'peakDbfs':float(20*np.log10(abs(x).max())),'rmsDbfs':float(20*np.log10(np.sqrt(np.mean(x*x))))}

op,cl=doors();acc,avs=traction();dec,dvs=traction(True)
report={}
for name,x in [('door_open_generic',op),('door_close_generic',cl),('traction_start_generic',acc),('traction_brake_generic',dec)]:report[name]=write(name,x)
report['door_demo_generic']=write('door_demo_generic',np.r_[op,np.zeros(FS//2),cl])
demo=np.r_[acc,np.zeros(FS//2),dec];report['traction_demo_generic']=write('traction_demo_generic',demo)
(R/'audio_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(R/'README.md').write_text('''# 通用地铁音效试听草稿

这些音频全部由 synthesize.py 原创合成，不是济南4号线录音，也不声称复现某一品牌或型号的VVVF控制曲线。

- door_open_generic：双音提示、门机滑动与锁机构声，2.25秒。
- door_close_generic：六次关门警示音、滑动与落锁，4秒。
- traction_start_generic：0→45km/h的通用电驱动啸叫与轮轨底噪，13秒。
- traction_brake_generic：45→0km/h，使用不同的音色混合并加入低速空气制动气声，13秒。
- traction_demo_generic：起步和减速串接试听，26.5秒。
- door_demo_generic：开门和关门串接试听，6.75秒。

WAV用于试听，OGG为后续MTR集成准备。均为44.1kHz单声道，峰值-3dBFS；无第三方录音。
当前游戏仍使用已有的SP1900声音引用。本目录不会自动替换它；本轮主要用于确认音色与能力。

若要还原济南4号线，需要按实际录音测出不同车速、牵引/制动工况的音高与切换时机。硬件供应商信息本身不能确定听到的声音。
''',encoding='utf-8')
print(json.dumps(report,indent=2))
