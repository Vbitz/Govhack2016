import subprocess, os, sys
from os.path import abspath as path_absoulte
from os.path import join as path_join

OPENSCAD_PATH = "C:\\Users\\Joshua\\dev\\apps\\openscad-2016.02.01\\openscad.com"

OUTPUT_DIR = path_join(path_absoulte("../../pub/napierModel/"), sys.argv[1])

if __name__ == "__main__":
    for baseDir, _, files in os.walk(OUTPUT_DIR):
        for f in files:
            f = path_join(OUTPUT_DIR, f)
            fname, ext = os.path.splitext(f)
            if ext != ".scad":
                continue
            openscad_args = [OPENSCAD_PATH, "-o", fname + ".stl", f]
            print "processing", f
            try:
                subprocess.check_call(openscad_args)
            except subprocess.CalledProcessError, e:
                print "error", f