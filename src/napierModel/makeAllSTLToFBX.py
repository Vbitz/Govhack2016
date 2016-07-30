import subprocess, os
from os.path import abspath as path_absoulte
from os.path import join as path_join

OPENSCAD_PATH = "C:\\Users\\Joshua\\dev\\apps\\openscad-2016.02.01\\openscad.com"
BLENDER_PATH = "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe"

OUTPUT_DIR = path_absoulte("../../pub/napierModel/output")

if __name__ == "__main__":
    for baseDir, _, files in os.walk(OUTPUT_DIR):
        for f in files:
            f = path_join(OUTPUT_DIR, f)
            fname, ext = os.path.splitext(f)
            if ext != ".stl":
                continue
            stlPath = f
            fbxPath = fname + ".fbx"
            blender_args = [BLENDER_PATH, "--background", "--python", "stlToFbx.py", "--", stlPath, fbxPath]
            print "processing", f
            try:
                subprocess.check_call(blender_args)
            except subprocess.CalledProcessError, e:
                print "error", f
                