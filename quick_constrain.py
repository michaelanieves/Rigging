import pymel.core as pm

'''
Usage:
   quick_constrainParent()
   quick_constrainParentOffset()
   quick_constrainPoint)
   quick_constrainPointOffset()
   quick_constrainOreint()
   quick_constrainOreintOffset()
   quick_constrainScale()
   quick_constrainScaleOffset()
'''   

# Parent constrain targets to source   
def quick_constrainParent(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.parentConstraint( source, obj, mo = False )
        
# Parent constrain targets to source maintain offset on   
def quick_constrainParentOffset(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.parentConstraint( source, obj, mo = True )

# Point constrain targets to source   
def quick_constrainPoint(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.pointConstraint( source, obj, mo = False )
        
# Point constrain targets to source maintain offset on   
def quick_constrainPointOffset(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.pointConstraint( source, obj, mo = True )
        
# Oreintation constrain targets to source   
def quick_constrainOreint(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.orientConstraint( source, obj )
        
# Oreintation constrain targets to source maintain offset on   
def quick_constrainOreintOffset(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.orientConstraint( source, obj, mo = True )
        
# Scale constrain targets to source   
def quick_constrainScale(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.scaleConstraint( source, obj )
        
# Scale constrain targets to source maintain offset on   
def quick_constrainScaleOffset(*args):
    sel = pm.ls(sl=True)
    source = pm.PyNode(sel[-1])
    
    for obj in sel[:-1]:
        pm.scaleConstraint( source, obj, mo = True )
        
