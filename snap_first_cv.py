#!/usr/bin/env python
"""
    :module: snap_first_cv
    :platform: Maya
    :synopsis: This module snaps selected objects to the closest point on the last selection
    :plans: None
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm
import Rigging.lib_closestPoint as lib_cp

#lib_cp.get_closest_point_sets(pm.ls(sl=True, fl=True)[:-1], pm.ls(sl=True)[-1])
#lib_cp.locators_on_closest_point_sets()

def snap_first_cv(transforms, target_mesh_transform):
    """ Helper function that overlays locators onto selection
    Args:
        transforms [pm.nt.Transform]: a transform with a nurbsCurve shape node under it
        target_mesh_transform (pm.nt.Transform): target mesh to query positions
    Returns: None
    Usage:
        snap_first_cv(pm.ls(sl=True, fl=True)[:-1], pm.ls(sl=True)[-1])
    """
    first_cvs = [transform.getShape().cv[0] for transform in transforms]
    point_data = lib_cp.get_closest_point_sets(first_cvs, target_mesh_transform)
    for first_cv in point_data:
        pm.xform( first_cv, a=True, ws=True, t=point_data[first_cv]['position']) # surface
        #pm.xform( first_cv, a=True, ws=True, t=point_data[first_cv]['component_pos']) # component
