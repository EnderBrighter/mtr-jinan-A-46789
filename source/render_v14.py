from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'source/build_blender.py').read_text(encoding='utf-8').split('cam.location=(20,28,12)')[0]
exec(compile(s,str(root/'source/build_blender.py'),'exec'))

# Show the actual LCD test output on the restored full-height screen in previews.
tex=bpy.data.images.load(str(ROOT/'preview/lcd_running_16.png'));tex.pack()
mat=materials['screen'];nodes=mat.node_tree.nodes;im=nodes.new('ShaderNodeTexImage');im.image=tex
em=nodes.new('ShaderNodeEmission');mat.node_tree.links.new(im.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],nodes.get('Material Output').inputs['Surface'])
for collection in collections.values():
 for ob in collection.objects:
  if not ob.name.startswith('lcd_mounts'):continue
  mesh=ob.data
  for face in mesh.polygons:
   if mesh.materials[face.material_index].name!='screen':continue
   for idx in face.loop_indices:
    q=mesh.vertices[mesh.loops[idx].vertex_index].co
    z=-q.y;u=z-round(z/5)*5;v=q.z-3.325
    mesh.uv_layers.active.data[idx].uv=((u/.87+1)/2 if q.x>0 else (1-u/.87)/2,(v/.1425+1)/2)

scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.eevee.taa_render_samples=48
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/jinan_line4_v14.blend'))
render('v14_door_exterior.png',(7,0,2.25),(1.48,0,2.25),3.4)
render('v14_lcd_interior.png',(0,-.35,2.35),(1.25,0,3.325),lens=22)
for ob in collections['cab'].objects:
 if ob.name.startswith('door_'):ob.location.y=.75 if '_a' in ob.name else -.75
render('v14_doors_open.png',(7,0,2.25),(1.48,0,2.25),3.4)

for ob in collections['cab'].objects:
 if ob.name.startswith('door_'):ob.location.y=0
render('v14_interior.png',(0,-8.3,2.36),(0,9,2.36),lens=20)
render('v14_exterior.png',(20,28,12),(0,0,1.8),29)
render('v14_seats.png',(0,-5,2.3),(0,3,1.9),lens=24)
