from pathlib import Path
from Texture import Texture
import OpenGL.GL as gl

class Cubemap:
  def __init__(self):
    self.faces = dict()
    self.VTO = None

  def load(self, dirpath):
    files = sorted(Path(dirpath).iterdir())

    for i in range(6):
      face = Texture()
      face.load(files[i])

      self.faces[gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i] = face


  def create(self):
    self.VTO = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.VTO)

    for i in range(6):
      face = self.faces[gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i]
      gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB, face.width, face.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, face.data)

    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)  