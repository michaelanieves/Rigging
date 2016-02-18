import maya.cmds as pm

def center_pivot_each(transforms):
    """ Centers pivot on transforms
    Args:
        transforms (pm.nt.Transform): list of transforms to modify
    Returns (None)
    Usage:
        center_piviot_each(pm.ls(sl=True))
    """
    for transform in transforms:
        pm.CenterPivot(transform)