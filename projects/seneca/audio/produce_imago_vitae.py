#!/usr/bin/env python3
"""IMAGO VITAE : one synthetic rehearsal voice, new instrumental score, source-aligned subtitle data.
All translated English passages are editorial renderings of selected portions of Seneca Ep.26,
except the clearly marked Tacitus opening narration. This is NOT Seneca's last letter or will.
"""
import json, os, subprocess, wave, math
import numpy as np
from scipy.signal import butter, sosfilt
from pathlib import Path
import soundfile as sf
O=Path('/mnt/data/imago_vitae'); O.mkdir(exist_ok=True)
SAMPLE=24000
# (speaker, spoken text, source, latin original, corresponding English translation, pause after, language)
segments=[
 ('NARRATOR', 'Tacitus reports that Seneca asked for the writing tablets of his will.', 'Tacitus, Annals 15.62; editorial paraphrase, not an exact quotation', 'Ille interritus poscit testamenti tabulas.', None,2.3,'en'),
 ('NARRATOR', 'The centurion refused. He left his friends only what remained: the image of his life.', 'Tacitus, Annals 15.62; editorial paraphrase, not an exact quotation', 'ac denegante centurione ... imaginem vitae suae relinquere testatur', None,5.6,'en'),
 ('SENECA', 'I told you I was within sight of old age. Now I fear that old age is already behind me.', 'Seneca, Epistulae morales 26.1; original editorial English rendering, abridged', 'Modo dicebam tibi in conspectu esse me senectutis: iam vereor ne senectutem post me reliquerim.', None,3.3,'en'),
 ('SENECA', 'Years have marked my body. Yet I do not feel their injury in my mind.', 'Seneca, Epistulae morales 26.2; original editorial English rendering, abridged', 'non sentio in animo aetatis iniuriam, cum sentiam in corpore.', None,3.4,'en'),
 ('SENECA', 'Each day takes something away from our strength.', 'Seneca, Epistulae morales 26.4; original editorial English rendering', 'carpimur, singuli dies aliquid subtrahunt viribus.', None,3.3,'en'),
 ('SENECA', 'Is there a better end than slowly to dissolve, as nature releases us?', 'Seneca, Epistulae morales 26.4; original editorial English rendering', 'ecquis exitus est melior quam in finem suum natura solvente dilabi?', None,4.5,'en'),
 ('SENECA', 'I watch myself, as though the day has come which must judge all the years of my life.', 'Seneca, Epistulae morales 26.4; original editorial English rendering, abridged', 'ego certe, velut appropinquet experimentum et ille laturus sententiam de omnibus annis meis dies venerit, ita me observo et alloquor:', None,3.4,'en'),
 ('SENECA', 'I will entrust to death the measure of my progress.', 'Seneca, Epistulae morales 26.5; original editorial English rendering', 'quid profecerim morti crediturus sum.', None,3.3,'en'),
 ('SENECA', 'That day will reveal whether I only speak with courage, or truly feel it.', 'Seneca, Epistulae morales 26.5; original editorial English rendering, abridged', 'utrum loquar fortia an sentiam', None,4.6,'en'),
 ('SENECA', 'Put aside the opinions of other people. They are always uncertain.', 'Seneca, Epistulae morales 26.6; original editorial English rendering, abridged', 'Remove existimationem hominum: dubia semper est et in partem utramque dividitur.', None,2.9,'en'),
 ('SENECA', 'Put aside the studies pursued throughout your life. Death will pronounce the judgment.', 'Seneca, Epistulae morales 26.6; original editorial English rendering', 'Remove studia tota vita tractata: mors de te pronuntiatura est.', None,3.3,'en'),
 ('SENECA', 'Learned conversation and the sayings of wise men do not reveal the true strength of the soul.', 'Seneca, Epistulae morales 26.6; original editorial English rendering, abridged', 'disputationes et litterata colloquia et ex praeceptis sapientium verba collecta et eruditus sermo non ostendunt verum robur animi', None,2.9,'en'),
 ('SENECA', 'Even a frightened man may speak bravely.', 'Seneca, Epistulae morales 26.6; original editorial English rendering', 'est enim oratio etiam timidissimis audax.', None,3.4,'en'),
 ('SENECA', 'What you have done will be clear when you draw your last breath.', 'Seneca, Epistulae morales 26.6; original editorial English rendering', 'Quid egeris tunc apparebit cum animam ages.', None,6.3,'en'),
 ('SENECA', 'Accipio condicionem. Non reformido iudicium.', 'Seneca, Epistulae morales 26.6; exact Latin, punctuation normalized', 'Accipio condicionem, non reformido iudicium.', 'I accept the condition. I do not fear the judgment.', 7.3,'la'),
 ('SENECA', 'I say these things to myself. But take them as spoken to you as well.', 'Seneca, Epistulae morales 26.7; original editorial English rendering', 'Haec mecum loquor, sed tecum quoque me locutum puta.', None,3.1,'en'),
 ('SENECA', 'You are younger. What difference does it make? Years are not counted.', 'Seneca, Epistulae morales 26.7; original editorial English rendering', 'Iuvenior es: quid refert? non dinumerantur anni.', None,4.7,'en'),
 ('SENECA', 'Incertum est quo loco te mors exspectet. Itaque tu illam omni loco exspecta.', 'Seneca, Epistulae morales 26.7; exact Latin, punctuation normalized', 'Incertum est quo loco te mors exspectet; itaque tu illam omni loco exspecta.', 'You cannot know where death awaits you; therefore be ready for it everywhere.', 6.7,'la'),
 ('SENECA', 'To meditate on death is to meditate on freedom.', 'Seneca, Epistulae morales 26.10; English rendering of his reflection on an Epicurean maxim quoted in 26.8', 'Meditare mortem: qui hoc dicit meditari libertatem iubet.', None,3.7,'en'),
 ('SENECA', 'Whoever has learned how to die has unlearned how to be a slave.', 'Seneca, Epistulae morales 26.10; original editorial English rendering', 'Qui mori didicit servire dedidicit.', None,3.9,'en'),
 ('SENECA', 'There is only one chain that binds us: the love of life.', 'Seneca, Epistulae morales 26.10; original editorial English rendering', 'Una est catena quae nos alligatos tenet, amor vitae.', None,3.1,'en'),
 ('SENECA', 'We need not cast it away. Only loosen its hold, so that when necessity comes, we are ready.', 'Seneca, Epistulae morales 26.10; original editorial English rendering, abridged', 'qui ut non est abiciendus, ita minuendus est, ut si quando res exiget ... parati simus', None,7.3,'en'),
 ('SENECA', 'Vale.', 'Seneca, Epistulae morales 26.10; exact Latin closing', 'Vale.', 'Farewell.', 17.8,'la'),
]

