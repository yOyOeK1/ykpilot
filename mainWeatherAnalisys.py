#!/usr/bin/env python3


from TimeHelper import *
import os
import time
import numpy as np
from PIL import Image, ImageSequence

fileKey = "wRadar_XXX.gif"
rangeColors = {}

if __name__ == "__main__":
	img = Image.open('wRadar_2020_05_10_10_59_29.gif')
	frames = np.array([np.array(frame.copy().convert('RGB').getdata(),dtype=np.uint8).reshape(frame.size[1],frame.size[0],3) for frame in ImageSequence.Iterator(img)])
	
	#print(frames)
	print("size ",len(frames)," x ",len(frames[0]),' Y ', len(frames[0][0]),' c ',len(frames[0][0][0]) )
	#[0][y][x]
	#print(frames[0][238][123])

	for y in range(0,470,1):
		x = 38
		pixel = str(frames[0][y][x])
		try:
			rangeColors[pixel]
		except:
			rangeColors[pixel] = 1

	print('colors found ',len(rangeColors))
	new_im = Image.fromarray(frames[0])
	new_im.show()		