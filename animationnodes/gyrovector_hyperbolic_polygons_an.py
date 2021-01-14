"""
in verts_in v
in faces_in s
in s_param s d=0.5 n=2
in depth s d=3 n=2
out verts_out v
out edges_out s
out faces_out s
"""

#Gyrovector space for making hyperbolic polyhedra
# Porting R code below to blender python
# source: https://laustep.github.io/stlahblog/posts/hyperbolicPolyhedra.html

# Source objects are needed to be triangulated in advance

import numpy as np
import math
import copy
from mathutils import Vector
from animation_nodes.data_structures import Vector3DList, EdgeIndicesList, PolygonIndicesList


def dotprod(X, Y=[]):
    return np.dot(X, (X if Y==[] else Y))

def betaF(A, s=1.0):
    # f = lambda a1, s1: 1.0 / math.sqrt(1.0 + dotprod(a1) / s1**2)
    # np_f = np.frompyfunc(f, 2, 1)
    # return np_f(A, s)
    # np_f = np.vectorize(lambda a1, s1: 1.0 / math.sqrt(1.0 + dotprod(a1) / s1**2))
    # return np_f(A, s)
    return 1.0 / math.sqrt(1.0 + dotprod(A) / s**2)

def gyroadd(A, B, s=1.0):
    A_ = np.array(A)
    B_ = np.array(B)
    betaA = betaF(A_, s)
    betaB = betaF(B_, s)
    return (1.0 + (betaA / (1.0 + betaA)) * dotprod(A_, B_) / s**2 \
            + (1.0 - betaB) / betaB) * A_ + B_

def gyroscalar(r, A, s=1.0):
    A_ = np.array(A)
    Anorm = math.sqrt(dotprod(A_))
    return  (s / Anorm) * np.sinh(r * np.arcsinh(Anorm/s)) * A_

def gyroABt(A, B, t, s=1.0):
    return gyroadd(A, gyroscalar(t, gyroadd(-A, B, s), s), s)
    
def gyromidpoint(A, B, s=1.0):
    return gyroABt(A, B, 0.5, s)

def gyrosegment(A, B, s=1.0, n=50):
    # gyroABt_func = np.frompyfunc(gyroABt, 4, 1)
    t = [i / n for i in range(0, n)]
    t.append(1.0)
    # return np.transpose(gyroABt_func(A, B, t, s))
    return [np.transpose(gyroABt(A, B, t_, s)).tolist() for t_ in t]


# verts = np.array([])
# edges = np.array([])
# for i, edge in enumerate(edges_in[0]):
#     a = np.array(verts_in[0][edge[0]])
#     b = np.array(verts_in[0][edge[1]])
#     verts = np.append(verts, gyrosegment(a, b, s_param, division))
#     edges = np.append(edges, [[i, i+1] for i in \
#                 range(i*(division+1), (i+1)*(division+1)-1)])

# verts_out = [verts.reshape(-1, 3).tolist()]
# faces_out = [edges.reshape(-1, 2).tolist()]

def gyrosubdiv(verts, indices, s=1.0):
    # indices of original triangle
    i0, i1, i2 = int(indices[0]), int(indices[1]), int(indices[2])
    # new vertices (middle points)
    M12 = np.round(gyromidpoint(verts[i0], verts[i1], s), 6)
    M23 = np.round(gyromidpoint(verts[i1], verts[i2], s), 6)
    M31 = np.round(gyromidpoint(verts[i2], verts[i0], s), 6)

    candidates = [M12, M23, M31]
    new_verts, new_indices, new_edges = [], [], []
    offset = 0    
    for cv in candidates:
        exists = np.all(verts == cv, axis=1)
        exists_indices = np.where(exists == True)
        if len(exists_indices[0]) > 0:
            new_indices.append(exists_indices[0][0])
        else:
            new_verts.append(cv)
            new_indices.append(len(verts) + offset)
            offset += 1            
         
    # new_verts = [M12, M23, M31]
    # new_indices = [len(verts), len(verts) + 1, len(verts) + 2]
    new_triangles = [[i0, new_indices[0], new_indices[2]], \
                [i1, new_indices[1], new_indices[0]], \
                [i2, new_indices[2], new_indices[1]], \
                [new_indices[0], new_indices[1], new_indices[2]] ]
    
    return new_verts, new_indices, new_triangles

def gyrosubdiv_loop(verts, triangle_faces, s=1.0, depth=5):
    
    new_verts = np.round(copy.deepcopy(verts), 6)
    new_triangles = copy.deepcopy(triangle_faces)
    
    remain = depth
    while (remain > 0):
        
        added_verts = np.array([])
        added_triangles = np.array([])
        for triangle in new_triangles:
            new_vs, new_ids, new_tris = \
                    gyrosubdiv(new_verts, triangle, s)
            # added_verts = np.append(added_verts, new_vs)
            added_triangles = np.append(added_triangles, new_tris)
            new_verts = np.append(new_verts, new_vs).reshape(-1, 3)
        
        new_triangles = added_triangles.reshape(-1, 3)
        
        remain -= 1
    
    return new_verts, new_triangles
# def extract_new_edges(new_triangles):
#     edges = np.array([])
#     for triangle in new_triangles:
#         edges.append([triangle[0], triangle[1]])

verts, faces = gyrosubdiv_loop(np.array(verts_in), np.array(faces_in), s_param, depth)


verts_out_list = [verts.reshape(-1, 3).tolist()]
verts_out = Vector3DList()
for v in verts_out_list[0]:
    verts_out.append(Vector((v[0], v[1], v[2])))

faces_out_list = [faces.reshape(-1, 3).astype(np.int32).tolist()]
faces_out = PolygonIndicesList()
for f in faces_out_list[0]:
    faces_out.append(tuple((f[0], f[1], f[2])))

edges_out = np.array([])
for face in faces_out_list[0]:
    edges = [sorted([int(face[0]), int(face[1])]), sorted([int(face[1]), int(face[2])]), sorted([int(face[2]), int(face[0])])]
    
    if len(edges_out) == 0:
        edges_out = np.array([edges[0], edges[1], edges[2]])
    else:
        for edge in edges:
            exists = np.all(edges_out == edge, axis=1)
            exists_indices = np.where(exists == True)
            if len(exists_indices[0]) == 0:
                edges_out = np.append(edges_out, edge)
                edges_out = edges_out.reshape(-1, 2)

edges_out_list = [edges_out.tolist()]
edges_out = EdgeIndicesList()
for edge in edges_out_list[0]:
    edges_out.append(tuple((edge[0], edge[1])))
    