
from kivy.graphics.opengl import *
from kivy.graphics import * 
from kivy.graphics.texture import Texture
from kivy.core.image import Image
from kivy.core.image import ImageData
from kivy.graphics.context_instructions import BindTexture as bt
from kivy.base import EventLoop
from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from kivy3dgui import canvas3d
from kivy3dgui.objloader import ObjFile
from kivy.clock import Clock
from kivy.core.window import Window
import sys
import math
from kivy3dgui.fbowidget import FboFloatLayout
from kivy.atlas import CoreImage


def magnitude(v):
    return math.sqrt(sum(v[i] * v[i] for i in range(len(v))))

def normalize(v):
    vmag = magnitude(v)
    if vmag == 0:
        vmag = 0.01
    return [v[i] / vmag for i in range(len(v))]

def min_vector(v1, v2):
    return [v1[i] - v2[i] for i, _ in enumerate(v1)]




class D3Helper:
    
    def __init__(self):
        self.objs = []
        
    def getObj(self,objName):
        for o in self.objs:
            if o['name'] == objName:
                return o
        
        return None    
    
    
    def loadObj(self, objs):
        print("load objects ",len(objs))
        
        for io,o in enumerate(objs):
            tao = {}
            tao['name'] = o[0]
            tao['filePath'] = o[1]
            tao['texturePath'] = o[2]
            m = ObjFile(tao['filePath'])
            tao['ol'] = m
            tao['mesh'] = None
            tao['cit'] = ObjectProperty(None)
            
            
            
            #print("doing normalization")
            
            m = list(m.objects.values())[0]
            res = []
            count = 0
            for i, o in enumerate(m.vertices):
                res.append(o)
                if (i + 1) % 8 == 0:
                    count += 1
                    res.append(0.0)
                    res.append(0.0)
                    res.append(0.0)

                    res.append(i // 8)
                    res.append(i // 8)

                    if count >= 3:
                        l = len(res)
                        v0 = [res[l - 13 * 3], res[l - 13 * 3 + 1], res[l - 13 * 3 + 2]]
                        v1 = [res[l - 13 * 2], res[l - 13 * 2 + 1], res[l - 13 * 2 + 2]]
                        v2 = [res[l - 13 * 1], res[l - 13 * 1 + 1], res[l - 13 * 1 + 2]]

                        t0xy = [res[l - 13 * 3 + 6], res[l - 13 * 3 + 7]]
                        t1xy = [res[l - 13 * 2 + 6], res[l - 13 * 2 + 7]]
                        t2xy = [res[l - 13 + 6], res[l - 13 + 7]]

                        edge1 = min_vector(v1, v0)
                        edge2 = min_vector(v2, v0)

                        delta_u1 = t1xy[0] - t0xy[0]
                        delta_v1 = t1xy[1] - t0xy[1]

                        delta_u2 = t2xy[0] - t0xy[0]
                        delta_v2 = t2xy[1] - t0xy[1]

                        d = (delta_u1 * delta_v2 - delta_u2 * delta_v1)
                        if d == 0:
                            d = 0.01
                        f = 1.0 / d;

                        tangent_x = f * (delta_v2 * edge1[0] - delta_v1 * edge2[0])
                        tangent_y = f * (delta_v2 * edge1[1] - delta_v1 * edge2[1])
                        tangent_z = f * (delta_v2 * edge1[2] - delta_v1 * edge2[2])

                        for _i in range(1, 4):
                            res[l - 13 * _i + 8] += tangent_x
                            res[l - 13 * _i + 9] += tangent_y
                            res[l - 13 * _i + 10] += tangent_z

                        count = 0

            for i in range(len(res)):
                if (i + 1) % 13 == 0:
                    vec = [res[i - 12 + 8], res[i - 12 + 9], res[i - 12 + 10]]
                    n_vec = normalize(vec)
                    res[i - 12 + 8] = n_vec[0]
                    res[i - 12 + 9] = n_vec[1]
                    res[i - 12 + 10] = n_vec[2]

            m.vertices = res
            _vertices = m.vertices
            tao['ver'] = _vertices
            _indices = m.indices
            tao['ind'] = _indices
            
            
            
            #print("normalization done")
            
            self.objs.append(tao)
            print(("    %s / %s    ["%(io+1,len(objs)) ),tao['name'],'] DONE')
            

    def set_uniform(self, name, val):
        if True:
            self.canvas[name] = val
        else:
            pass
    
    def makeMesh(self,objName):
        oOrg = self.getObj(objName)
        o = {}
        for k in oOrg.keys():
            o[k] = oOrg[k]
        tp = "makeMesh ["+o['name']+"]"
        
        _vertices = o['ver']
        _indices = o['ind']
        texturePath = o['texturePath']
        tp+= "    texturePath [%s]"%texturePath
            #o['texture'] = img._texture
        
        PushMatrix()
        o['pos'] = Translate(0.1,0.1,0.1)
        o['rot'] = [
            Rotate(0,0,0,1),
            Rotate(0,0,1,0),
            Rotate(0,1,0,0)
            ]
        o['sca'] = Scale(1.0, 1.0, 1.0)
        mesh = Mesh(
            vertices=_vertices,
            indices=_indices,
            fmt=[
               (b'v_pos', 3, 'float'), 
               (b'v_normal', 3, 'float'), 
               (b'v_tc0', 2, 'float'),
               (b'tangent', 3, 'float'), 
               (b'vert_pos', 2, 'float')
                ],
            mode='triangles'
            )
        PopMatrix()
        
        if texturePath == "":
            tp+= "    no texture"
            pass
        else:
            o['cit'] = ObjectProperty(None) 
            o['cit'] = Image(texturePath).texture
            mesh.texture = o['cit']
            tp+="    size [%s]"%str(o['cit'].size)
            
        #self.set_uniform("texture0_enable",True)
        o['mesh'] = mesh
        print(tp)
        return o
    
    