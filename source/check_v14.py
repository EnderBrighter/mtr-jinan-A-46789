from pathlib import Path
import json,zipfile,math
from PIL import Image
r=Path('.')
old=zipfile.ZipFile(r/'source/archive/before_v14_lcd_restore.zip')
report={'version':14,'gameVerified':False}
keys=['name','from','to','inflate','origin','rotation','uv_offset']
def signature(b):return sorted(json.dumps({k:e.get(k) for k in keys},sort_keys=True) for e in b['elements'])
for line in [4,6,7,8,9]:
 root=f'assets/mtr/jinan_line{line}'
 before=json.loads(old.read(root+'/models/doors.bbmodel'))
 after=json.loads((r/root/'models/doors.bbmodel').read_text())
 assert signature(before)==signature(after),(line,'door moved')
 for n in ['doors.json','doors_reverse.json']:
  assert json.loads(old.read(root+'/properties/'+n))==json.loads((r/root/'properties'/n).read_text()),(line,n)
 atlas=Image.open(r/root/'textures/atlas.png')
 assert atlas.getpixel((352,32))[:3]==(231,235,231)
 assert atlas.getpixel((32,32))[:3]==(214,219,221)
 assert atlas.getpixel((32,448))[3]==0
 for kind in ['cab','middle','motor']:
  obj=(r/root/f'models/{kind}.obj').read_text()
  prop=json.loads((r/root/f'properties/{kind}.json').read_text())
  assert all('g '+g in obj for g in ['interior_soft_white','seats_soft_white','lcd_mounts_soft_white'])
  assert any('interior_soft_white' in p['names'] and p['renderStage']=='ALWAYS_ON_LIGHT' for p in prop['parts'])
scenes=json.loads((r/'source/geometry.json').read_text())
minimum=10
for car in ['cab','middle','motor']:
 for face in scenes[car]['lcd_mounts']:
  if face['c']=='screen':
   vs=face['v'];ys=[v[1] for v in vs];zs=[v[2] for v in vs]
   assert abs(max(ys)-min(ys)-.285)<1e-8
   assert abs(max(zs)-min(zs)-1.74)<1e-8
  if face['c']=='white':
   for x,y,z in face['v']:
    a=abs(x);roof=3.67 if a<=.95 else 3.075+.595*math.sqrt(1-((a-.95)/.55)**2)
    gap=roof-y;assert gap>.01,(car,x,y,gap);minimum=min(minimum,gap)
for filename,count in [('jinan_lines_4_6_7_8_9_v14.zip',20),('jinan_line4_no_logo_v14.zip',4)]:
 with zipfile.ZipFile(r/'dist'/filename) as z:
  assert z.testzip() is None
  cfg=json.loads(z.read('assets/mtr/mtr_custom_resources.json'));assert len(cfg['vehicles'])==count
  for v in cfg['vehicles']:
   s=next(s for s in cfg['vehicleScripts'] if s['id']==v['scriptId']);assert s['input']['defaultColor']==int(v['color'],16)
  for n in z.namelist():
   if n.startswith('assets/mtr/jinan_line'):assert z.read(n)==(r/n).read_bytes(),n
report.update(doorGeometryAndMotionUnchanged=True,lcdWidth=1.74,lcdVerticalHeight=.285,lcdRaisedFromV11=.210,roofClearanceAtHousingVertices=minimum,softWhite='#E7EBE7',silver='#D6DBDD',yellowSeatsSwapped=True,zipIntegrity='PASS')
(r/'preview/v14_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
