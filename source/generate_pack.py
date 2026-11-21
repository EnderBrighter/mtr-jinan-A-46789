import pathlib,json,math,uuid,base64
from mesh_topology import triangles
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1]; A=ROOT/'assets/mtr/jinan_line4'; M=A/'models'; P=A/'properties'; T=A/'textures'
COLORS={'silver':'#d6dbdd','roof':'#bcc5c9','green':'#b1d93e','glass':'#243c46','black':'#111b22','white':'#edf0e9','floor':'#747f84','steel':'#85979d','seat':'#9dd91d','yellow':'#efc944','light':'#f4ffee','red':'#d52f3f','rubber':'#333a3c','screen':'#151f24'}
im=Image.new('RGBA',(1024,512));dr=ImageDraw.Draw(im)
UV={}
for i,(n,c) in enumerate(COLORS.items()):
 x=i*64;dr.rectangle((x,0,x+63,63),fill=c);UV[n]=((x+32)/1024,32/512)
f='C:/Windows/Fonts/msyh.ttc';font=ImageFont.truetype(f,38);small=ImageFont.truetype(f,22)
for y,txt in [(80,'济南地铁   JINAN METRO'),(145,'4 号线   LINE 4'),(210,'0401'),(275,'请勿倚靠车门'),(340,'第一医科大学  ←  4  →  彭家庄')]:
 dr.rectangle((0,y,1023,y+58),fill=(0,0,0,0) if y==210 else '#14252e');dr.text((12,y+4),txt,font=font if y<270 else small,fill='#dcebd8')
