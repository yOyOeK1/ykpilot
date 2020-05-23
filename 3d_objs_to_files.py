import bpy
import os
import bmesh

desFolder = "./3dModels/"
prefix = ''

fileWPath = bpy.context.blend_data.filepath
file = os.path.basename(fileWPath)
file = file.split(".")[0]
print("file: [%s]"%file)

prefix+= file+"_3dex"


bpy.ops.object.select_all(action='DESELECT')

s = bpy.context.scene

print("--------")
print(s)

print("prefix: [%s]"%prefix)

ff = open(desFolder+prefix+"_files.list", "w")
fo = open(desFolder+prefix+"_objNames.list", "w")


for o in s.objects:
    
    for oo in s.objects:
        oName = o.name
        s.objects.active = oo
        oo.select = False    
    
    
    oName = o.name
    print("obj [%s]"%o.name)

    targetName=prefix+"_"+oName    
    s.objects.active = o
    o.select = True    

    


   
    if o.type == "MESH":
        print("triangulating [%s].... "%oName)
        trian = bmesh.new()
        trian.from_mesh(o.data)
        bmesh.ops.triangulate( trian, faces=trian.faces[:], quad_method=0, ngon_method=0 )
        trian.to_mesh(o.data)
        trian.free()


        print("mesh ready to export...")
  
        bpy.ops.export_scene.obj( filepath=desFolder+targetName+".obj", use_selection=True )
        ff.write(desFolder+targetName+"\n")
        fo.write(desFolder+oName+"\n")    
    
        
        print("error with obj[%s]"%oName)    
    
ff.close()
fo.close()
    
    
