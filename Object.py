import OpenGL.GL as gl
import OpenGL.GLUT as glut
from ctypes import c_void_p
import numpy as np
import utils as ut

class Object:

  def __init__(self, file_data, color_r, color_g, color_b):
    self.n_vertices = len(file_data['vertex'])
    self.box_limits = file_data['bbox']
    # self.vertex = file_data['vertex']
    self.vertex_position = file_data['v']
    self.vertex_normal = file_data['n']
    self.vertex_faces = file_data['f']

    self.normal_flag = file_data['normal_data']
    
    self.x = file_data['center'][0]
    self.y = file_data['center'][1]
    self.z = file_data['center'][2]

    self.M = np.identity(4, dtype='float32')
    self.color = [color_r, color_g, color_b]
    self.angle_axis = [0, 0, 0]

    self.VAO = None
    self.VBO = None
    self.VTO = None



  def init_data(self, txt_data=None):

    # texture_height = txt_data['height']
    # texture_width = txt_data['width']
    # texture_array = txt_data['data']

    # Vertex array.
    self.VAO = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(self.VAO)

    # Vertices 
    self.VBO = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.VBO)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertex_position.nbytes, self.vertex_position, gl.GL_STATIC_DRAW)

    ### Set attributes

    if self.normal_flag:
      # Position
      gl.glEnableVertexAttribArray(0)
      gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*self.vertex_position.itemsize, None)
      # Normal
      gl.glEnableVertexAttribArray(1)
      gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6*self.vertex_position.itemsize, c_void_p(3*self.vertex_position.itemsize))
 
    else:
      # Position
      gl.glEnableVertexAttribArray(0)
      gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)


    # Texture
    # gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
    # gl.glEnableVertexAttribArray(2)

    # self.VTO = gl.glGenTextures(1)

    # gl.glBindTexture(gl.GL_TEXTURE_2D, self.VTO)
    
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)	
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, texture_width, texture_height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, texture_array)
    # gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    gl.glBindVertexArray(0)


  def set_texture(self, txt_data):

    height = txt_data['height']
    width = txt_data['width']
    array = txt_data['data']

    self.VTO = gl.glGenTextures(1)

    gl.glBindVertexArray(self.VAO)
    gl.glBindTexture(gl.GL_TEXTURE_2D, self.VTO)
    
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)	
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, array)
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)


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


  def build_vertex_array(positions, faces, normals, texture):
    vertex_pos = list()

    if len(normals) > 0:
        for v, n in zip(faces['v'], faces['n']):
            vertex_pos.append(positions[v])
            vertex_pos.append(normals[n])

    else:
        for v in faces['v']:
            vertex_pos.append(positions[v])


    return np.asarray(vertex_pos, dtype='float32')