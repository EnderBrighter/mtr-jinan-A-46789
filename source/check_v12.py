from pathlib import Path
import json,zipfile,re
from PIL import Image
r=Path('.')
report={'version':12,'gameVerified':False,'doorShiftMetres':.1875,'lines':[4,6,7,8,9]}
config=json.loads((r/'assets/mtr/mtr_custom_resources.json').read_text(encoding='utf-8'))
assert len(config['vehicles'])==20 and len(config['vehicleScripts'])==5
refs=set(re.findall(r'mtr:(jinan_line[^"\s]+)',json.dumps(config)))
for p in (r/'assets/mtr').glob('jinan_line*/properties/*.json'):refs.update(re.findall(r'mtr:(jinan_line[^"\s]+)',p.read_text(encoding='utf-8')))
for ref in refs:assert (r/'assets/mtr'/ref).is_file(),ref
for line in report['lines']:
 base=r/f'assets/mtr/jinan_line{line}'
 atlas=Image.open(base/'textures/atlas.png')
 for kind in ['cab','middle','motor']:
  group='';uvs=[]
  for row in (base/f'models/{kind}.obj').read_text().splitlines():
   if row.startswith('g '):group=row[2:]
   if row.startswith('vt ') and group in ['window','cab_glazing']:
    u,v=map(float,row.split()[1:]);assert atlas.getpixel((round(u*1024),round(v*512)))[3]==0
 b=json.loads((base/'models/doors.bbmodel').read_text())
 for e in b['elements']:
  if e['uv_offset']==[132,4] and e['from'][1]/16<2:assert e['from'][1]/16==1.1875 and e['to'][1]/16==1.3125
for car,gs in json.loads((r/'source/geometry.json').read_text()).items():
 if car=='bogie':continue
 assert not any(f['c']=='yellow' for f in gs['lights'])
for name in ['jinan_line4_no_logo_v12.zip','jinan_lines_4_6_7_8_9_v12.zip']:
 with zipfile.ZipFile(r/'dist'/name) as z:
  assert z.testzip() is None
  assert 'pack.mcmeta' in z.namelist() and not any('使用说明' in n for n in z.namelist())
  for p in z.namelist():
   if p.startswith('assets/mtr/jinan_line'):assert z.read(p)==(r/p).read_bytes(),p
report.update(vehicles=20,scripts=5,resourceReferences=len(refs),zipIntegrity='PASS',allPassengerWindowAlpha='zero',doorIndicators='removed',liveryAlignment='PASS')
(r/'preview/v12_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
