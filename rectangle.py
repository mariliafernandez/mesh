#!/usr/bin/env python3

import sys
import ctypes
import numpy as np
import OpenGL.GL as gl
import OpenGL.GLUT as glut
sys.path.append('../lib/')
import utils as ut
from ctypes import c_void_p

win_width  = 800
win_height = 600

program = None
VAO = None

M = np.identity(4, dtype='float32')

## Vertex shader.
vertex_code = """
#version 330 core
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

out vec3 vColor;

uniform mat4 transform;

void main()
{
    gl_Position = transform * vec4(position, 1.0);
    vColor = color;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(vColor, 1.0f);
} 
"""

# Draws primitive.
def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)

    loc = gl.glGetUniformLocation(program, "transform")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, M.transpose())

    gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)

    glut.glutSwapBuffers()



# @param width New window width.
# @param height New window height.
def reshape(width,height):

    win_width = width
    win_height = height
    gl.glViewport(0, 0, width, height)
    glut.glutPostRedisplay()


def mouse(btn, state, x, y):
    #  Does not work 
    if btn == 3:    # Zoom in
        translate(0.0, 0.0, -0.05)
    elif btn == 4:    # Zoom out
        translate(0.0, 0.0, 0.05)



 global type_primitive

    if key == b'1':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    elif key == b'2':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):
    ## Transformations

    # Translate
    elif key == b'a':   # Left
        translate(-0.05, 0.0, 0.0)
    elif key == b'd':   # Right
        translate(0.05, 0.0, 0.0)
    elif key == b'w':   # Up
        translate(0.0, 0.05, 0.0)
    elif key == b's':   # Down
        translate(0.0, -0.05, 0.0)
    
    # Rotate
    elif key == b'x':
        rotate('x')
    elif key == b'y':
        rotate('y')
    elif key == b'z':
        rotate('z')

    # Scale
    elif key == b'+':
        scale(1.05, 1.05, 1.05)
    elif key == b'-':
        scale(0.95, 0.95, 0.95)

    glut.glutPostRedisplay()


def translate(x, y, z):
    global M

    T = ut.matTranslate(x, y, z)

    M = np.matmul(T,M)
    glut.glutPostRedisplay()


def scale(x, y, z):
    global M

    S = ut.matScale(x, y, z)

    M = np.matmul(S,M)
    glut.glutPostRedisplay()


def rotate(move, angle=90.0):
    global M

    if move == 'x':
        R = ut.matRotateX(np.radians(angle))
    elif move == 'y':
        R = ut.matRotateY(np.radians(angle))
    elif move == 'z':
        R = ut.matRotateZ(np.radians(angle))

    M = np.matmul(R,M)
    glut.glutPostRedisplay()



def initData():

    global VAO

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
    
    # Vertex array.
    VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(VAO)

    # Vertex buffer
    VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    
    # Element Buffer Object 
    EBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, EBO)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)
    
    # Set attributes.
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, None)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*vertices.itemsize, c_void_p(3*vertices.itemsize))
    gl.glEnableVertexAttribArray(1)
    
    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)


def initShaders():

    global program

    program = ut.createShaderProgram(vertex_code, fragment_code)


def main():

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Cube')

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)

    initData()
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutMouseFunc(mouse)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
