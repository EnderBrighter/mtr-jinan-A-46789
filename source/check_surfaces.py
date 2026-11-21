"""Regression for missing front surfaces and concave seat-cap overlap."""
import json,pathlib,numpy as np
from mesh_topology import triangles
R=pathlib.Path(__file__).resolve().parents[1]
data=json.loads((R/'source/geometry.json').read_text())
checked=0
for name,groups in data.items():
 for g,faces in groups.items():
  for f in faces:
   p=np.array(f['v']);n=sum((np.cross(p[i],p[(i+1)%len(p)]) for i in range(len(p))),np.zeros(3));axis=np.argmax(abs(n));ids=[i for i in range(3) if i!=axis]
   pp=p[:,ids];area=abs(sum(np.cross(pp[i],pp[(i+1)%len(pp)]) for i in range(len(pp))))/2
   ts=triangles(f['v']);ta=sum(abs(np.cross(pp[b]-pp[a],pp[c]-pp[a]))/2 for a,b,c in ts)
   assert abs(area-ta)<1e-7,(name,g,f['c'],area,ta)
   checked+=1
# Read the delivered OBJ, not the generating function or Blender's repaired normals.
vs=[];front=[]
for line in (R/'assets/mtr/jinan_line4/models/cab.obj').read_text().splitlines():
 if line.startswith('v '):vs.append([float(x) for x in line.split()[1:]])
 elif line.startswith('f '):
  t=np.array([vs[int(i.split('/')[0])-1] for i in line.split()[1:]])
  if t[:,2].max()<-11.0:front.append(t)
front=np.array(front)
count=0
for y in [1.2,1.5,1.75,1.85,3.4]:
 for x in [-.9,-.6,-.3,0,.3,.6,.9]:
  hits=[]
  for t in front:
   a,b,c=t;u=b[:2]-a[:2];v=c[:2]-a[:2];det=u[0]*v[1]-u[1]*v[0]
   if abs(det)<1e-12:continue
   p=np.array([x,y])-a[:2];s=(p[0]*v[1]-p[1]*v[0])/det;r=(u[0]*p[1]-u[1]*p[0])/det
   if s>=-1e-8 and r>=-1e-8 and s+r<=1+1e-8:hits.append((a[2]+s*(b[2]-a[2])+r*(c[2]-a[2]),np.cross(b-a,c-a)[2]))
  assert hits,('front missing',x,y)
  assert min(hits,key=lambda h:h[0])[1]<0,('front culled',x,y)
  count+=1
print(f'PASS: {checked} polygon projected areas; {count} exterior rays hit outward-facing nose/mask in actual OBJ')

# Each cab window is exactly one planar sheet with one outward and one inward face.
glazing=data['cab']['cab_glazing'];assert len(glazing)==10
for i in range(0,10,2):
 p=np.array(glazing[i]['v']);q=np.array(glazing[i+1]['v'])
 assert np.allclose(p,q[::-1])
 n=np.cross(p[1]-p[0],p[2]-p[0]);assert abs(np.dot(n,p[3]-p[0]))<1e-10
print('PASS: five planar cab panes, opposite culled windings, no tessellated multi-layer glass')
