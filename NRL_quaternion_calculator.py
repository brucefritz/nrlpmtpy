# -*- coding: utf-8 -*-
"""
Created on Mon Jan 22 23:19:03 2024

@author: bfritz
"""

import numpy as np

"""
; NAME: apply_quaternion.pro
; PURPOSE:  to transform a vector from one coordinate system into another by 
;           applying aquaternion.
; CALLING SEQUENCE: new_vector = apply_quaternion(quat,v)
; INPUT ARGUMENTS: Variable Name           Type                      Description
;
;                     quat            array[4] or [4,n]       a quaternion or array of quaternions
;                      v              array[4] or [4,n]       a vector or array of vectors in quaternion
;															  form  (ie [x,y,z,0])  three-dim vectors [x,y,z]
;															  are also accepted.
; OUTPUTS:  a vector or array of vectors
; CALLED ROUTINES:  qmultiply, qconj
;
; NOTES:  if the input vector is in three dimensions then the output will be a
;           three dimensional vector
;
; MODIFICATION HISTORY: 
;  v1.0  6/17/09
;  v2.0  12/04/2010 SAB  Extensive revision to data parsing logic.  Corrected 
;                        the orderof operation applying the quaternion and its
;                        conjugate to the vector.
"""

def apply_quaternion(quat, v):
    nquats = len(quat) // 4
    shape_v = np.shape(v)
    nelem = shape_v[0]
    if len(shape_v) == 1: numv = 1
    else: numv = shape_v[1]
    # 
    if nquats == 1 and numv == 1:   nout = 1
    elif nquats == 1 and numv > 1:  nout = numv
    # elif nquats > 1 and numv == 1:  nout = nquats
    elif numv != nquats:
        print('Incompatible dimensions between quaternions and vectors.')
        return -1
    else: nout = nquats
    # Convert vector to a quaternion with 0 scalar
    v2 = np.zeros((4, nout), dtype=float)
    if nelem == 3: v2[0:3, :] = v
    else:
        v2 = v
        if np.max(np.abs(v2[3, :])) > 1e-5:
            print('Non-zero scalar elements in 4-vector. May be invalid.')
    # Apply quaternion by multiplying v_new = q * v * q-1
    out = qmultiply(quat, qmultiply(v2, qconj(quat)))
    # Converts output into cartesian form if it was input that way
    if nelem == 3:  out = out[0:3, :]
    return out


"""
; NAME: qconj.pro
; PURPOSE:  Takes a unit quaternion or an array of unit quaternions and conjugates them
;          (if input quaternions are not in unit form then the code will normalize them)
; CALLING SEQUENCE:  quaternion_conjugate = qconj( quaternion )
; INPUT ARGUMENTS: Variable Name           Type                      Description
;                   quaternion		   4 element array        must be in the form [i,j,k,a]
;															  where a is the scalar component
; OUTPUTS: a  4 x n  array of quaternions of the form [i,j,k,a]
; MODIFICATION HISTORY: v1.0  6/17/09
"""
def qconj(q):
    n = q.size // 4
    q = np.array(q, dtype=float)
    # 
    # This normalizes quaternions
    DNORM = np.linalg.norm(q, axis=0)
    # 
    # Conjugates the quaternions
    conjugate = np.zeros((4, n), dtype=float)
    # 
    conjugate[0, :] = -q[0, :] / DNORM
    conjugate[1, :] = -q[1, :] / DNORM
    conjugate[2, :] = -q[2, :] / DNORM
    conjugate[3, :] = q[3, :] / DNORM
    # 
    return conjugate


"""
; NAME: qmultiply.pro
;
; PURPOSE:  multiplies quaternions.  Accepts two inputs which allows for 4 possible cases
;             case 1: two quaternions are inputed and they are multiplied                            q1 * q2
;			  case 2: an array of quaternions and a sigle quaternion is inputed.  Every quaternion
;                     in the array is right-multiplied by the single quaternion.                     q1[0]*q2 , q1[1]*q2 ...
;             case 3: a single quaternion and an array of quaternions are inputed.  Every quaternion
;                     in the array is left-multiplied by the single quaternion.                      q1*q2[0] , q1*q2[1] ...
;             case 4: two arrays of quaternions (of the same length) are inputed.  For each index of
;                     the arrays the quaternion of the first array will be left multiplied with the  q1[0]*q2[0] , q1[1]*q2[1] ..
;                     quaternion of the second array.
;
; CALLING SEQUENCE:  new_quaternion = qmultiply(quaternion1, quaternion2)
;
; INPUT ARGUMENTS: Variable Name           Type                      Description
;
;                       q1          array:  [4] or [4,n]               as above
;                       q2          array:  [4] or [4,n]
;
; OUTPUTS: a 4 x n  array of quaternions.  All returned quaternions will be normalized
;
; NOTES:  as noted previously the order of the quaternions inputed is important.  quaternion multiplication
;         is not commutative. The first quaternion will be left-multiplied with the second quaternion  (ie. q1 * q2)
;
; MODIFICATION HISTORY: v1.0  6/17/09
"""

def qmultiply(q1, q2):
    # Handle input/output dimensions
    s1 = np.shape(q1)
    nelem1 = s1[0]
    if len(s1) == 1:    n1 = 1
    elif len(s1) == 2:  n1 = s1[1]
    # 
    s2 = np.shape(q2)
    nelem2 = s2[0]
    if len(s2) == 1:    n2 = 1
    elif len(s2) == 2:  n2 = s2[1]
    # 
    if nelem1 != 4 or nelem2 != 4:
        print("Quaternion does not have 4 elements.")
        return -1

    if n1 == 1 and n2 == 1:     nout = 1
    elif n1 == 1 and n2 > 1:    nout = n2
    elif n1 > 1 and n2 == 1:    nout = n1
    elif n1 != n2:
        print("Incompatible dimensions between quaternions.")
        return -1
    else:                       nout = n1

    # Make double precision, simplify dimensions
    x1 = np.double(q1[0, :])
    y1 = np.double(q1[1, :])
    z1 = np.double(q1[2, :])
    w1 = np.double(q1[3, :])

    x2 = np.double(q2[0, :])
    y2 = np.double(q2[1, :])
    z2 = np.double(q2[2, :])
    w2 = np.double(q2[3, :])

    # Make the output array
    result = np.zeros((4, nout), dtype=float)
    result[0, :] = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    result[1, :] = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    result[2, :] = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
    result[3, :] = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2

    return qnorm(result)

def qnorm(q):
    return q / np.linalg.norm(q, axis=0)
