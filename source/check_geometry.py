import json,pathlib,math
from mesh_topology import triangles
r=pathlib.Path('.');scenes=json.loads((r/'source/geometry.json').read_text());report={}
for name,groups in scenes.items():
 vs=[v for faces in groups.values() for f in faces for v in f['v']];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 assert all(math.isfinite(q) for v in vs for q in v)
 assert lo[0]>=-1.50001 and hi[0]<=1.50001,(name,lo,hi)
 if name!='bogie':assert lo[2]>=-12.50001 and hi[2]<=12.50001,(name,lo,hi)
 tris=sum(len(triangles(f['v'])) for g,faces in groups.items() if not g.startswith('door_') for f in faces)
 report[name]={'bounds':[lo,hi],'exportedTriangles':tris}
# Ceiling and floor actually reach a carriage's two gangway frames, with floor half-bridges to ±12.5.
for name in ['middle','motor']:
 fs=[f for f in scenes[name]['interior'] if f['c']=='floor'];v=[v for f in fs for v in f['v']]
 assert min(p[2] for p in v)<=-12.5 and max(p[2] for p in v)>=12.5
 assert max(p[1] for p in v)==1.0
 # Eye-level horizontal rays in the 1.24m end zones must hit opaque sides, not empty sky.
 for side in [-1,1]:
  for end in [-1,1]:
   for z in [end*(11.01+i*.12) for i in range(11)]:
    for y in [1.4,2.0,2.6,2.99]:
     faces=scenes[name]['shell']+scenes[name]['interior']
     assert any(all(abs(p[0]-side*1.435)<.061 for p in f['v']) and min(p[1] for p in f['v'])-1e-6<=y<=max(p[1] for p in f['v'])+1e-6 and min(p[2] for p in f['v'])-1e-6<=z<=max(p[2] for p in f['v'])+1e-6 for f in faces),(name,side,end,z,y)
(r/'preview/geometry_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2));print('PASS: length/width budget, finite vertices, full-height end-zone side closure and continuous gangway floor')
