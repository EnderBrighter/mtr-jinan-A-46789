from pathlib import Path
import json,zipfile,numpy as np
r=Path('.')
def read_triangles(path):
 v=[];tri=[];labels=[];g=''
 for row in path.read_text().splitlines():
  if row.startswith('g '):g=row[2:]
  elif row.startswith('v '):v.append([float(n) for n in row.split()[1:]])
  elif row.startswith('f ') and g in ['interior','interior_soft_white','lcd_mounts','lcd_mounts_soft_white']:
   tri.append([v[int(x.split('/')[0])-1] for x in row.split()[1:]]);labels.append(g)
 return np.array(tri),labels
checks=0
for car in ['cab','middle','motor']:
 t,labels=read_triangles(r/f'assets/mtr/jinan_line4/models/{car}.obj');a=t[:,0];e1=t[:,1]-a;e2=t[:,2]-a
 for side in [-1,1]:
  d=np.array([side,0.,0.]);h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-10;inv=np.zeros(len(det));inv[ok]=1/det[ok]
  for z in [-10,-5,0,5,10]:
   for end in [-1,1]:
    for fraction in [.05,.2,.4,.6,.8,.95]:
     zz=z+end*(1.025+.175*fraction);y=3.46+.055*(1-fraction);eye=np.array([0.,y,zz])
     s=eye-a;u=np.einsum('ij,ij->i',s,h)*inv;q=np.cross(s,e1);v=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
     ids=np.flatnonzero(ok&(u>=-1e-7)&(v>=-1e-7)&(u+v<=1+1e-7)&(dist>1e-6)&(dist<1.5))
     assert len(ids),(car,side,z,end,fraction,'gap')
     i=min(ids,key=lambda i:dist[i]);assert labels[i]=='lcd_mounts_soft_white',(car,side,z,end,fraction,labels[i])
     # Correctly wound opaque face must be visible from the aisle.
     assert np.dot(np.cross(e1[i],e2[i]),d)<0,(car,side,z,end,'culled')
     checks+=1
old=zipfile.ZipFile(r/'dist/jinan_lines_4_6_7_8_9_v16.zip')
for line in [4,6,7,8,9]:
 base=f'assets/mtr/jinan_line{line}'
 assert (r/base/'textures/atlas.png').read_bytes()==old.read(base+'/textures/atlas.png')
 assert (r/base/'scripts/lcd.js').read_bytes()==old.read(base+'/scripts/lcd.js')
 def door_shape(b):return [{k:e.get(k) for k in ['name','from','to','inflate','origin','uv_offset','shade']} for e in b['elements']]
 assert door_shape(json.loads((r/base/'models/doors.bbmodel').read_text()))==door_shape(json.loads(old.read(base+'/models/doors.bbmodel')))
for name in ['jinan_lines_4_6_7_8_9_v17.zip','jinan_line4_no_logo_v17.zip']:
 with zipfile.ZipFile(r/'dist'/name) as z:
  assert z.testzip() is None
  for n in z.namelist():
   if n.startswith('assets/mtr/jinan_line'):assert z.read(n)==(r/n).read_bytes()
report={'version':17,'gameVerified':False,'transitionJoinMetres':.175,'actualObjOpaqueJoinRays':checks,'texturesLcdScriptsAndDoorShapesUnchanged':True,'zipIntegrity':'PASS'}
(r/'preview/v17_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))
