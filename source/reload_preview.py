"""Load the complete current pack into the running local MTR creator preview."""
from pathlib import Path
import json,zipfile,requests
r=Path(__file__).resolve().parents[1];p=r/'dist/jinan_line4_v6_runtime.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for f in [r/'pack.mcmeta',r/'pack.png']+list((r/'assets').rglob('*')):
  if f.is_file():z.write(f,f.relative_to(r).as_posix())
with p.open('rb') as f:res=requests.post('http://localhost:8888/mtr/api/creator/upload/zip',files={'file':(p.name,f,'application/zip')},timeout=30)
res.raise_for_status();res.encoding='utf-8';d=res.json()
d['minecraftModelResources']=[];d['minecraftTextureResources']=[]
res=requests.post('http://localhost:8888/mtr/api/creator/operation/update?id=',data=json.dumps(d,ensure_ascii=False).encode(),headers={'Content-Type':'text/plain;charset=UTF-8'},timeout=30);res.raise_for_status()
res=requests.get('http://localhost:8888/mtr/api/creator/operation/refresh',timeout=10);res.encoding='utf-8';d=res.json()
for v in d['vehicles']:
 if v['id'] in ['jinan_line4_tc','jinan_line4_tc_reverse']:assert any(m['modelResource'].endswith('headsign.bbmodel') for m in v['models'])
print('PASS: complete runtime preview updated; both cab registrations include native headsigns')
