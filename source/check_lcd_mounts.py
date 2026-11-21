"""LCD visibility from a passenger's eye, actual opaque meshes, across both sides."""
from pathlib import Path
import json,numpy as np
from mesh_topology import triangles
r=Path(__file__).resolve().parents[1];scenes=json.loads((r/'source/geometry.json').read_text())
checks=0
for car in ['cab','middle','motor']:
 groups=scenes[car];tri=[];labels=[]
 for g,faces in groups.items():
  if g.startswith('door_') or g in ['window','cab_glazing']:continue
  for f in faces:
   for t in triangles(f['v']):tri.append([f['v'][k] for k in t]);labels.append((g,f['c']))
 t=np.array(tri);a=t[:,0];e1=t[:,1]-a;e2=t[:,2]-a
 for side in [-1,1]:
  for z in [-10,-5,0,5,10]:
   eye=np.array([0,2.40,z])
   for u,v in [(0,0),(-.76,-.11),(.76,-.11),(-.76,.11),(.76,.11)]:
    target=np.array([side*(1.245-.48*v-.014),3.325+v,z+u]);d=target-eye
    h=np.cross(d,e2);det=np.einsum('ij,ij->i',e1,h);ok=abs(det)>1e-10;inv=np.zeros(len(det));inv[ok]=1/det[ok]
    s=eye-a;uu=np.einsum('ij,ij->i',s,h)*inv;q=np.cross(s,e1);vv=q@d*inv;dist=np.einsum('ij,ij->i',e2,q)*inv
    ids=np.flatnonzero(ok&(uu>=-1e-7)&(vv>=-1e-7)&(uu+vv<=1+1e-7)&(dist>1e-6)&(dist<=1.0001))
    assert len(ids),(car,side,z,u,v,'no screen')
    i=min(ids,key=lambda k:dist[k]);assert labels[i]==('lcd_mounts','screen'),(car,side,z,u,v,labels[i],dist[i])
    checks+=1
print(f'PASS: {checks} passenger-eye rays reach blank LCD inserts without rail/ceiling obstruction')

# The former housing consisted of two open sheets: from below/along the aisle
# their unclosed sides exposed the sky. Every white housing must now be closed.
from collections import Counter
for car in ['cab','middle','motor']:
 edges=Counter()
 for f in scenes[car]['lcd_mounts']:
  if f['c']!='white':continue
  vs=[tuple(round(q,6) for q in p) for p in f['v']]
  for a,b in zip(vs,vs[1:]+vs[:1]):edges[tuple(sorted((a,b)))]+=1
 assert edges and all(n==2 for n in edges.values()),(car,'unclosed LCD housing',[e for e,n in edges.items() if n!=2][:4])
print('PASS: all 30 LCD housings have closed top, bottom, rear and both end caps')

