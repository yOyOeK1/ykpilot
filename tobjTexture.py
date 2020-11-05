# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time

# IMPORT OBJECT LOADER
from tobjload import *

pygame.init()
viewport = (800,600)
hx = viewport[0]/2
hy = viewport[1]/2
srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9, 1.0))
glEnable(GL_LIGHT0)
glEnable(GL_LIGHTING)
glEnable(GL_COLOR_MATERIAL)
glEnable(GL_DEPTH_TEST)
glShadeModel(GL_SMOOTH)           # most obj files expect to be smooth-shaded

# LOAD OBJECT AFTER PYGAME INIT
#obj = OBJ(sys.argv[1], swapyz=False)
objB = OBJ("./3dModels/boat2_3dex_boat.obj", swapyz=False)
objM = OBJ("./3dModels/boat2_3dex_sailMain_sailup_onPower.obj", swapyz=False)
objG = OBJ("./3dModels/boat2_3dex_sailGenoa_onPower.obj", swapyz=False)
objR = OBJ("./3dModels/boat2_3dex_ruder.obj", swapyz=False)

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
width, height = viewport
gluPerspective(90.0, width/float(height), 1, 100.0)
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

rx, ry = (0,0)
tx, ty = (0,0)
zpos = 5
rotate = move = False
while 1:
    #clock.tick(30)
    time.sleep(1.0/30.0)
    for e in pygame.event.get():
        if e.type == QUIT:
            sys.exit()
        elif e.type == KEYDOWN and e.key == K_ESCAPE:
            sys.exit()
        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 4: zpos = max(1, zpos-1)
            elif e.button == 5: zpos += 1
            elif e.button == 1: rotate = True
            elif e.button == 3: move = True
        elif e.type == MOUSEBUTTONUP:
            if e.button == 1: rotate = False
            elif e.button == 3: move = False
        elif e.type == MOUSEMOTION:
            i, j = e.rel
            if rotate:
                rx += i
                ry += j
            if move:
                tx += i
                ty -= j
            move = True
        
    if move or rotate:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # RENDER OBJECT
        glTranslate(tx/20., ty/20., - zpos)
        glRotate(ry, 1, 0, 0)
        glRotate(rx, 0, 1, 0)
        glCallList(objB.gl_list)
        
        glCallList(objM.gl_list)
        
        glCallList(objG.gl_list)
        
        glCallList(objR.gl_list)
        pygame.display.flip()
