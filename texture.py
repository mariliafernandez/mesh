from PIL import Image
import numpy as np

filename = "texture/castle.jpg"

with Image.open(filename) as im:
  a = np.asarray(im)

print(a)