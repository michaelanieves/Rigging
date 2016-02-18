import pymel.core as pm

'''
Usage:
   quick_connectTranslateX()
   quick_connectTranslateY()
   quick_connectTranslateZ()
   quick_connectRotateX()
   quick_connectRotateY()
   quick_connectRotateZ()
   quick_connectScaleX()
   quick_connectScaleY()
   quick_connectScaleZ()
   quick_connectVisibiity()
'''   

# Connect translate X of target objects to source object    
def quick_connectTranslateX(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'translateX', obj.translateX, f = True)
        
# Connect translate Y of target objects to source object    
def quick_connectTranslateY(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'translateY', obj.translateY, f = True)
        
# Connect translate Z of target objects to source object    
def quick_connectTranslateZ(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'translateZ', obj.translateZ, f = True)
        
# Connect rotate X of target objects to source object    
def quick_connectRotateX(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'rotateX', obj.rotateX, f = True)
        
# Connect rotate Y of target objects to source object    
def quick_connectRotateY(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'rotateY', obj.rotateY, f = True)
        
# Connect rotate Z of target objects to source object    
def quick_connectRotateZ(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'rotateZ', obj.rotateZ, f = True)
        
# Connect scale X of target objects to source object    
def quick_connectScaleX(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'scaleX', obj.scaleX, f = True)
        
# Connect scale X of target objects to source object    
def quick_connectScaleY(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'scaleY', obj.scaleY, f = True)
        
# Connect scale X of target objects to source object    
def quick_connectScaleZ(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'scaleZ', obj.scaleZ, f = True)
        
# Connect visibility of target objects to source object    
def quick_connectVisibiity(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        source.connectAttr( 'visibility', obj.visibility, f = True)