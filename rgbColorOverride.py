import pymel.core as pm

'''
Usage:
   rgbColorOverride()
'''   

def rgbColorOverride(*args):
    """ This function can open a rgb color picker and assign a chosen color to the drawing override color of selected obects
    Args:
        None
    Returns (None)
    """
    sel = pm.ls(sl=True)
    
    pm.colorEditor()
    if pm.colorEditor(query=True, result=True):
        rgb = pm.colorEditor(query=True, rgb=True)
        hsv = pm.colorEditor(query=True, hsv=True)
        alpha = pm.colorEditor(query=True, alpha=True)
    else:
        print 'Editor was dismissed'
    
    for obj in sel:
        for shape in obj.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideRGBColors.set(1)
            shape.overrideColorRGB.set( rgb[0], rgb[1], rgb[2])