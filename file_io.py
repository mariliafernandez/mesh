
import sys
import re
import numpy as np


def read_obj(filepath):

    data = dict()

    with open(filepath) as obj:
        r = obj.read()

    vertices = read_vertices(r)
    faces = read_faces(r)

    x_center, y_center, z_center = find_center(vertices['box'])

    file_data = {
        "vertices":vertices,
        "faces":faces,
        "center":[x_center, y_center, z_center]

    }

    # T = ut.matTranslate(-x_center, -y_center, -z_center)
    # M = np.matmul(T,M)

    return file_data

def read_normal(r):
    vertices_n = list()
    vn_re = re.compile('vn .*')
    vn_lines = vn_re.findall(r)

    for line in vn_lines:

        elements = line.split()[1:]

        for el in elements:
            vertices_n.append(float(el))

    return np.asarray(vertices_n, dtype='float32')

def normalize(v):
    return v/np.max(v)


def read_vertices(r):
    global x_min, y_min, z_min, x_max, y_max, z_max

    # Limits of obj file
    x_min = sys.float_info.max
    y_min = sys.float_info.max
    z_min = sys.float_info.max

    x_max = sys.float_info.min
    y_max = sys.float_info.min
    z_max = sys.float_info.min

    vertices = list()
    v_re = re.compile('v .*')
    v_lines = v_re.findall(r)

    for line in v_lines:
        
        elements = line.split()[1:]
        
        x = float(elements[0])
        y = float(elements[1])
        z = float(elements[2])

        vertices.append(x)
        vertices.append(y)
        vertices.append(z)

        if x > x_max:
            x_max = x
        if x < x_min:
            x_min = x
        if y > y_max:
            y_max = y
        if y < y_min:
            y_min = y
        if z > z_max:
            z_max = z
        if z < z_min:
            z_min = z

    vertices = np.asarray(vertices, dtype='float32')
    v_max = np.max(vertices)
    vertices = vertices/v_max

    v_data = {
        "v": np.asarray(vertices, dtype='float32'),
        "box": [ x_min/v_max, x_max/v_max, y_min/v_max, y_max/v_max, z_min/v_max, z_max/v_max]
    }

    return v_data


def read_faces(r):
    v_list = list()
    vt_list = list()
    vn_list = list()
    indices = dict()

    f_re = re.compile('f .*')
    f_lines = f_re.findall(r)

    for line in f_lines:

        elements = line.split()[1:]

        for el in elements:
            if '/' in el:
                v = el.split('/')[0]
                # vt = el.split('/')[1]
                # vn = el.split('/')[2]
            
                if v:
                    v_list.append(int(v)-1)
                # if vt:
                #     vt_list.append(int(vt)-1)
                # if vn:
                #     vn_list.append(int(vn)-1)
            
            else: v_list.append(int(el)-1)
            
    
    count_vertices = len(v_list)
 
    data = {
        "v":np.asarray(v_list, dtype='uint32'),
        "vt":np.asarray(vt_list, dtype='uint32'),
        "vn":np.asarray(vn_list, dtype='uint32'),
        "n":count_vertices
    }

    return data


def find_center(box_limits):
    [x1, x2, y1, y2, z1, z2] = box_limits
    return (x2+x1)/2, (y2+y1)/2, (z2+z1)/2