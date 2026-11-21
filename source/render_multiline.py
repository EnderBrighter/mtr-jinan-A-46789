import bpy, pathlib, math
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/jinan_line4.blend'))
scene=bpy.context.scene
scene.render.resolution_x=900
scene.render.resolution_y=600
scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=32
cam=scene.camera
for line in [4,6,7,8,9]:
    image=bpy.data.images.load(str(ROOT/f'assets/mtr/jinan_line{line}/textures/atlas.png'),check_existing=False)
    image.pack()
    for material in bpy.data.materials:
        if material.use_nodes:
            for node in material.node_tree.nodes:
                if node.type=='TEX_IMAGE':node.image=image
    for name,pos,target,scale,lens in [
        ('front',(5.7,17.8,4.2),(0,10.6,2.05),7.2,23),
        ('seat',(-.45,1,2.24),(1.16,2.5,1.7),None,28)]:
        cam.location=pos
        cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cam.data.type='ORTHO' if scale else 'PERSP'
        cam.data.ortho_scale=scale or 10
        cam.data.lens=lens
        scene.render.filepath=str(ROOT/f'preview/v11_line{line}_{name}.png')
        bpy.ops.render.render(write_still=True)
    if line==4:
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/jinan_line4.blend'))
