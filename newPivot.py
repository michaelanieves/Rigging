import pymel.core as pm

'''
Usage:
   set_newPivot()
'''   

# Match the pivot of the target obects to the selected source object    
def set_newPivot(*args):
    sel = pm.ls(sl=True)
    source = sel[-1]
    piv = pm.xform (source, piv=True, q=True, ws=True)
    
    for obj in sel[:-1]:
        pm.xform (obj, ws=True, piv=(piv[0], piv[1], piv[2]) )