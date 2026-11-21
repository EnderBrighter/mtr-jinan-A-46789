"""Actual translated BB cuboid volumes versus fixed mesh triangles, whole door sweep."""
import json,pathlib,numpy as np
from mesh_topology import triangles
R=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((R/'source/geometry.json').read_text())

def clipped_area(tri,lo,hi):
 p=[v.copy() for v in tri]
 for k in range(3):
  for edge,sign in [(lo[k],1),(hi[k],-1)]:
   if not p:return 0
   out=[]
   for a,b in zip(p,p[1:]+p[:1]):
    da=(a[k]-edge)*sign;db=(b[k]-edge)*sign
    if da>=0:out.append(a)
    if (da>=0)!=(db>=0):out.append(a+(b-a)*da/(da-db))
   p=out
 if len(p)<3:return 0
 return sum(np.linalg.norm(np.cross(p[i]-p[0],p[i+1]-p[0]))/2 for i in range(1,len(p)-1))

bb=json.loads((R/'assets/mtr/jinan_line4/models/doors.bbmodel').read_text())
motion={p['names'][0]:-p['doorZMultiplier']/16 for p in json.loads((R/'assets/mtr/jinan_line4/properties/doors.json').read_text())['parts']}
collisions=[]
for name,groups in data.items():
 if name=='bogie':continue
 fixed=[];labels=[]
 for g,faces in groups.items():
  if g.startswith('door_'):continue
  for fi,f in enumerate(faces):
   for t in triangles(f['v']):fixed.append([f['v'][j] for j in t]);labels.append((g,fi,f['c']))
 fixed=np.array(fixed);flo=fixed.min(1);fhi=fixed.max(1)
 for e in bb['elements']:
  inflate=e.get('inflate',0)
  v=np.array([np.array(e['from'])-inflate,np.array(e['to'])+inflate])/16*np.array([-1,1,-1]);lo=v.min(0);hi=v.max(0)
  dz=motion[e['name']]
  lo[2]+=min(0,dz);hi[2]+=max(0,dz)
  for k in range(3):
   if hi[k]-lo[k]<1e-7:lo[k]-=1e-5;hi[k]+=1e-5
   else:lo[k]+=1e-5;hi[k]-=1e-5
  cand=np.flatnonzero(((flo<hi)&(fhi>lo)).all(1))
  for i in cand:
   if clipped_area(fixed[i],lo,hi)>1e-9:
    collisions.append((name,e['name'],labels[i],fixed[i].tolist()))
(R/'preview/door_sweep_validation.json').write_text(json.dumps({'collisions':collisions,'cuboidsPerCar':len(bb['elements']),'method':'Continuous swept cuboid / triangle clipping; tolerance 0.01 mm'},indent=2))
for c in collisions[:20]:print(c)
assert not collisions, f'{len(collisions)} swept collisions with fixed mesh'
print('PASS: full continuous sweep of every native door cuboid against all fixed triangles, Tc/M/Mp; 0.01 mm tolerance')
