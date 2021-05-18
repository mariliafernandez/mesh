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
        w = im.width-(im.width%4)
        area = (0,0,w,w)
        im = im.crop(area)
      
      if im.width != im.height:
        w = im.width
        area = (0,0,w,w)
        im = im.crop(area)

      print(im.width)
      print(im.height)
      self.data = np.asarray(im, dtype='uint8')
      self.width = im.width
      self.height = im.height
