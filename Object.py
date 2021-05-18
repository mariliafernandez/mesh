import OpenGL.GL as gl
import OpenGL.GLUT as glut
from ctypes import c_void_p
import numpy as np
import utils as ut
from pathlib import Path
from PIL import Image

class Object:

  def __init__(self, file_data, color):
    self.file_data = file_data

    self.n_vertices = None
    self.box_limits = file_data['bbox']
    self.vertex_array = None

    self.normal_flag = file_data['normal_data']
    
    self.x = file_data['center'][0]
    self.y = file_data['center'][1]
    self.z = file_data['center'][2]

    self.M = np.identity(4, dtype='float32')
    self.color = color
    self.angle_axis = [0, 0, 0]

    self.texture = None

    self.VAO = None
    self.VBO = None
    self.VTO = None


  def create(self, texture_obj=None):
    self.build_vertex_array()
    self.init_data(texture_obj)


  def init_data(self, texture=None):

    # Vertex array.
    self.VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(self.VAO)


    # Vertices 
    self.VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)

    gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertex_array.nbytes, self.vertex_array, gl.GL_STATIC_DRAW)

    ### Set attributes

    if self.normal_flag:
      # Position
      gl.glEnableVertexAttribArray(0)
      gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*self.vertex_array.itemsize, None)
      # Normal
      gl.glEnableVertexAttribArray(1)
      gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*self.vertex_array.itemsize, c_void_p(3*self.vertex_array.itemsize))
 
    else:
      # Position
      gl.glEnableVertexAttribArray(0)
      gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)


    self.VTO = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.VTO)

    for i in range(6):
      # print(texture)
      gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB, texture.width, texture.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, texture.data)
    
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)  


    gl.glBindVertexArray(0)


  def translate(self, x, y, z):
    T = ut.matTranslate(x, y, z)

    self.M = np.matmul(T, self.M)
      
    self.x += x
    self.y += y
    self.z += z


  def scale(self, x, y, z):
    x_center, y_center, z_center = self.x, self.y, self.z

    self.translate(-x_center, -y_center, -z_center)

    S = ut.matScale(x, y, z)
    self.M = np.matmul(S,self.M)

    self.translate( x_center, y_center, z_center)


  def rotate(self, axis, angle=10.0):
    x, y, z = self.x, self.y, self.z

    self.translate(-x, -y, -z)
      
    if axis == 'x':
      R = ut.matRotateX(np.radians(angle))
      self.angle_axis[0] += angle
    elif axis == 'y':
      R = ut.matRotateY(np.radians(angle))
      self.angle_axis[1] += angle
    elif axis == 'z':
      R = ut.matRotateZ(np.radians(angle))
      self.angle_axis[2] += angle

    self.M = np.matmul(R, self.M)

    self.translate(x, y, z)


  def build_vertex_array(self):
    vertex_list = list()

    vertex_position = self.file_data['v']
    vertex_normal = self.file_data['n']
    vertex_faces = self.file_data['f']

    # Tem normal
    if len(vertex_normal) > 0:

      # vn indexado por face
      if len(vertex_faces['n']) > 0:
        for v, n in zip(vertex_faces['v'], vertex_faces['n']):
          vertex_list.append(vertex_position[v])
          vertex_list.append(vertex_normal[n])

        self.n_vertices = len(vertex_faces['v']*3)
        

      # um vn por vértice
      else:
        for v, n in zip(vertex_position, vertex_normal):
          vertex_list.append(v)
          vertex_list.append(n) 

        self.n_vertices = len(vertex_position)

    # Não tem normal
    else:
      for v in vertex_faces['v']:
        vertex_list.append(vertex_position[v])

      self.n_vertices = len(vertex_list)

    self.vertex_array = np.asarray(vertex_list, dtype='float32').flatten()

