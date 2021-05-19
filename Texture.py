from pathlib import Path
from PIL import Image
import numpy as np
import OpenGL.GL as gl

class Texture:
  def __init__(self):
    self.height = None
    self.width = None
    self.data = None
    self.VTO = None
    self.filename = None
  
  
  def load(self, filepath):

    with Image.open(filepath) as im:
      if im.width % 4 != 0:
        w = im.width-(im.width%4)
        area = (0,0,w,w)
        im = im.crop(area)
      
      if im.width != im.height:
        w = im.width
        area = (0,0,w,w)
        im = im.crop(area)

      self.data = np.asarray(im, dtype='uint8')
      self.width = im.width
      self.height = im.height
      self.filename = Path(filepath).name

  def create(self):
    self.VTO = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.VTO)

    for i in range(6):
      gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB, self.width, self.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, self.data)

    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)  