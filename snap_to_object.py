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

def snap_object(transforms, target_mesh_transform):
    """ Helper function that overlays locators onto selection
    Args:
        transforms [pm.nt.Transform]: a transform with a nurbsCurve shape node under it
        target_mesh_transform (pm.nt.Transform): target mesh to query positions
    Returns: None
    Usage:
        snap_object(pm.ls(sl=True, fl=True)[:-1], pm.ls(sl=True)[-1])
    """
    point_data = lib_cp.get_closest_point_sets(transforms, target_mesh_transform)
    for transform in point_data:
        pm.move (transform, point_data[transform]['position'], rpr=True)
