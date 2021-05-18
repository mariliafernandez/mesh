from PIL import Image
import numpy as np

class Texture:
  def __init__(self):
    self.height = None
    self.width = None
    self.data = None
    self.VTO = None

  def load(self, filepath):

    with Image.open(filepath) as im:
      if im.width % 4 != 0:
        area = (0,0,im.width-(im.width%4),im.width-(im.width%4))
        im = im.crop(area)

      self.data = np.asarray(im, dtype='uint8')
      self.width = im.width
      self.height = im.height
