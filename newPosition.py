import pymel.core as pm

'''
Usage:
   set_newPosition()
'''   

# Match the position of the target obects to the selected source object    
def set_newPosition(*args):
    sel = pm.ls(sl=True)
    source = sel[-1]
    
    for obj in sel[:-1]:
        tempConst = pm.parentConstraint(source, obj, name ='tempConst')
        pm.delete(tempConst)

        

