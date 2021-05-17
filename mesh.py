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
from time import time
from PIL import Image

import file_io as io
from Object import Object

# Window size
win_width  = 800
win_height = 800

# Field of view
fovy = np.radians(60)

filepath = None
program = None
line = False
mode = None

objs = []

## Vertex shader.
vertex_code = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 text_coord;

uniform mat4 inverse;
uniform mat4 transform;
uniform mat4 projection;
uniform mat4 view;

uniform vec3 lightPosition;

out vec3 vNormal;
out vec3 fragPosition;
out vec3 LightPos;

out vec2 TexCoord;

void main()
{
    gl_Position = projection * view * transform * vec4(position, 1.0);
    fragPosition = vec3(view * transform * vec4(position, 1.0));
    vNormal = mat3(inverse) * normal;
    LightPos = vec3(view * vec4(lightPosition, 1.0));
    TexCoord = text_coord;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vNormal;
in vec3 fragPosition;
in vec3 LightPos;
in vec2 TexCoord;

out vec4 fragColor;

uniform vec3 objectColor;
uniform vec3 lightColor;
uniform sampler2D ourTexture;

void main()
{
    float ka = 0.5;
    vec3 ambient = ka * lightColor;

    float kd = 0.8;
    vec3 n = normalize(vNormal);
    vec3 l = normalize(LightPos - fragPosition);
    
    float diff = max(dot(n,l), 0.8);
    vec3 diffuse = kd * diff * lightColor;

    float ks = 0.1;
    vec3 v = normalize(-fragPosition);
    vec3 r = reflect(-l, n);

    float spec = pow(max(dot(v, r), 0.0), 8.0);
    vec3 specular = ks * spec * lightColor;

    vec3 light = (ambient + diffuse + specular) * objectColor;
  
    fragColor = vec4(light, 1.0);
    fragColor = texture(ourTexture, TexCoord) * fragColor;

} 
"""

def display():

    light = objs[1]

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(program)
    
    # View
    # [x_max, x_min, y_max, y_min, z_max, z_min] = objs[0].box_limits
    y_max, y_min = objs[0].box_limits[2], objs[0].box_limits[3]

    z_near = (y_max-y_min)*6.0/np.tan(fovy) 
    

    # Projection
    # projection = ut.matOrtho(x_min*1.5, x_max*1.5, y_min*1.5, y_max*1.5, 0.1, 500)
    projection = ut.matPerspective(fovy, win_width/win_height, 0.1, 300)
    loc = gl.glGetUniformLocation(program, "projection")
    gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, projection.transpose())

    # Light color.
    loc = gl.glGetUniformLocation(program, "lightColor")
    gl.glUniform3f(loc, 1.0, 1.0, 1.0)

    # Light position.
    loc = gl.glGetUniformLocation(program, "lightPosition")
    gl.glUniform3f(loc, light.x, light.y, light.z)
    
    for obj in objs:

        gl.glBindVertexArray(obj.VAO)

        # Transformations
        loc = gl.glGetUniformLocation(program, "transform")
        gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, obj.M.transpose())

        view = ut.matTranslate(0.0, 0.0, z_near) 

        loc = gl.glGetUniformLocation(program, "view")
        gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())

        # Adjust Normals
        loc = gl.glGetUniformLocation(program, "inverse")
        gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, np.linalg.inv(view*obj.M).transpose())

        # Object color.
        loc = gl.glGetUniformLocation(program, "objectColor")
        gl.glUniform3f(loc, obj.color[0], obj.color[1], obj.color[2])
        

        # gl.glBindTexture(gl.GL_TEXTURE_2D, obj.VTO)

        # gl.glDrawElements(gl.GL_TRIANGLES, count_vertices, gl.GL_UNSIGNED_INT, None)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, obj.n_vertices)
        gl.glBindVertexArray(0)


    glut.glutSwapBuffers()


def reshape(width,height):
    global win_width, win_height

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


def special_keyboard(key, mouse_x, mouse_y):
    handle_transform(key)


def keyboard(key, mouse_x, mouse_y):
    
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
    obj = objs[0]
    x_max, y_max, z_max = obj.box_limits[1], obj.box_limits[3], obj.box_limits[5]
    unit = 0.01*max(x_max, y_max, z_max)

    if mode == 'translate':
        if key_pressed ==  glut.GLUT_KEY_UP:
            obj.translate(0.0, unit, 0.0)
        elif key_pressed == glut.GLUT_KEY_DOWN:
            obj.translate(0.0, -unit, 0.0)
        elif key_pressed == glut.GLUT_KEY_RIGHT:
            obj.translate(unit, 0.0, 0.0)
        elif key_pressed == glut.GLUT_KEY_LEFT:
            obj.translate(-unit, 0.0, 0.0)
        elif key_pressed == b'a':
            obj.translate(0.0, 0.0, unit)
        elif key_pressed == b'd':
            obj.translate(0.0, 0.0, -unit)

    elif mode == 'rotate':
        angle = 1.0
        if key_pressed == glut.GLUT_KEY_UP:
            obj.rotate('x', angle)
        elif key_pressed == glut.GLUT_KEY_DOWN:
            obj.rotate('x', -angle)
        elif key_pressed == glut.GLUT_KEY_RIGHT:
            obj.rotate('y', angle)
        elif key_pressed == glut.GLUT_KEY_LEFT:
            obj.rotate('y', -angle)
        elif key_pressed == b'a':
            obj.rotate('z', angle)
        elif key_pressed == b'd':
            obj.rotate('z', -angle)
    
    elif mode == 'scale':
        coeff=0.01

        if key_pressed == glut.GLUT_KEY_UP:
            obj.scale(1, 1+coeff, 1)
        elif key_pressed == glut.GLUT_KEY_DOWN:
            obj.scale(1, 1-coeff, 1)
        elif key_pressed == glut.GLUT_KEY_RIGHT:
            obj.scale(1+coeff, 1, 1)
        elif key_pressed == glut.GLUT_KEY_LEFT:
            obj.scale(1-coeff, 1, 1)
        elif key_pressed == b'a':
            obj.scale(1, 1, 1+coeff)
        elif key_pressed == b'd':
            obj.scale(1, 1, 1-coeff)

    glut.glutPostRedisplay()


def idle():
    global objs

    light = objs[1]

    x = 2*np.sin(time())
    z = 2*np.cos(time())

    light.translate(x-light.x, 0, z-light.z)
    glut.glutPostRedisplay()


def initData(filepath):

    global objs
    
    obj_data = io.read_obj(filepath)
    light_data = io.read_obj("files/octaedro.obj")

    obj = Object(obj_data, 0.7, 0.2, 0.2)
    light = Object(light_data, 0.2, 0.2, 0.9)

    castle_txt = texture("texture/castle.jpg")
    blob_txt = texture("texture/blob.png")

    obj.init_data(castle_txt)
    light.init_data(blob_txt)

    objs = [obj, light]

    # Place objects in center
    obj.translate(-obj.x, -obj.y, -obj.z)
    light.translate(-light.x, 0.5-light.y, -light.z)
    light.scale(0.3, 0.3, 0.3)

    
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)


    ###############################################################
    # Texture Parameters
    # VTO = gl.glGenTextures(1)
    # gl.glBindTexture(gl.GL_TEXTURE_2D, VTO)
    
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)	
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, im_width, im_height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, data)
    # gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    ################################################################

    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)


def texture(filename):

    with Image.open(filename) as im:
        v = np.asarray(im, dtype='float32')
        im_with = im.width
        im_heigh = im.height

    return {'data':v, 'height':im_heigh, 'width':im_with } 


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
    glut.glutIdleFunc(idle)

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
