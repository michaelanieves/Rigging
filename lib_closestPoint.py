#!/usr/bin/env python
"""
.. module:: lib_closestPoint
    :platform: Maya
    :synopsis: Functions relating to getting the closest point on objects
    :plans: Need many many more functions
"""
__author__ = "Andres Weber"
__email__ = "andresmweber@gmail.com"
__version__ = 1.0
__contributor__ = "Michael A Nieves"

import pymel.core as pm
import math
import pprint

def locators_on_closest_point_sets():
    """ Helper function that overlays locators onto selection
        Last thing selected is the target object
    Args:
        None
    Returns: None
    Usage:
        locators_on_closest_point_sets()
    """
    point_data = get_closest_point_sets(pm.ls(sl=True, fl=True)[:-1], pm.ls(sl=True)[-1])
    for transform in point_data:
        loc = pm.spaceLocator()
        loc.t.set(point_data[transform]['component_pos'])

def get_closest_point_sets(transforms, target, fill_keys=False):
    """
    Args:
        transforms [pm.nt.Transform]: list of transforms to query for (can be components)
        target (pm.nt.Transform): the mesh transform to query
        fill_keys (bool): will fill all default keys with None if not found
    Returns (dict):
        dictionary of results paired with the arg transforms, keys include:
            'result', 'position', 'component', 'normal',
            'parameterU', 'parameterV', 'closestFaceIndex'
        will contain None if incorrect type or doesn't exist
    Usage:
        get_closest_point_sets(pm.ls(sl=True, fl=True)[:-1], pm.ls(sl=True)[-1])
    """
    # Query and receive all mesh components on target mesh
    cnode = None
    shape = target.getShape()
    type = shape.type()
    sets = {}
    
    if type=="mesh":
        cnode = pm.shadingNode('closestPointOnMesh', asUtility=True)
        shape.worldMesh[0].connect(cnode.inMesh)
        target.worldMatrix[0].connect(cnode.inputMatrix)
        
    elif type=="nurbsCurve":
        cnode = pm.shadingNode('closestPointOnCurve', asUtility=True)
        shape.worldSpace.connect(cnode.inCurve)
        
    elif type=="nurbsSurface":
        cnode = pm.shadingNode('closestPointOnSurface', asUtility=True)
        shape.worldSpace.connect(cnode.inputSurface)
        
    else:
        pm.error( "Mesh of type: %s is currently not supported" % shape.type() )
    
    # Now store all data found in a dictionary, raw data is result and can query the rest
    for transform in transforms:
        entry, position = {}, (0,0,0)
        # If it's a transform we definitely want rotate pivot, otherwise it'll be a component
        if isinstance(transform, pm.nodetypes.Transform):
            position = pm.xform(transform, ws=True, q=True, rp=True)
        else:
            position = pm.xform(transform, ws=True, q=True, t=True)
            
        cnode.inPosition.set(position)
        attrs = ['result', 'position', 'component', 'component_pos', 'normal',
                 'parameterU', 'parameterV', 'closestVertexIndex', 'closestFaceIndex']
        for attr in attrs:
            try:
                entry[attr] =  cnode.attr(attr).get()
            except:
                if fill_keys:
                    entry[attr] = None
        # Add the component as well
        entry['component'] = get_closest_components([entry['position']], shape)[0]
        entry['component_pos'] = pm.xform(entry['component'], q=True, ws=True, t=True)
        
        sets[transform]=entry
    
    # Cleanup
    pm.delete(cnode)
    return sets

def get_closest_components(positions, shape):
    """ Gets closest CVs to a list of positions as a non-repeating list of CVs
    Args:
        positions [tuple]: list of tuples for position
        transform (pm.nt.NurbsCurve or pm.nt.NurbsSurface): target transform with shape of either nurbsCurve or nurbsSurface
    Returns [pm.nt.ControlPoint]: list of CVs that are closest
    """
    closest_components=[]
    for position in positions:
        closest_component, dist, components = None, 10000000000, []
        # Compare to all existing mesh CVs in turn and compute closest CV
        if shape.type() in ['nurbsCurve','nurbsSurface']:
            components = shape.cv[:]
        else:
            components = shape.vtx[:]
        for component in components:
            dist_bet = distanceBetween( pm.xform(component, q=True, ws=True, t=True), position)
            if  dist_bet < dist:
                dist = dist_bet
                closest_component = component
        if closest_component:
            closest_components.append(closest_component)
    # Return result with dulicates removed
    return list(set(closest_components))
        
def distanceBetween(p1, p2):
    """ Gets the distance between two points
    Args:
        p1 (tuple): spatial coordinate
        p1 (tuple): spatial coordinate
    Returns: (float): distance between the points
    """
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    xd = x2-x1
    yd = y2-y1
    zd = z2-z1
    return math.sqrt(xd*xd + yd*yd + zd*zd)