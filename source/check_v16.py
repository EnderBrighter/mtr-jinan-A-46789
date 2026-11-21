from pathlib import Path
import json,zipfile
import numpy as np
from PIL import Image
r=Path('.')
keys=['name','from','to','inflate','origin','rotation','uv_offset']
def signatures(b):
 result=[]
 for e in b['elements']:
  d={k:e.get(k) for k in keys};d['name']=d['name'].removesuffix('_soft_white');result.append(json.dumps(d,sort_keys=True))
 return sorted(result)
old=zipfile.ZipFile(r/'source/archive/before_v15_unified_panels.zip')
for line in [4,6,7,8,9]:
 base=r/f'assets/mtr/jinan_line{line}';atlas=Image.open(base/'textures/atlas.png')
 assert atlas.getpixel((352,32))==(237,240,233,255)
 b=json.loads((base/'models/doors.bbmodel').read_text());prev=json.loads(old.read(f'assets/mtr/jinan_line{line}/models/doors.bbmodel'))
 assert signatures(b)==signatures(prev),('door geometry changed',line)
 for rev in ['', '_reverse']:
  doors=json.loads((base/f'properties/doors{rev}.json').read_text())
  for p in doors['parts']:
   if p['names'][0].endswith('_soft_white'):assert p['renderStage']=='INTERIOR'
 for car in ['cab','middle','motor']:
  props=json.loads((base/f'properties/{car}.json').read_text());mapping={n:p for p in props['parts'] for n in p['names']}
  group='';v=[];uv=[];count=0
  for row in (base/f'models/{car}.obj').read_text().splitlines():
   if row.startswith('g '):group=row[2:];assert group in mapping,(line,car,group)
   elif row.startswith('v '):v.append([float(x) for x in row.split()[1:]])
   elif row.startswith('vt '):uv.append([float(x) for x in row.split()[1:]])
   elif row.startswith('f ') and group.endswith('_soft_white'):
    assert mapping[group]['renderStage']=='INTERIOR',('nonopaque white',group)
    for index in row.split()[1:]:
     u,w=uv[int(index.split('/')[1])-1];assert atlas.getpixel((round(u*1024),round(w*512)))[3]==255
    count+=1
  assert count>0
# Check the delivered cabin inner lining from the inside, below and above windshield apertures.
from mesh_topology import triangles
s=json.loads((r/'source/geometry.json').read_text())['cab'];ts=[]
for f in s['interior']:
 for ids in triangles(f['v']):
  t=np.array([f['v'][i] for i in ids])
  if t[:,2].max()<-11.3:ts.append(t)
checks=0
for y in [1.2,1.5,1.75,3.4]:
 for x in [-.9,-.6,-.3,0,.3,.6,.9]:
  hits=[]
  for t in ts:
   a,b,c=t;u=b[:2]-a[:2];v=c[:2]-a[:2];det=u[0]*v[1]-u[1]*v[0]
   if abs(det)<1e-12:continue
   p=np.array([x,y])-a[:2];alpha=(p[0]*v[1]-p[1]*v[0])/det;beta=(u[0]*p[1]-u[1]*p[0])/det
   if alpha>=-1e-8 and beta>=-1e-8 and alpha+beta<=1+1e-8:hits.append((a[2]+alpha*(b[2]-a[2])+beta*(c[2]-a[2]),np.cross(b-a,c-a)[2]))
  assert hits,(x,y,'missing inner lining')
  assert max(hits,key=lambda h:h[0])[1]>0,(x,y,'inner lining culled')
  checks+=1
for name,count in [('jinan_lines_4_6_7_8_9_v16.zip',20),('jinan_line4_no_logo_v16.zip',4)]:
 with zipfile.ZipFile(r/'dist'/name) as z:
  assert z.testzip() is None
  assert len(json.loads(z.read('assets/mtr/mtr_custom_resources.json'))['vehicles'])==count
  for n in z.namelist():
   if n.startswith('assets/mtr/jinan_line'):assert z.read(n)==(r/n).read_bytes()
report={'version':16,'gameVerified':False,'doorGeometryUnchanged':True,'whitePanelColor':'#EDF0E9','fixedAndMovingWhitePanelsUseSameOpaqueStage':'INTERIOR / CUTOUT_BRIGHT','allWhitePanelAlpha':255,'cabInnerLiningRays':checks,'zipIntegrity':'PASS'}
(r/'preview/v16_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
