"""Validate the seat placement, full-height door seams and native headsign options."""
from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
data=json.loads((r/'source/geometry.json').read_text())
for car in ['cab','middle','motor']:
 faces=data[car]['seats']
 for side in [-1,1]:
  for z in [-7.5,-2.5,2.5,7.5]:
   yellow=[f for f in faces if f['c']=='yellow' and sum(p[0] for p in f['v'])*side>0 and abs(sum(p[2] for p in f['v'])/len(f['v'])-z)<1.31]
   assert len(yellow)==52,(car,side,z,'one seat/back pair',len(yellow))
   expected=z+(1.075 if side<0 else -1.075)
   assert all(abs(sum(p[2] for p in f['v'])/len(f['v'])-expected)<.22 for f in yellow),(car,side,z)
bb=json.loads((r/'assets/mtr/jinan_line4/models/doors.bbmodel').read_text())
seals=[e for e in bb['elements'] if e.get('inflate',0)>0]
assert len(seals)==40
for e in seals:
 assert (e['from'][1]-e['inflate'])/16>1.0
 assert (e['to'][1]+e['inflate'])/16>2.8
for name in ['headsign','headsign_reverse']:
 a=json.loads((r/f'assets/mtr/jinan_line4/properties/{name}.json').read_text())
 dest=next(p for p in a['parts'] if p['displayType']=='DESTINATION')
 route=next(p for p in a['parts'] if p['displayType']=='ROUTE_NUMBER')
 assert 'SCROLL_NORMAL' in dest['displayOptions'] and 'CYCLE_LANGUAGES' in dest['displayOptions']
 assert route['displayOptions']==['SINGLE_LINE']
print('PASS: every bench has one yellow seat, opposite ends on opposite sides; 40 full-height seals clear the sill; both destination displays scroll')
