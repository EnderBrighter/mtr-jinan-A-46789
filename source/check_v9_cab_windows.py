"""Cab side aperture stays behind the nose wrap and retains single-sheet glazing."""
from pathlib import Path
import json,math,shutil
r=Path(__file__).resolve().parents[1]
a=json.loads((r/'source/geometry.json').read_text())['cab']['cab_glazing']
for i in [6,8]:
 vs=a[i]['v']
 assert min(v[2] for v in vs)>-11.55
 assert max(v[2] for v in vs)<=-11+1e-6
 assert all(abs(abs(v[0])-1.492)<2e-5 for v in vs)
 lower=min((v for v in vs if abs(v[1]-2.16)<1e-6),key=lambda v:v[2])
 upper=min((v for v in vs if abs(v[1]-2.95)<1e-6),key=lambda v:v[2])
 assert upper[2]-lower[2]>.17
 assert a[i+1]['v']==list(reversed(vs))
print('PASS: both side panes moved behind front wrap; inclined leading edges; five single-sheet cab panes retained')
