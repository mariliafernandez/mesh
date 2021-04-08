#!/usr/bin/env python3

import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import argparse
sys.path.append('../lib/')
import utils as ut
from pathlib import Path
from ctypes import c_void_p

# from . import io
import file_io as io

# Initial Transform Matrix
M = np.identity(4, dtype='float32')

# Window size
win_width  = 800
win_height = 600

# Field of view
fovy = np.radians(60)

# Total vertices to be drawn
count_vertices = 0
box_limits = None
center = [0, 0, 0]
angle_axis = [0, 0, 0]

filepath = None
program = None
line = False
mode = None
VAO = None


## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;

uniform mat4 transform;
uniform mat4 projection;
uniform mat4 view;

void main()
{
    gl_Position = projection * view * transform * vec4(position, 1.0);
}
"""

## Fragment shader.
fragment_code = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.7f, 0.7f, 0.7f, 1.0f);
} 
"""

def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glBindVertexArray(VAO)
    gl.glUseProgram(program)

    # Transformations
    loc = gl.glGetUniformLocation(program, "transform")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())


    [x_max, x_min, y_max, y_min, z_max, z_min] = box_limits
    print(count_vertices)
    print(M)

    # View
    # z_near = z_min + (y_max-y_min)/np.tan(fovy)
    z_near = (y_max-y_min)*4.0/np.tan(fovy) # Funciona pro cubo

    print(z_near)
    view = ut.matTranslate(0.0, 0.0, z_near) 
    # view = ut.matTranslate(0.0, 0.0, z_near-1)

    loc = gl.glGetUniformLocation(program, "view")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())

    # Projection
    # projection = ut.matOrtho(x_min*1.5, x_max*1.5, y_min*1.5, y_max*1.5, 0.1, 500)
    projection = ut.matPerspective(fovy, win_width/win_height, 0.1, 300)
    loc = gl.glGetUniformLocation(program, "projection")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())


    gl.glDrawElements(gl.GL_TRIANGLES, count_vertices, gl.GL_UNSIGNED_INT, None)

    glut.glutSwapBuffers()


def reshape(width,height):

    win_width = width
    win_height = height
    gl.glViewport(0, 0, width, height)
    glut.glutPostRedisplay()

def switch_view(line):
    if line:
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    else:
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    
    glut.glutPostRedisplay()


def special_keyboard(key, x_mouse, y_mouse):
    handle_transform(key)


def keyboard(key, x_mouse, y_mouse):
    
    global type_primitive, line, mode
    
    if key == b't':
        mode = 'translate'
        print('translate')
    elif key == b'r':
        mode='rotate'
        print('rotate')
    elif key == b'e':
        mode='scale'
        print('scale')
    elif key == b'v':
        line = not line
        switch_view(line)
    else:
        handle_transform(key)

    

def handle_transform(key_pressed):
    x_max, y_max, z_max = box_limits[1], box_limits[3], box_limits[5]
    unit = 0.01*max(x_max, y_max, z_max)

    if mode == 'translate':
        if key_pressed ==  glut.GLUT_KEY_UP:
            translate(0.0, unit, 0.0)
        elif key_pressed == glut.GLUT_KEY_DOWN:
            translate(0.0, -unit, 0.0)
        elif key_pressed == glut.GLUT_KEY_RIGHT:
            translate(unit, 0.0, 0.0)
        elif key_pressed == glut.GLUT_KEY_LEFT:
            translate(-unit, 0.0, 0.0)
        elif key_pressed == b'a':
            translate(0.0, 0.0, unit)
        elif key_pressed == b'd':
            translate(0.0, 0.0, -unit)

    elif mode == 'rotate':
        angle = 1.0
        if key_pressed == glut.GLUT_KEY_UP:
            rotate('x', angle)
        elif key_pressed == glut.GLUT_KEY_DOWN:
            rotate('x', -angle)
        elif key_pressed == glut.GLUT_KEY_RIGHT:
            rotate('y', angle)
        elif key_pressed == glut.GLUT_KEY_LEFT:
            rotate('y', -angle)
        elif key_pressed == b'a':
            rotate('z', angle)
        elif key_pressed == b'd':
            rotate('z', -angle)
    
    elif mode == 'scale':
        coeff=0.01

        if key_pressed == glut.GLUT_KEY_UP:
            scale(1, 1+coeff, 1)
        elif key_pressed == glut.GLUT_KEY_DOWN:
            scale(1, 1-coeff, 1)
        elif key_pressed == glut.GLUT_KEY_RIGHT:
            scale(1+coeff, 1, 1)
        elif key_pressed == glut.GLUT_KEY_LEFT:
            scale(1-coeff, 1, 1)
        elif key_pressed == b'a':
            scale(1, 1, 1+coeff)
        elif key_pressed == b'd':
            scale(1, 1, 1-coeff)

    glut.glutPostRedisplay()


