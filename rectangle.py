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

## Vertex array object.
VAO = None

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

## Drawing function.
#
# Draws primitive.
def display():

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    gl.glBindVertexArray(VAO)

    # Translation
    T = ut.matTranslate(-0.5, 0.5, 0.0)

    # Rotation around z
    Rz = ut.matRotateX(np.radians(30.0))

    # Scale.
    S = ut.matScale(1.0, 1.0, 1.0)

    # M = T*R*S
    M = np.matmul(Rz,S)
    M = np.matmul(T,M)

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



# @param key Pressed key.
# @param x Mouse x coordinate when key pressed.
# @param y Mouse y coordinate when key pressed.
def keyboard(key, x, y):

    global type_primitive

    if key == b'\x1b'or key == b'q':
        sys.exit( )
    if key == b'1':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    if key == b'2':
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    glut.glutPostRedisplay()


# Defines the coordinates for vertices, creates the arrays for OpenGL.
def initData():

    # Uses vertex arrays.
    global VAO

 # Set vertices.
    vertices = np.array([
        # coordinate     color
        -0.5, -0.5, 0.5, 1.0, 0.0, 0.0,
         0.5, -0.5, 0.5, 0.0, 1.0, 0.0,
         0.5,  0.5, 0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5, 0.5, 1.0, 0.0, 0.0,

        -0.5, -0.5, -0.5, 1.0, 0.0, 0.0,
         0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
         0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5, -0.5, 1.0, 0.0, 0.0,
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



# Compile shaders and create programs
def initShaders():

    global program

    program = ut.createShaderProgram(vertex_code, fragment_code)


# Init GLUT and the window settings. Also, defines the callback functions used in the program
def main():

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('Cube')

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)

    # Init vertex data for the cube
    initData()
    
    # Create shaders
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)

    glut.glutMainLoop()

if __name__ == '__main__':
    main()
