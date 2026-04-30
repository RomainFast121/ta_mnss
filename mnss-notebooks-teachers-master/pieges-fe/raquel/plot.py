#!/usr/bin/env python3

##########
import matplotlib.pyplot as plt
import meshio
import matplotlib.tri as tri
import subprocess
import numpy as np
import os
from IPython.display import IFrame, display
# from Slides import math_helper as mh
# from sympy import *
import matplotlib

################################################################
matplotlib.rcParams['figure.figsize'] = 9, 6
################################################################


# def plot_matrix(matrix, matrix_name):
#     mh.print_latex(matrix_name+"= {0}", Matrix(matrix))


def readMesh(filename, element_type='triangle'):
    mesh = meshio.read(filename)
    conn = []
    for c in mesh.cells:
        if c.type != element_type:
            continue
        conn.extend([i for i in c.data])
    return mesh.points[:, :2], np.array(conn)


def plotMesh(coords, connectivity, field=None):
    triangles = tri.Triangulation(coords[:, 0], coords[:, 1], connectivity)
    plt.axes().set_aspect('equal')
    if field is not None:
        plt.tricontourf(triangles, np.linalg.norm(
            field.reshape(coords.shape), axis=1))
    t = plt.triplot(triangles, '--', lw=.8)


def meshGeo(filename, dim=2, order=1):
    ret = subprocess.run(f"gmsh -2 -order 1 -o tmp.msh {filename}", shell=True)
    if ret.returncode:
        print("Beware, gmsh could not run: mesh is not generated")
    else:
        print("Mesh generated")
        mesh = readMesh('tmp.msh')
        # os.remove('tmp.msh')
        return mesh
    return None


# def votre_opinion_compte(name):
#     display(IFrame('https://www.surveymonkey.com/r/NOTOSURVEY?notebook_set=CIVIL-321&notebook_id=CIVIL-321'+name, 600, 1000))
