"""Regression for the visible door header/lamp planes that previously z-fought."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1];data=json.loads((r/'source/geometry.json').read_text())
for car in ['cab','middle','motor']:
 for side in [-1,1]:
  for z in [-10,-5,0,5,10]:
   def outer(group,color,dz):
    faces=[f for f in data[car][group] if f['c']==color and all(v[0]*side>1.45 for v in f['v']) and min(v[1] for v in f['v'])<=3.015<=max(v[1] for v in f['v']) and min(v[2] for v in f['v'])<=z+dz<=max(v[2] for v in f['v']) and max(v[0] for v in f['v'])-min(v[0] for v in f['v'])<1e-8]
    return max(v[0]*side for f in faces for v in f['v'])
   strip=outer('shell','silver',.12);bezel=outer('shell','rubber',.06);lens=outer('lights','yellow',0)
   assert abs(strip-1.496)<1e-8 and abs(bezel-1.498)<1e-8 and abs(lens-1.5)<1e-8
   assert bezel-strip>=.00199 and lens-bezel>=.00199
   assert not any(f['c']=='white' and all(abs(v[0]*side-1.5)<1e-8 for v in f['v']) and min(v[1] for v in f['v'])<3.02 and max(v[1] for v in f['v'])>3.01 for f in data[car]['interior'])
print('PASS: 30 door headers: silver/bezel/lens planes at 1.496/1.498/1.500 m, 2 mm separation; no white cap at exterior plane')
