import json,pathlib,math
from PIL import Image
r=pathlib.Path('assets/mtr/jinan_line4');b=json.loads((r/'models/doors.bbmodel').read_text());out={g['name']:g['children'] for g in b['outliner']};els={e['uuid']:e for e in b['elements']}
def rendered_corners(e):
 inflate=e.get('inflate',0)
 return [[q-inflate for q in e['from']],[q+inflate for q in e['to']]]
# Native BBMODEL: draw coordinates (-x,-y,z), interaction bounds (x,y,z).
# Both use the same Z axis. Test actual panel aperture and correspondence with source OBJ geometry.
scene=json.loads(pathlib.Path('source/geometry.json').read_text())['cab']
for g,ids in out.items():
 src=[v for f in scene[g] for v in f['v']];bb=[v for uid in ids for v in rendered_corners(els[uid])]
 for k,sign in enumerate([-1,1,-1]):
  native=sorted([min(v[k] for v in bb)/16,max(v[k] for v in bb)/16]);expected=sorted([min(v[k] for v in src)*sign,max(v[k] for v in src)*sign]);assert all(abs(a-c)<1e-6 for a,c in zip(native,expected)),g
for flip in [False,True]:
 p=json.loads((r/'properties'/('doors_reverse.json' if flip else 'doors.json')).read_text())
 for side in ['l','r']:
  for i in range(5):
   pair=[]
   for leaf in ['a','b']:
    g=f'door_{side}_{i}_{leaf}';vs=[v for uid in out[g] for v in rendered_corners(els[uid])];lo=min(v[2] for v in vs)/16;hi=max(v[2] for v in vs)/16
    if flip:lo,hi=-hi,-lo
    part=next(t for t in p['parts'] if t['names']==[g]);dz=part['doorZMultiplier']/16*(-1 if flip else 1);pair.append((lo,hi,dz))
   for step in range(101):
    t=step/100;intervals=sorted([(lo+dz*t,hi+dz*t) for lo,hi,dz in pair]);assert intervals[0][1]<=intervals[1][0]+1e-6,(side,i,step)
   intervals=sorted([(lo+dz,hi+dz) for lo,hi,dz in pair]);assert abs(intervals[1][0]-intervals[0][1]-1.5)<.02
# Match each opaque leaf to its native doorway using MTR's closest-interval metric.
interaction=json.loads((r/'models/interaction.bbmodel').read_text())
ways=[e for e in interaction['elements'] if e['name'].startswith('way_')]
def axis_distance(a,b,c,d):
 return max(0,c-b,a-d)
for g,ids in out.items():
 if g.endswith('_glass'):continue
 vs=[v for uid in ids for v in [els[uid]['from'],els[uid]['to']]]
 lo=[min(v[k] for v in vs)/16 for k in range(3)];hi=[max(v[k] for v in vs)/16 for k in range(3)]
 def distance(w):
  a=[v/16 for v in w['from']];b=[v/16 for v in w['to']];a[1]+=1;b[1]+=1
  return sum(axis_distance(lo[k],hi[k],a[k],b[k]) for k in range(3))
 w=min(ways,key=distance);native_side=1 if lo[0]>0 else -1
 assert w['name'].split('_')[1]==str(native_side),(g,w['name'])
 assert abs((w['from'][2]+w['to'][2])/32-(lo[2]+hi[2])/2)<1,(g,w['name'])
for v in json.loads(pathlib.Path('assets/mtr/mtr_custom_resources.json').read_text(encoding='utf-8'))['vehicles']:
 for m in v['models']:
  p=json.loads((pathlib.Path('assets')/m['modelPropertiesResource'].replace(':','/')).read_text(encoding='utf-8'))
  displays=[x for x in p['parts'] if x.get('type')=='DISPLAY']
  if displays:
   assert m['modelResource'].endswith('/headsign.bbmodel')
   assert {x['displayType'] for x in displays}=={'DESTINATION','ROUTE_NUMBER'}
   assert all('济南地铁' not in x.get('displayDefaultText','') for x in displays)
  if m['modelResource'].endswith('.obj'):assert not any('doorZMultiplier' in t for t in p['parts'])
assert Image.open(r/'textures/atlas.png').getpixel((224,32))[3]<150
atlas=Image.open(r/'textures/atlas.png')
# MTR's actual Blockbench importer reads uv_offset and integer box sizes, not
# faces[].uv. Verify the complete native cube UV net lies in clear alpha pixels.
panes=[e for e in b['elements'] if e['name'].endswith('_glass')]
assert len(panes)==20
for e in panes:
 size=[round(hi-lo) for lo,hi in zip(e['from'],e['to'])];x,y=e['uv_offset']
 net=atlas.crop((x,y,x+max(1,2*size[0]+2*size[2]),y+max(1,size[1]+size[2])))
 assert net.getchannel('A').getextrema()==(0,0),e['name']
for f in scene['cab_glazing']+[f for f in scene['window'] if f['c']=='clear_glass']:
 assert f['c']=='clear_glass'
 for u,v in f['uv']:assert atlas.getpixel((int(u*1024),int(v*512)))[3]==0
seals=[e for e in b['elements'] if e.get('inflate',0)>0]
assert len(seals)==40
for e in seals:
 assert abs(e['to'][0]-e['from'][0])<1e-8 and abs(e['to'][2]-e['from'][2])<1e-8
 assert 0<2*e['inflate']/16<.008
 assert all(abs((hi-lo)-round(hi-lo))<1e-8 for lo,hi in zip(e['from'],e['to']))
print(f'PASS: {len(out)} native door parts; matching draw/bounds, 101 opening samples each direction, 1.5 m aperture; 20 clear native UV nets, clear cab/partition panes; 40 fine seals use supported native inflate')