dr.rectangle((3*64,0,4*64-1,63),fill=(61,91,103,66))
# Clear glazing discards its central fragments instead of writing depth before water.
# All passenger glazing uses discarded alpha-zero fragments to avoid water occlusion.
COLORS.update(clear_glass='#3d5b67',seal='#333a3c')
UV['clear_glass']=(32/1024,448/512)
UV['seal']=UV['rubber']
dr.rectangle((0,416,63,479),fill=(61,91,103,0))
# Blank rounded badge patch (emblem removed in v17); all destination text remains native, dynamic MTR DISPLAY text.
dr.rounded_rectangle((220,212,272,264),radius=7,fill='#f3f5ef')
im.save(T/'atlas.png')
Image.new('RGB',(16,16),'#444b4b').save(T/'gangway.png')
class Mesh:
 def __init__(self):self.groups={};self.door_boxes=[]
 def poly(self,g,vs,c='silver',uv=None):
  self.groups.setdefault(g,[]).append({'v':vs,'uv':uv or [UV[c]]*len(vs),'c':c})
 def box(self,g,x,y,z,w,h,l,c='silver'):
  if g.startswith('door_'):
   if c=='glass':c='clear_glass'
   # Keep the livery at body height when the moving leaf is raised.
   if c=='silver' and y<1.2:return
   centre=(-10,-5,0,5,10)[int(g.split('_')[2])]
   scale=1.5/2  # Visual door width is independent of its 2 m platform allocation.
   z=centre+(z-centre)*scale;l*=scale
   y=1.1875+(y-1)*.9375;h*=.9375  # v17: move the complete 1.875 m leaf up 3/16 m, into the two stripe boundaries.
   coords=[x,y,z];sizes=[w,h,l];inflate=0
   if c=='seal':
    # Blockbench rounds cuboid SIZES, but preserves float origins and inflate.
    # Inflate a vertical zero-width/depth line to form a genuinely fine seal,
    # instead of relying on ignored per-face UVs or a 6.25 cm wide carrier.
    inflate=.032 if abs(x)<1.45 else .06
    half=inflate/16;leaf=-1 if g.split('_')[3]=='a' else 1
    coords[2]=centre+leaf*half
    sizes=[2*half,round(h*16)/16+2*half,2*half]
   for axis in ([] if c=='seal' else range(3)):
    if axis==0:
     width=round(sizes[axis]*16)/16;lo=coords[axis]-width/2;hi=coords[axis]+width/2
    else:lo=round((coords[axis]-sizes[axis]/2)*16)/16;hi=round((coords[axis]+sizes[axis]/2)*16)/16
    if axis in [1,2] and sizes[axis]>.001 and lo==hi:
     if axis==2 and '_a' in g:lo-=1/16
     else:hi+=1/16
    coords[axis]=(lo+hi)/2;sizes[axis]=hi-lo
   if c=='green':
    coords[1],sizes[1]=(3.03125,.0625) if y>2 else (1.25,.125)
   elif c=='silver' and y<2:coords[1]=1.625;sizes[1]=.625
   x,y,z=coords;w,h,l=sizes
   # Same opaque panel lighting for the moving inner skins and the fixed lining.
   if c=='white':g+='_soft_white'
   self.door_boxes.append((g,x,y,z,w,h,l,c,inflate))
  v=[(x+a*w/2,y+b*h/2,z+d*l/2) for a,b,d in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  import numpy as np
  emitted=set()
  for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:
   points=[v[i] for i in ids];key=frozenset(points)
   if key in emitted:continue
   aa,bb,cc=[np.array(q) for q in points[:3]]
   if float(np.linalg.norm(np.cross(bb-aa,cc-aa)))<1e-10:continue
   emitted.add(key)
   self.poly(g,points,c)
 def rod(self,g,a,b,r,c='steel',n=8):
  import numpy as np
  a=np.array(a);b=np.array(b);d=b-a;d=d/float(np.linalg.norm(d));u=np.cross(d,[0,0,1])
  if float(np.linalg.norm(u))<.01:u=np.cross(d,[1,0,0])
  u=u/float(np.linalg.norm(u));v=np.cross(d,u)
  rings=[[tuple(p+r*(u*math.cos(t*math.tau/n)+v*math.sin(t*math.tau/n))) for t in range(n)] for p in [a,b]]
  self.poly(g,list(reversed(rings[0])),c);self.poly(g,rings[1],c)
  for i in range(n):j=(i+1)%n;self.poly(g,[rings[0][i],rings[0][j],rings[1][j],rings[1][i]],c)
 def write(self,name):
  import numpy as np
  from collections import defaultdict
  lines=['# Jinan Line 4 detailed geometry | metres | MTR4','mtllib jinan.mtl'];idx=1;ni=1
  export_groups={}
  for group,polys in self.groups.items():
   for face in polys:
    target=group+'_soft_white' if group in ['interior','seats','lcd_mounts'] and face['c']=='white' else group
    export_groups.setdefault(target,[]).append(face)
  for g,faces in export_groups.items():
   if g.startswith('door_'):continue  # Moving parts are exported only as native BBMODEL.
   adjacency=defaultdict(list);normals=[]
   def key(v,c):return (c,)+tuple(round(float(q),5) for q in v)
   for p in faces:
    n=np.array([0.,1.,0.])
    for j in range(1,len(p['v'])-1):
     a,b,c=[np.array(p['v'][k]) for k in [0,j,j+1]];nn=np.cross(b-a,c-a);length=float(np.linalg.norm(nn))
     if length>1e-9:n=nn/length;break
    normals.append(n)
    for v in p['v']:adjacency[key(v,p['c'])].append(n)
   lines+=['g '+g,'usemtl atlas']
   for p,n in zip(faces,normals):
    for v in p['v']:lines.append('v '+' '.join(f'{float(q):.6f}' for q in v))
    for uv in p['uv']:lines.append('vt '+' '.join(f'{q:.6f}' for q in uv))
    smooth=[]
    for v in p['v']:
     ns=[q for q in adjacency[key(v,p['c'])] if float(np.dot(q,n))>.77];q=sum(ns);q=q/float(np.linalg.norm(q));smooth.append(q)
    for tri in triangles(p['v']):
     ids=[]
     for k in tri:
      lines.append('vn '+' '.join(f'{float(q):.6f}' for q in smooth[k]));ids.append(f'{idx+k}/{idx+k}/{ni}');ni+=1
     lines.append('f '+' '.join(ids))
    idx+=len(p['v'])
  (M/(name+'.obj')).write_text('\n'.join(lines)+'\n',encoding='utf-8')
  return self.groups

import model_geometry

def build(cab=False,panto=False):return model_geometry.build(Mesh,cab,panto)
def bogie():return model_geometry.bogie(Mesh)

(M/'jinan.mtl').write_text('newmtl atlas\nKd 1 1 1\nd 1\nmap_Kd mtr:jinan_line4/textures/atlas.png\n')
scenes={}
door_boxes=[]
for name,cab,panto in [('cab',True,False),('middle',False,False),('motor',False,True)]:
 mesh=build(cab,panto);scenes[name]=mesh.write(name)
 if name=='cab':door_boxes=mesh.door_boxes
scenes['bogie']=bogie().write('bogie')
(ROOT/'source/geometry.json').write_text(json.dumps(scenes),encoding='utf-8')
# BBMODEL supplies FLOOR / DOORWAY / DISPLAY: MTR's OBJ implementation handles NORMAL only.
els=[];out=[]
def cube(g,a,b):
 uid=str(uuid.uuid4());els.append({'name':g,'type':'cube','uuid':uid,'from':a,'to':b,'origin':[0,0,0],'faces':{k:{'uv':[0,0,1,1],'texture':0} for k in ['north','south','east','west','up','down']}});out.append({'name':g,'origin':[0,0,0],'uuid':str(uuid.uuid4()),'children':[uid]})
cube('floor',[-22.5,-1,-200],[22.5,0,200])
for side in [-1,1]:
 # MTR scans horizontal doorway surfaces at floor height, extending across the platform gap.
 for i,z in enumerate([-160,-80,0,80,160]):
  xa,xb=sorted([side*21.5,side*28]);cube(f'way_{side}_{i}',[xa,0,z-16],[xb,0,z+16])
cube('display',[-10,29,-196.4],[10,33,-196.4])
(M/'interaction.bbmodel').write_text(json.dumps({'meta':{'format_version':'4.9','model_format':'modded_entity','box_uv':False},'name':'interaction','resolution':{'width':1024,'height':512},'elements':els,'outliner':out,'textures':[{'id':'0','name':'atlas.png','source':'data:image/png;base64,'+base64.b64encode((T/'atlas.png').read_bytes()).decode()}]}))
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
dump(P/'origin.json',{'positionDefinitions':[{'name':'origin','positions':[{}]},{'name':'flipped','positionsFlipped':[{}]}]})
for name in ['cab','middle','motor']:
 parts=[{'names':['shell'],'positionDefinitions':['origin'],'renderStage':'EXTERIOR'},{'names':['interior','seats','lcd_mounts'],'positionDefinitions':['origin'],'renderStage':'INTERIOR'},{'names':['window','cab_glazing'] if name=='cab' else ['window'],'positionDefinitions':['origin'],'renderStage':'INTERIOR_TRANSLUCENT'},{'names':['lights'],'positionDefinitions':['origin'],'renderStage':'LIGHT'}]
 parts.append({'names':['interior_soft_white','seats_soft_white','lcd_mounts_soft_white'],'positionDefinitions':['origin'],'renderStage':'INTERIOR'})
 if name=='cab':
  for g,cond in [('headlights','ON_ROUTE_FORWARDS'),('tail_lights','ON_ROUTE_BACKWARDS'),('depot_lights','AT_DEPOT')]:parts.append({'names':[g],'positionDefinitions':['origin'],'renderStage':'ALWAYS_ON_LIGHT','condition':cond})
 props={'parts':parts,'modelYOffset':0,'gangwayWidth':1.64,'gangwayHeight':2.15,'gangwayYOffset':1,'gangwayZOffset':.26}
 for s in ['Inner','Outer']:
  for face in ['Side','Top','Bottom']:props[f'gangway{s}{face}Resource']='mtr:jinan_line4/textures/gangway.png'
 # OBJ is rotated 180 degrees about X by MTR before rendering/bounds.
 # The leading cab must use the flipped instance; the BBMODEL interaction axes differ.
 if name=='cab':
  for part in props['parts']:part['positionDefinitions']=['flipped']
 dump(P/(name+'.json'),props)
 # mirror every component by using positionDefinitions flipped
 props2=json.loads(json.dumps(props))
 for part in props2['parts']:
  part['positionDefinitions']=['origin'] if name=='cab' else ['flipped']
  if name=='cab' and part.get('condition') in ['ON_ROUTE_FORWARDS','ON_ROUTE_BACKWARDS']:part['condition']='ON_ROUTE_BACKWARDS' if part['condition']=='ON_ROUTE_FORWARDS' else 'ON_ROUTE_FORWARDS'
 dump(P/(name+'_reverse.json'),props2)
dump(P/'bogie.json',{'parts':[{'names':['bogie'],'positionDefinitions':['origin'],'renderStage':'EXTERIOR'}],'modelYOffset':0})
# Dedicated display model: its BB axes match the leading cab's final render axes.
# This differs deliberately from the (-x,y,-z) native door convention above.
sign_elements=[];sign_out=[]
for name,x,y,w,h in model_geometry.headsign_layout():
 w=round(w*16)/16;h=round(h*16)/16
 z=model_geometry.cab_front(x,y)[2]-.027
 tilt=math.degrees(math.atan((model_geometry.cab_front(x,y+.001)[2]-model_geometry.cab_front(x,y-.001)[2])/.002))
 uid=str(uuid.uuid4());origin=[x*16,y*16,z*16]
 sign_elements.append({'name':name,'type':'cube','uuid':uid,'from':[x*16-w*8,y*16-h*8,z*16],'to':[x*16+w*8,y*16+h*8,z*16],'origin':origin,'rotation':[tilt,0,0],'uv_offset':[256,0],'faces':{k:{'uv':[256,0,257,1],'texture':0} for k in ['north','south','east','west','up','down']}})
 sign_out.append({'name':name,'origin':[0,0,0],'uuid':str(uuid.uuid4()),'children':[uid]})
dump(M/'headsign.bbmodel',{'meta':{'format_version':'4.9','model_format':'modded_entity','box_uv':True},'name':'headsign','resolution':{'width':1024,'height':512},'elements':sign_elements,'outliner':sign_out,'textures':[{'id':'0','name':'atlas.png','source':'data:image/png;base64,'+base64.b64encode((T/'atlas.png').read_bytes()).decode()}]})
for rev in [False,True]:
 sign_parts=[{'names':[name],'positionDefinitions':['flipped' if rev else 'origin'],'type':'DISPLAY','displayType':'DESTINATION' if name=='destination' else 'ROUTE_NUMBER','displayDefaultText':'回库' if name=='destination' else '', 'displayColorCjk':'B8EFE6','displayColor':'B8EFE6','displayMaxLineHeight':1.5,'displayCjkSizeRatio':2,'displayXPadding':.1,'displayYPadding':.1,'displayOptions':['SINGLE_LINE','SCROLL_NORMAL','CYCLE_LANGUAGES'] if name=='destination' else ['SINGLE_LINE']} for name in ['destination','route']]
 dump(P/('headsign_reverse.json' if rev else 'headsign.json'),{'parts':sign_parts,'modelYOffset':0})
for rev in [False,True]:
 parts=[{'names':['floor'],'positionDefinitions':['flipped' if rev else 'origin'],'type':'FLOOR'}]
 parts +=[{'names':[f'way_{side}_{i}'],'positionDefinitions':['flipped' if rev else 'origin'],'type':'DOORWAY'} for side in [-1,1] for i in range(5)]
 dump(P/('interaction_reverse.json' if rev else 'interaction.json'),{'parts':parts,'modelYOffset':1})
p0=json.loads((P/'interaction.json').read_text(encoding='utf-8'));p0['parts']=[p for p in p0['parts'] if p.get('type')!='DISPLAY'];dump(P/'interaction_middle.json',p0)
# MTR native cube convention is (-OBJ.x, OBJ.y, -OBJ.z), in 1/16 m units.
# Use one import path for moving door meshes and their interaction bounds.
door_elements=[];door_groups={}
for g,x,y,z,w,h,l,c,inflate in door_boxes:
 uid=str(uuid.uuid4());cx,cy,cz=-x*16,y*16,-z*16
 u,v=UV[c];uv=[u*1024-1,v*512-1,u*1024+1,v*512+1]
 el={'name':g,'type':'cube','uuid':uid,'from':[cx-w*8+inflate,cy-h*8+inflate,cz-l*8+inflate],'to':[cx+w*8-inflate,cy+h*8-inflate,cz+l*8-inflate],'inflate':inflate,'origin':[0,0,0],'box_uv':True,'shade':True,'uv_offset':[int(u*1024-28),int(v*512-28)],'faces':{k:{'uv':uv,'texture':0} for k in ['north','south','east','west','up','down']}}
 door_elements.append(el);door_groups.setdefault(g,[]).append(uid)
dump(M/'doors.bbmodel',{'meta':{'format_version':'4.9','model_format':'modded_entity','box_uv':False},'name':'doors','resolution':{'width':1024,'height':512},'elements':door_elements,'outliner':[{'name':g,'origin':[0,0,0],'uuid':str(uuid.uuid4()),'children':ids} for g,ids in door_groups.items()],'textures':[{'id':'0','name':'atlas.png','source':'data:image/png;base64,'+base64.b64encode((T/'atlas.png').read_bytes()).decode()}]})
for reverse in [False,True]:
 parts=[]
 for g in door_groups:
  leaf=g.split('_')[3];parts.append({'names':[g],'positionDefinitions':['flipped' if reverse else 'origin'],'renderStage':'INTERIOR_TRANSLUCENT' if g.endswith('_glass') else 'INTERIOR','doorZMultiplier':12 if leaf=='a' else -12,'doorAnimationType':'STANDARD'})
 dump(P/('doors_reverse.json' if reverse else 'doors.json'),{'parts':parts,'modelYOffset':0})

def model(name,props=None,bb=False):return {'modelResource':f'mtr:jinan_line4/models/{name}.{"bbmodel" if bb else "obj"}','textureResource':'mtr:jinan_line4/textures/atlas.png','modelPropertiesResource':f'mtr:jinan_line4/properties/{props or name}.json','positionDefinitionsResource':'mtr:jinan_line4/properties/origin.json','flipTextureV':False}
vehicles=[]
for id,label,mesh,rev in [('tc','头车 Tc','cab',False),('m','中间动车 M','middle',False),('mp','受电弓动车 Mp','motor',False),('tc_reverse','尾车 Tc（反向）','cab',True)]:
 v={'id':'jinan_line4_'+id,'name':'济南地铁4号线 | '+label,'color':'A5D431','transportMode':'TRAIN','width':3,'length':25,'couplingPadding1':0,'couplingPadding2':0,'bogie1Position':-8.5,'bogie2Position':8.5,'hasGangway1':mesh!='cab' or rev,'hasGangway2':mesh!='cab' or not rev,'tags':['family:jinan_line4','iso_3166:CN','doors:5','length:25m'],'models':[model(mesh,mesh+('_reverse' if rev else '')),model('doors','doors_reverse' if mesh=='cab' and not rev else 'doors',True),model('interaction','interaction_reverse' if rev else ('interaction' if mesh=='cab' else 'interaction_middle'),True)],'bogie1Models':[model('bogie')],'bogie2Models':[model('bogie')],'legacySpeedSoundBaseResource':'sp1900','legacySpeedSoundCount':120,'legacyDoorSoundBaseResource':'sp1900','legacyDoorCloseSoundTime':.5}
 vehicles.append(v)
 if mesh=='cab':v['models'].append(model('headsign','headsign_reverse' if rev else 'headsign',True))
for v in vehicles:v['scriptId']='jinan_line4_lcd'
lcd_entry={'id': 'jinan_line4_lcd', 'scriptLocations': ['mtr:jinan_line4/scripts/lcd.js'], 'dataFetchMode': 'ALL', 'input': {'singleRowMax': 18, 'maxPerRow': 18, 'refreshMillis': 200, 'arrivalPageSeconds': 6, 'animationSeconds': 1.4, 'doorCycleSeconds': 1.0, 'arrivalTolerance': 6, 'stoppedSpeed': 0.6, 'screenOffset': 0.02, 'defaultColor': 0xA5D431, 'debug': False}}
dump(ROOT/'assets/mtr/mtr_custom_resources.json',{'vehicles':vehicles,'vehicleScripts':[lcd_entry],'signs':[],'rails':[],'objects':[],'lifts':[]})
dump(ROOT/'pack.mcmeta',{'pack':{'pack_format':22,'description':'济南地铁4号线 · 无标志单线版 v17 | 版本：MTR 4.0.5，JCM 2.3.0 | 这是GPT-6.1-sol (High)接入Codex制作'}})
icon=Image.new('RGB',(128,128),'#14252e');d=ImageDraw.Draw(icon);d.rounded_rectangle((24,16,104,106),18,fill='#cbd1d3');d.rounded_rectangle((30,25,98,68),8,fill='#243c46');d.line((28,79,100,79),fill='#a5d431',width=6);d.text((52,28),'4',font=font,fill='white');d.ellipse((35,87,45,97),fill='white');d.ellipse((83,87,93,97),fill='white');icon.save(ROOT/'pack.png')
print('Generated',len(vehicles),'vehicle definitions;',sum(len(v) for v in scenes.values()),'mesh groups')
