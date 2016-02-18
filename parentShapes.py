import pymel.core as pm

'''
Usage:
   parentShapes()
'''   

# Match the pivot of the target obects to the selected source object    
def parentShapes(*args):
    sel = pm.ls(sl=True)
    newParent = sel[-1]
    parentShapes = pm.listRelatives( newParent, shapes = True )
    
    pm.rename( parentShapes, newParent + 'Shape' )
    pm.makeIdentity( newParent, apply = True, translate = True, rotate = True, scale = True )
    
    for obj in sel[:-1]:
        pm.parent( obj, w = True )
        # freeze transforms
        pm.makeIdentity( obj, apply = True, translate = True, rotate = True, scale = True )
        # Get Shapes
        getShapes = pm.listRelatives( obj, shapes = True )
        # Parent shapes to newParent object
        pm.parent( getShapes, newParent, r = True, s = True )
        pm.rename( getShapes, newParent + 'Shape')
        #remove unused transform
        pm.delete( obj )