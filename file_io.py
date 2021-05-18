import sys
import re
import numpy as np


def read_obj(filepath):

    with open(filepath) as obj:
        r = obj.read()

    position_data = read_position(r)
    positions = position_data['v']
    normals = read_normal(r)
    faces = read_faces(r)

    x, y, z = find_center(position_data['box'])
    # vertex_data = build_vertex_input(positions, faces, normals).flatten()

    file_data = {
        # "vertex":vertex_data,
        "v":positions,
        "n":normals,
        "f":faces,
        "center":[x, y, z],
        "bbox": position_data['box'],
        "normal_data":len(normals) > 0
    }

    return file_data


def build_vertex_input(positions, faces, normals):
    vertex_pos = list()

    if len(normals) > 0:
        for v, n in zip(faces['v'], faces['n']):
            vertex_pos.append(positions[v])
            vertex_pos.append(normals[n])

    else:
        for v in faces['v']:
            vertex_pos.append(positions[v])

    return np.asarray(vertex_pos, dtype='float32')


def read_normal(r):
    normal = list()
    vn_re = re.compile('vn .*')
    vn_lines = vn_re.findall(r)

    for line in vn_lines:

        elements = line.split()[1:]
        normal_x = float(elements[0])
        normal_y = float(elements[1])
        normal_z = float(elements[2])

        normal.append([normal_x, normal_y, normal_z])
    
    return normal


def read_texture(r):
    texture = list()
    vt_re = re.compile('vt .*')
    vt_lines = vt_re.findall(r)

    for line in vt_lines:

        elements = line.split()[1:]

        tex_x = float(elements[0])
        tex_y = float(elements[1])

        texture.append([tex_x, tex_y])

    return texture


def read_position(r):
    global x_min, y_min, z_min, x_max, y_max, z_max

    # Limits of obj file
    x_min = sys.float_info.max
    y_min = sys.float_info.max
    z_min = sys.float_info.max

    x_max = sys.float_info.min
    y_max = sys.float_info.min
    z_max = sys.float_info.min

    position = list()
    v_re = re.compile('v .*')
    v_lines = v_re.findall(r)

    for line in v_lines:
        
        elements = line.split()[1:]
        
        x = float(elements[0])
        y = float(elements[1])
        z = float(elements[2])

        position.append([x, y, z])

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

    # Normalization
    v_max = np.max(position)
    position = position/v_max
    x_min, y_min, z_min, x_max, y_max, z_max = x_min/v_max, y_min/v_max, z_min/v_max, x_max/v_max, y_max/v_max, z_max/v_max

    position_data = {
        "v": position,
        "box": [ x_min, x_max, y_min, y_max, z_min, z_max]
    }

    return position_data


def read_faces(r):
    v_list = list()
    data = {'v':[], 'n':[]}

    f_re = re.compile('f .*')
    f_lines = f_re.findall(r)

    for line in f_lines:

        elements = line.split()[1:]

        for el in elements:
            if '/' in el:
                v = el.split('/')[0]
                data['v'].append(int(v)-1)

                n = el.split('/')[-1]
                data['n'].append(int(n)-1)
            
            else: 
                data['v'].append(int(el)-1)
    
    return data


def find_center(box_limits):
    [x1, x2, y1, y2, z1, z2] = box_limits
    return (x2+x1)/2, (y2+y1)/2, (z2+z1)/2