voice_array=[]; cues=[]; playhead=12.0

def make_tts(text,language,i):
  # Deliberately understated low synthetic proof voice. One timbre for Tacitus framing and letter.
  path=O/f'voice_{i:02d}.wav'
  lang='la' if language=='la' else 'en-gb+m3'
  speed='123' if language=='la' else '129'
  pitch='33' if language=='la' else '31'
  subprocess.run(['espeak','-v',lang,'-s',speed,'-p',pitch,'-a','150','-g','5','-w',str(path),text],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  arr, sr=sf.read(path,dtype='float32')
  if arr.ndim>1:arr=arr.mean(1)
  # Pitch engine is basic; lowpass its buzzy harmonics and add gently rounded presence.
  if sr!=SAMPLE:
    from scipy.signal import resample_poly
    from math import gcd
    g=gcd(sr,SAMPLE);arr=resample_poly(arr,SAMPLE//g,sr//g).astype('float32')
  sos=butter(3,[105,3700],btype='bandpass',fs=SAMPLE,output='sos')
  arr=sosfilt(sos,arr).astype('float32')
  peak=np.max(np.abs(arr))
  if peak>1e-5:arr=arr/max(.30,peak)*.68
  fade=int(.07*SAMPLE)
  if len(arr)>fade*2:
    arr[:fade]*=np.linspace(0,1,fade,dtype=np.float32)
    arr[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)
  return arr

for i,(speaker,text,source,latin,translation,pause,language) in enumerate(segments):
  arr=make_tts(text,language,i)
  duration=len(arr)/SAMPLE
  start=round(playhead,3);end=round(playhead+duration,3)
  cue={'id':f'{i+1:02d}','speaker':speaker,'text':text,'latin':latin,
       'translation':translation,'source':source,'language':language,
       'kind':'tacitus-paraphrase' if speaker=='NARRATOR' else 'seneca-letter',
       'start':start,'end':end}
  cues.append(cue);voice_array.append((start,arr))
  playhead=end+pause

total_duration=round(math.ceil(playhead+6),1)
n=int(total_duration*SAMPLE)
print('Total duration',total_duration,'voice secs',round(sum(len(v)/SAMPLE for t,v in voice_array),2),'cues',len(cues))
voice=np.zeros(n,dtype='float32')
for t,arr in voice_array:
  at=int(t*SAMPLE);voice[at:at+len(arr)]+=arr
# Music sound bed (original continuous low-frequency drone with very slow harmonic changes).
# Produce in chunks to avoid large vector allocations. Tonal centre D minor.
score=np.zeros(n,dtype='float32')
rs=np.random.default_rng(2665)
block=4*SAMPLE
# base notes D2,A2,D3,F3,A3,C4; avoid cheap epic crescendos, build an ensemble of near-sine pad partials.
frequencies=[73.416,110.0,146.832,174.614,220.0,261.626]
# slow harmonics, amplitude, and different initial phase; no percussive attacks
weights=[.25,.12,.18,.10,.04,.024]
phases=rs.uniform(0,2*np.pi,len(frequencies))
for st in range(0,n,block):
 size=min(block,n-st);t=(np.arange(size,dtype='float64')+st)/SAMPLE
 x=np.zeros(size,dtype=np.float64)
 for j,(freq,w) in enumerate(zip(frequencies,weights)):
  swell=.62+.23*np.sin(2*np.pi*(.0045+j*.0006)*t+phases[j])
  detune=.0040*np.sin(2*np.pi*.067*t+(j*.43))
  x+=w*swell*(np.sin(2*np.pi*freq*t+detune+phases[j])+.11*np.sin(2*np.pi*(2*freq)*t+phases[j]))
 # electroacoustic air, shaped dark and far away
 hiss=rs.standard_normal(size)
 hiss=sosfilt(butter(2,530,fs=SAMPLE,output='sos'),hiss)
 x+=.012*hiss
 # distant moving subdrone
 x+=.07*np.sin(2*np.pi*(36.708+.05*np.sin(.02*t))*t)
 # slow arrival and withdrawal. Near-complete silence after last words.
 envelope=np.minimum(1.0,t/12.0)
 last_cue=cues[-1]['end']
 outro=np.clip((total_duration-4-t)/(total_duration-4-last_cue),0,1)
 envelope*=np.where(t>last_cue,outro,1)
 score[st:st+size]=(.39*x*envelope).astype('float32')
# duck under spoken words with 0.8sec fade edges
for t,arr in voice_array:
 l=max(0,int((t-.85)*SAMPLE));r=min(n,int((t+len(arr)/SAMPLE+.85)*SAMPLE));
 # envelope .5 during speech ramping in/out
 span=r-l; tt=np.arange(span,dtype='float32')/SAMPLE
 ramp=np.minimum(np.minimum(tt/.85,(span/SAMPLE-tt)/.85),1)
 duck=1-.37*np.clip(ramp,0,1)
 score[l:r]*=duck.astype('float32')
# master left/right spatial bed: timbral voice centred, pad broader
from scipy.signal import lfilter
left_score=score
right_score=.88*score+.12*np.roll(score,int(.021*SAMPLE))
mix=np.stack([np.clip(left_score+voice*.75,-.98,.98),np.clip(right_score+voice*.75,-.98,.98)],axis=1)
score_st=np.stack([left_score,right_score],axis=1)
# soft saturation, normalize without flattening performance
mix=np.tanh(mix*1.15).astype('float32')*.86
score_st=np.tanh(score_st*1.15).astype('float32')*.86
sf.write(O/'imago-vitae-letter.wav',mix,SAMPLE,subtype='PCM_16')
sf.write(O/'imago-vitae-score.wav',score_st,SAMPLE,subtype='PCM_16')
for nm in ['letter','score']:
 p=O/f'imago-vitae-{nm}'
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p)+'.wav','-ac','2','-ar','24000','-codec:a','libmp3lame','-b:a','112k','-id3v2_version','3',str(p)+'.mp3'],check=True)
# metadata JSON accessible to JS
meta={'title':'IMAGO VITAE','subtitle':'The Will He Could Not Write','duration':total_duration,
      'credits':'One synthetic rehearsal voice with one original ambient score. Opening is an explicitly credited editorial rendering of Tacitus, Annals 15.62. The remainder is selected and abridged editorial English renderings of Seneca, Epistulae Morales 26.1–10 with exact Latin excerpts. The letter predates his death and is not Seneca’s written will or last spoken words.',
      'disclaimer':'This is a curated reading, NOT the last letter of Seneca and not a surviving will. The narration is synthetic and preliminary.',
      'source_urls':['https://www.altertum.uni-rostock.de/en/hsi-digital/online-texte/sen-epist-26/','https://www.thelatinlibrary.com/tacitus/tac.ann15.shtml'],
      'cues':cues}
(O/'imago-vitae.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def srtclock(sec, web=False):
 h=int(sec//3600);m=int(sec//60)%60;s=int(sec)%60;ms=int(round((sec-int(sec))*1000))
 return f'{h:02d}:{m:02d}:{s:02d}.{ms:03d}'
lines=['WEBVTT','','NOTE Original editorial English translations. Latin passages quoted from Seneca Epistulae morales 26.','']
for i,c in enumerate(cues,1):
 text=c['text']
 if c['language']=='la' and c['translation']:text+='\n'+c['translation']
 lines.extend([str(i),f'{srtclock(c["start"])} --> {srtclock(c["end"])}',text,''])
(O/'imago-vitae.vtt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Wrote:')
for p in sorted(O.glob('imago-vitae-*')):print(p.name,p.stat().st_size)
print('First 3 cues:',[(c['start'],c['end']) for c in cues[:3]],'last cue',cues[-1]['start'],cues[-1]['end'])