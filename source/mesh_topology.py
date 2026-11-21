"""Deterministic ear clipping: no triangle fans across concave seat/cove caps."""
import math

def triangles(vertices):
 n=len(vertices)
 if n<3:return []
 normal=[0.,0.,0.]
 for i,p in enumerate(vertices):
  q=vertices[(i+1)%n]
  normal[0]+=(p[1]-q[1])*(p[2]+q[2]);normal[1]+=(p[2]-q[2])*(p[0]+q[0]);normal[2]+=(p[0]-q[0])*(p[1]+q[1])
 axis=max(range(3),key=lambda k:abs(normal[k]))
 if abs(normal[axis])<1e-12:return []
 keep=[k for k in range(3) if k!=axis];p=[(v[keep[0]],v[keep[1]]) for v in vertices]
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 area=sum(p[i][0]*p[(i+1)%n][1]-p[(i+1)%n][0]*p[i][1] for i in range(n));sgn=1 if area>0 else -1
 ids=list(range(n));result=[]
 # Remove only redundant projected collinear points, preserving polygon outline.
 changed=True
 while changed and len(ids)>3:
  changed=False
  for j,i in enumerate(ids):
   a,b=ids[j-1],ids[(j+1)%len(ids)]
   if abs(cross(p[a],p[i],p[b]))<1e-12:
    ids.pop(j);changed=True;break
 while len(ids)>3:
  found=False
  for j,b in enumerate(ids):
   a,c=ids[j-1],ids[(j+1)%len(ids)]
   if sgn*cross(p[a],p[b],p[c])<1e-12:continue
   def inside(k):return all(sgn*cross(p[u],p[v],p[k])>=-1e-12 for u,v in [(a,b),(b,c),(c,a)])
   if any(inside(k) for k in ids if k not in [a,b,c]):continue
   result.append((a,b,c));ids.pop(j);found=True;break
  if not found:raise ValueError('Polygon is self-intersecting or degenerate: '+str(vertices))
 if len(ids)==3:result.append(tuple(ids))
 return result