def translate(x, y, z):
    global M, center

    T = ut.matTranslate(x, y, z)
    M = np.matmul(T,M)
    
    center[0] += x
    center[1] += y
    center[2] += z


def scale(x, y, z):
    global M
    x_center, y_center, z_center = center[0], center[1], center[2]

    translate(-x_center, -y_center, -z_center)

    S = ut.matScale(x, y, z)
    M = np.matmul(S,M)

    translate( x_center, y_center, z_center)



def rotate(axis, angle=10.0):
    global M
    x, y, z = center[0], center[1], center[2]

    translate(-x, -y, -z)
    
    if axis == 'x':
        R = ut.matRotateX(np.radians(angle))
        angle_axis[0] += angle
    elif axis == 'y':
        R = ut.matRotateY(np.radians(angle))
        angle_axis[1] += angle
    elif axis == 'z':
        R = ut.matRotateZ(np.radians(angle))
        angle_axis[2] += angle

    M = np.matmul(R,M)

    translate(x, y, z)


def define_cube():
    vertices = np.array([
        # coordinate        color
        -0.5, -0.5, 0.5,    1.0, 0.68, 0.74,
         0.5, -0.5, 0.5,    0.63, 0.91, 0.9,
         0.5,  0.5, 0.5,    0.98, 0.91, 0.78,
        -0.5,  0.5, 0.5,    0.71, 0.97, 0.78,

        -0.5, -0.5, -0.5,   0.63, 0.91, 0.9,
         0.5, -0.5, -0.5,   1.0, 0.68, 0.74,
         0.5,  0.5, -0.5,   0.98, 0.91, 0.78,
        -0.5,  0.5, -0.5,   0.71, 0.97, 0.78,
    ], dtype='float32')

    indices = np.array([
        # Front
        0, 1, 2,    # First Triangle
        2, 3, 0,    # Second Triangle

        # Back
        4, 5, 6,
        6, 7, 4,

        # Left
        0, 3, 7,
        7, 4, 0,

        # Right
        1, 5, 6,
        6, 2, 1,

        # Top
        2, 6, 7,
        7, 3, 2,

        # Bottom
        0, 1, 5,
        5, 4, 0,

    ], dtype="uint32")

    return vertices



def initData(filepath):

    global VAO, box_limits, count_vertices, M, center
    
    file_data = io.read_obj(filepath)

    center = file_data['center']
    [x, y, z] = center 

    print(center)

    box_limits = file_data['vertices']['box']
    vertices = file_data['vertices']['v']
    indices = file_data['faces']['v']
    count_vertices = file_data['faces']['n']

    # Define Initial Matrix
    T = ut.matTranslate(-x, -y, -z)
    M = np.matmul(T,M)

    center[0] -= x
    center[1] -= y
    center[2] -= z


    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertices 
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Elements 
    EBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)
    

    # Set attributes.
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)


    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    # gl.glEnable(gl.GL_CULL_FACE)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)



def initShaders():

    global program
    program = ut.createShaderProgram(vertex_code, fragment_code)


def main(filepath):

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('M E S H')

    initData(filepath)
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(special_keyboard)

    glut.glutMainLoop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath')
    args = parser.parse_args()

    filepath = Path(args.filepath)
    
    if filepath.suffix != '.obj' or not filepath.is_file():
        print('Not a valid .obj file')

    else:
        main(filepath)
