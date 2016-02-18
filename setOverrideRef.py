import pymel.core as pm

'''
Usage:
   set_overrideRef()
'''   

# Match the pivot of the target obects to the selected source object    
def set_overrideRef():
    sel = pm.ls(sl=True)

    for obj in sel:
        obj.overrideEnabled.set(True)
        obj.overrideDisplayType.set(2)
