"""
in verts_in v
in edges_in s
in s_param s d=0.5 n=2
in division s d=5 n=2
out verts_out v
out edges_out s
"""

#Gyrovector space for making hyperbolic polyhedra
# Porting R code below to blender python
# source: https://laustep.github.io/stlahblog/posts/hyperbolicPolyhedra.html

# ***************************************************************
# *** Remove double vertices after applying this script       ***
# ***************************************************************

import numpy as np
import math

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


verts = np.array([])
edges = np.array([])
for i, edge in enumerate(edges_in[0]):
    a = np.array(verts_in[0][edge[0]])
    b = np.array(verts_in[0][edge[1]])
    verts = np.append(verts, gyrosegment(a, b, s_param, division))
    edges = np.append(edges, [[i, i+1] for i in \
                range(i*(division+1), (i+1)*(division+1)-1)])

verts_out = [verts.reshape(-1, 3).tolist()]
edges_out = [edges.reshape(-1, 2).astype(np.int32).tolist()]

