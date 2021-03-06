#!/usr/bin/env python3

from Cubemap import Cubemap
import sys
import ctypes
from typing import Text
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
from Texture import Texture
from Cubemap import Cubemap

# Window size
win_width  = 800
win_height = 800

# Field of view
fovy = np.radians(60)

filepath = None
program = None
line = False
mode = None

texture_on = True
light_on = True

objs = []

## Vertex shader.
vertex_code = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;

uniform mat4 inverse;
uniform mat4 transform;
uniform mat4 projection;
uniform mat4 view;

uniform vec3 lightPosition;

out vec3 vNormal;
out vec3 fragPosition;
out vec3 LightPos;
out vec3 TexCoords;

void main()
{
    gl_Position = projection * view * transform * vec4(position, 1.0);
    fragPosition = vec3(view * transform * vec4(position, 1.0));
    vNormal = mat3(inverse) * normal;
    LightPos = vec3(view * vec4(lightPosition, 1.0));
    TexCoords = position;
}
"""

## Fragment shader.
fragment_code = """
#version 330 core

in vec3 vNormal;
in vec3 fragPosition;
in vec3 LightPos;
in vec3 TexCoords;

out vec4 fragColor;

uniform vec3 objectColor;
uniform vec3 lightColor;
uniform samplerCube cubemap;
uniform bool light_mode;
uniform bool texture_mode;

void main()
{
    float ka = 0.9;
    vec3 ambient = ka * lightColor;

    float kd = 0.6;
    vec3 n = normalize(vNormal);
    vec3 l = normalize(LightPos - fragPosition);
    
    float diff = max(dot(n,l), 0.0);
    vec3 diffuse = kd * diff * lightColor;

    float ks = 0.9;
    vec3 v = normalize(-fragPosition);
    vec3 r = reflect(-l, n);

    float spec = pow(max(dot(v, r), 0.0), 4.0);
    vec3 specular = ks * spec * lightColor;

    fragColor = vec4(objectColor, 1.0);

    if(light_mode) {
        vec3 light = (ambient + diffuse + specular) * objectColor;
        fragColor = vec4(light, 1.0);
    }

    if(texture_mode) {
        fragColor = texture(cubemap, TexCoords) * fragColor;
    }
    
} 
"""

def display():

    global light_on

    light = objs[1]

    gl.glClearColor(0.2, 0.3, 0.3, 1.0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # gl.glDepthMask(gl.GL_FALSE)
    gl.glUseProgram(program)
    
    # View
    # [x_max, x_min, y_max, y_min, z_max, z_min] = objs[0].box_limits
    y_max, y_min = objs[0].box_limits[2], objs[0].box_limits[3]

    z_near = (y_max-y_min)*5.0/np.tan(fovy) 
    

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
    # gl.glUniform3f(loc, 0.0, 0.0, 0.0)

    
    for obj in objs:

        gl.glBindVertexArray(obj.VAO)

        # Transformations
        loc = gl.glGetUniformLocation(program, "transform")
        gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, obj.M.transpose())

        # print(obj.M)

        view = ut.matTranslate(0.0, 0.0, z_near) 

        loc = gl.glGetUniformLocation(program, "view")
        gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, view.transpose())

        # Adjust Normals
        loc = gl.glGetUniformLocation(program, "inverse")
        # gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, np.linalg.inv(obj.M).transpose())
        gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, np.matmul(view, obj.M).transpose())


        # Object color.
        loc = gl.glGetUniformLocation(program, "objectColor")
        gl.glUniform3f(loc, obj.color[0], obj.color[1], obj.color[2])


        loc_light = gl.glGetUniformLocation(program, "light_mode")
        loc_tex = gl.glGetUniformLocation(program, "texture_mode")
        
        if light_on:
            gl.glUniform1f(loc_light, True)
        else:
            gl.glUniform1f(loc_light, False)

        if texture_on:
            light_on = True
            gl.glUniform1f(loc_tex, True)
            gl.glUniform1f(loc_light, True)

        else:
            gl.glUniform1f(loc_tex, False)

        
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, obj.texture.VTO)

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
    
    global type_primitive, line, mode, texture_on, light_on
    
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

    elif key == b'1':
        print(f'lights {light_on}')
        light_on = not light_on
        print(f'lights {light_on}')

    elif key == b'2':
        texture_on = not texture_on
        print('texture')

    else:
        # print(key)
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

    x = 2*np.sin(time()/4)
    z = 2*np.cos(time()/4)

    light.translate(x-light.x, 0, z-light.z)
    objs[0].rotate('y', -0.02)
    objs[1].rotate('y', 0.09)
    objs[2].rotate('z', 0.03)

    glut.glutPostRedisplay()


def initData(filepath=None, texpath=None):
    global objs

    if not filepath:
        filepath=Path("files/sphere.obj")
    if not texpath:
        texpath=Path("texture/earth")

    
    obj_data = io.read_obj(filepath)
    sphere = io.read_obj("files/sphere.obj")
    # cube_data = io.read_obj("files/cube.obj")

    obj = Object(obj_data, [1.0, 1.0, 1.0])
    light = Object(sphere, [1.0, 1.0, 1.0])
    sky = Object(sphere, [0.8, 0.8, 0.8])

    if Path(texpath).is_dir():
        obj_tex = Cubemap()
    else:
        obj_tex = Texture()

    obj_tex.load(Path(texpath))
    
    stars = Texture()
    stars.load("texture/milky_way.jpg")

    moon = Texture()
    moon.load("texture/moon.jpg")


    # for key in earth.faces:
        # print(f'{key}: {earth.faces[key].filename}')

    sky.create(stars)
    obj.create(obj_tex)
    # obj.create()

    light.create(moon)

    objs = [obj, light, sky]
    # objs = [obj, light]


    # Place objects in center
    light.translate(-light.x, -light.y, -light.z)
    obj.translate(-obj.x, -obj.y, -obj.z)
    sky.translate(-sky.x, -sky.y, -sky.z-1)
    
    light.scale(0.1, 0.1, 0.1)
    sky.scale(10,10,10)
    
    sky.rotate('y', 145)

    
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)

    # Unbind Vertex Array Object.
    gl.glBindVertexArray(0)



def initShaders():

    global program
    program = ut.createShaderProgram(vertex_code, fragment_code)


def main(filepath, texpath):

    glut.glutInit()
    glut.glutInitContextVersion(3, 3)
    glut.glutInitContextProfile(glut.GLUT_CORE_PROFILE)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(win_width,win_height)
    glut.glutCreateWindow('M E S H')

    initData(filepath, texpath)
    initShaders()

    glut.glutReshapeFunc(reshape)
    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(special_keyboard)
    glut.glutIdleFunc(idle)

    glut.glutMainLoop()


if __name__ == '__main__':
    filepath = None
    texpath = None

    parser = argparse.ArgumentParser()

    parser.add_argument('--obj')
    parser.add_argument('--texture')
    
    args = parser.parse_args()

    if args.texture:
        texpath = Path(args.texture)
    else:
        main(filepath, texpath)
    
    if args.obj:
        filepath = Path(args.obj)
        if filepath.suffix != '.obj' or not filepath.is_file():
            print('Not a valid .obj file')

    
