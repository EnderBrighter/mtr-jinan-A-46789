"""Build the editable Blender 3.0 scene and render photo-review views."""
import bpy,bmesh,json,pathlib,math,sys
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from mesh_topology import triangles
data=json.loads((ROOT/'source/geometry.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
img=bpy.data.images.load(str(ROOT/'assets/mtr/jinan_line4/textures/atlas.png'));img.pack()
colours=['silver','roof','green','glass','black','white','floor','steel','seat','yellow','light','red','rubber','screen','clear_glass','seal']
materials={}
for c in colours:
 mat=bpy.data.materials.new(c);mat.use_nodes=True;n=mat.node_tree.nodes.new('ShaderNodeTexImage');n.image=img;n.interpolation='Closest';bs=mat.node_tree.nodes.get('Principled BSDF');mat.node_tree.links.new(n.outputs['Color'],bs.inputs['Base Color'])
 mat.node_tree.links.new(n.outputs['Alpha'],bs.inputs['Alpha']);mat.blend_method='CLIP';mat.use_backface_culling=True
 bs.inputs['Roughness'].default_value=.48 if c in ['seat','rubber','floor','white'] else .38;bs.inputs['Metallic'].default_value=.35 if c in ['silver','roof','steel'] else 0
 if c in ['glass','clear_glass']:
  mat.node_tree.links.new(n.outputs['Alpha'],bs.inputs['Alpha']);bs.inputs['Roughness'].default_value=.11;mat.blend_method='HASHED';mat.use_screen_refraction=True;mat.use_backface_culling=True;mat.show_transparent_back=False
 if c=='light':mat.node_tree.links.new(n.outputs['Color'],bs.inputs['Emission']);bs.inputs['Emission Strength'].default_value=.7
 materials[c]=mat
collections={}
for name,groups in data.items():
 col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col);collections[name]=col
 for group,polys in groups.items():
  verts=[];faces=[];uvs=[];face_colours=[]
  for p in polys:
   idx=len(verts);verts.extend([(x,-z,y) for x,y,z in p['v']]);uvs.extend([(u,1-v) for u,v in p['uv']])
   for tri in triangles(p['v']):faces.append(tuple(idx+i for i in tri));face_colours.append(p['c'])
  mesh=bpy.data.meshes.new(name+'_'+group);mesh.from_pydata(verts,[],faces);mesh.update();uv=mesh.uv_layers.new()
  for i,loop in enumerate(mesh.loops):uv.data[i].uv=uvs[loop.vertex_index]
  for c in colours:mesh.materials.append(materials[c])
  for f,c in zip(mesh.polygons,face_colours):f.material_index=colours.index(c);f.use_smooth=True
  # Keep source winding: an automatic normal repair concealed missing front faces in-game.
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.000001);bm.to_mesh(mesh);bm.free();mesh.use_auto_smooth=True;mesh.auto_smooth_angle=math.radians(38)
  ob=bpy.data.objects.new(group,mesh);col.objects.link(ob);ob.hide_render=name!='cab' or group in ['headlights','tail_lights'];ob.hide_viewport=ob.hide_render
# Bogies instantiated for the head car, independent of the source origin.
for z in [-8.5,8.5]:
 ob=bpy.data.objects.new('cab_bogie',next(iter(collections['bogie'].objects)).data);collections['cab'].objects.link(ob);ob.location.y=-z
# Neutral studio, orthographic geometry review and perspective interior review.
bpy.ops.mesh.primitive_plane_add(size=500,location=(0,0,-.02));stage=bpy.context.object;stage.name='Studio floor';mt=bpy.data.materials.new('Studio neutral');mt.diffuse_color=(.105,.13,.15,1);stage.data.materials.append(mt)
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.35,.39,.43,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65
for loc,power,size in [((5,10,12),2100,8),((-7,0,9),1800,10),((1,-10,12),2400,9)]:
 bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.data.energy=power;l.data.shape='DISK';l.data.size=size;l.rotation_euler=(Vector((0,0,1.8))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene=bpy.context.scene;scene.camera=cam;scene.render.engine='BLENDER_EEVEE';scene.eevee.use_gtao=True;scene.eevee.gtao_distance=1.6;scene.eevee.use_soft_shadows=True;scene.eevee.taa_render_samples=96
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.view_settings.view_transform='Standard';scene.view_settings.look='Medium High Contrast';scene.view_settings.exposure=0
cam.data.clip_start=.025

def render(name,pos,target,scale=None,lens=23):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if scale else 'PERSP';cam.data.ortho_scale=scale or 10;cam.data.lens=lens;scene.render.filepath=str(ROOT/'preview'/name);bpy.ops.render.render(write_still=True)
cam.location=(20,28,12);cam.rotation_euler=(Vector((0,0,1.8))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=29
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/jinan_line4.blend'))
render('cab_overview.png',(20,28,12),(0,0,1.8),29)
render('cab_front.png',(5.7,17.8,4.2),(0,10.6,2.05),7.2)
render('cab_front_orthographic.png',(0,20,2.15),(0,11,2.15),6.4)
render('cab_inside.png',(0,8.7,2.30),(0,12.0,2.35),lens=22)
render('cab_side_profile.png',(8,11,2.2),(0,11,2.2),5.4)
render('cab_window_threequarter.png',(5.5,16.5,3.7),(0,11.65,2.45),4.5)
render('cab_window_side_detail.png',(7,11.6,2.6),(0,11.6,2.6),3.4)
render('interior.png',(0,-8,2.36),(0,10,2.36),lens=20)
render('seat_detail.png',(-.45,1,2.24),(1.16,2.5,1.7),lens=28)
render('lcd_mount.png',(0,0,2.38),(1.245,0,3.115),lens=21)
render('door_joint.png',(0,.9,2.1),(1.40,0,1.55),lens=28)
render('door_header_detail.png',(3.9,-.30,2.95),(1.49,0,3.015),.72)
for ob in collections['cab'].objects:
 if ob.name.startswith('door_'):ob.location.y=.75 if '_a' in ob.name else -.75
render('doors_open.png',(8.5,1,4.0),(0,0,1.9),13)
for ob in collections['cab'].objects:
 ob.hide_render=True
 if ob.name.startswith('door_'):ob.location.y=0
for ob in collections['middle'].objects:ob.hide_render=False
for ob in list(collections['middle'].objects):
 dup=ob.copy();dup.data=ob.data;collections['middle'].objects.link(dup);dup.location.y=-25;dup.hide_render=False
render('gangway_join.png',(0,-10.2,2.15),(0,-15,2.15),lens=24)
# Six-car consist: Tc + M + Mp + Mp + M + reverse Tc, total pitch 150 m.
for col in collections.values():
 for ob in col.objects:ob.hide_render=True
train_col=bpy.data.collections.new('Six-car preview');scene.collection.children.link(train_col)
for index,name in enumerate(['cab','middle','motor','motor','middle','cab']):
 for ob in list(collections[name].objects):
  if ob.location.length>.001 or ob.name.startswith('cab_bogie'):continue
  dup=ob.copy();dup.data=ob.data;train_col.objects.link(dup);dup.location.y=-25*index
  if index==5:dup.rotation_euler.z=math.pi
  dup.hide_render=False
 for bogie_z in [-8.5,8.5]:
  dup=bpy.data.objects.new('consist_bogie',next(iter(collections['bogie'].objects)).data);train_col.objects.link(dup);dup.location.y=-25*index-bogie_z
render('six_car_consist.png',(75,12,39),(0,-62.5,1.7),135)
