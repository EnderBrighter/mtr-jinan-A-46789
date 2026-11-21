from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'source/build_blender.py').read_text(encoding='utf-8').split('cam.location=(20,28,12)')[0]
exec(compile(s,str(root/'source/build_blender.py'),'exec'))
scene.render.resolution_x=1400;scene.render.resolution_y=900;scene.eevee.taa_render_samples=48
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/jinan_line4_v12.blend'))
render('v12_door_exterior.png',(7,0,2.25),(1.48,0,2.25),3.4)
render('v12_lcd_interior.png',(0,-.35,2.35),(1.25,0,3.05),lens=22)
for ob in collections['cab'].objects:
 if ob.name.startswith('door_'):ob.location.y=.75 if '_a' in ob.name else -.75
render('v12_doors_open.png',(7,0,2.25),(1.48,0,2.25),3.4)
