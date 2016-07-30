# designed to be run with blender

# https://blender.stackexchange.com/questions/1365/how-can-i-run-blender-from-command-line-or-a-python-script-without-opening-a-gui

import sys
import bpy

argv = sys.argv
argv = argv[argv.index("--") + 1:]  # get all args after "--"

# From: http://blenderscripting.blogspot.co.nz/2012/03/deleting-objects-from-scene.html
# PKHG points out in the comments that there are more convenient ways to do this 

bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete(use_global=False)

for item in bpy.data.meshes:
    bpy.data.meshes.remove(item)
    
bpy.ops.import_mesh.stl(filepath=argv[0])
bpy.ops.export_scene.fbx(filepath=argv[1])