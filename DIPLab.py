# from PIL import Image
# import numpy as np

# img = Image.open("images.mandril.bmp")

# data = np.array(img)

# width = data.shape(0)
# height = data.shape(1)

# mode_to_bpp = {"1":1,"L":8,"P":8,"RGB":24,"RGBA":32,"CMYK":32,"YCbCr":24,"LAB":24,"HSV":24,"I":32,"F":32}
# bitDepth = mode_to_bpp[img.mode]

# print("Image %s with %s x %s pixels (%s bits per pixels) has been read!" % (img.file-name, width, height, bitDepth))

# fo = "images/out.bmp"

# try:
#     img.save(fo)
# except: 
#     print("Write file error")
# else:
#     print("Image %s has been written!" % (fo))
    
from ImageManager import ImageManager

im = ImageManager()

im.read("images/mandril.bmp")
# im.read("images/gamemaster_noise_2024.bmp")

# Quest 006
# im.medianFilter(3)
# im.write("images/mandrilmedian3.bmp")
# im.restoreToOriginal()
# im.medianFilter(7)
# im.write("images/mandrilmedian7.bmp")
# im.restoreToOriginal()
# im.medianFilter(15)
# im.write("images/mandrilmedian15.bmp")
# im.restoreToOriginal()

# Quest 007
im.unsharpFilter(3, 1)
im.write("images/mandrilunsharp3.bmp")