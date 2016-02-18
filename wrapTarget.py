#!/usr/bin/env python
"""
    :module: wrapTarget
    :platform: Maya
    :synopsis: This module has the nessacery components to wrap the target mesh to the source mesh using a standard maya wrap deformer
    :plans: None
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm


def wrap_target(target, source, **kwargs):
    """ This function will use a wrap deformer to wrap the target mesh to the source mesh
    Args:
        None
    Returns (pm.nt.Wrap): generated wrap node
    """
    targetShape = target.getShape()
    sourceShape = source.getShape()
 
    #create wrap deformer
    weightThreshold = kwargs.get('weightThreshold',0.0)
    maxDistance = kwargs.get('maxDistance',1.0)
    exclusiveBind = kwargs.get('exclusiveBind',False)
    autoWeightThreshold = kwargs.get('autoWeightThreshold',True)
    falloffMode = kwargs.get('falloffMode',0)
 
    wrapData = pm.deformer(source, type='wrap')
    wrapNode = wrapData[0]
 
    pm.setAttr(wrapNode+'.weightThreshold',weightThreshold)
    pm.setAttr(wrapNode+'.maxDistance',maxDistance)
    pm.setAttr(wrapNode+'.exclusiveBind',exclusiveBind)
    pm.setAttr(wrapNode+'.autoWeightThreshold',autoWeightThreshold)
    pm.setAttr(wrapNode+'.falloffMode',falloffMode)
 
    pm.connectAttr(source+'.worldMatrix[0]',wrapNode+'.geomMatrix')
    
    #add target
    duplicateData = pm.duplicate(target,name=target+'Base')
    base = duplicateData[0]
    shapes = pm.listRelatives(base,shapes=True)
    baseShape = shapes[0]
    pm.hide(base)
    
    #create dropoff attr if it doesn't exist
    if not pm.attributeQuery('dropoff',n=target,exists=True):
        pm.addAttr( target, sn='dr', ln='dropoff', dv=4.0, min=0.0, max=20.0  )
        pm.setAttr( target+'.dr', k=True )
    
    #if type mesh
    if pm.nodeType(targetShape) == 'mesh':
        #create smoothness attr if it doesn't exist
        if not pm.attributeQuery('smoothness',n=target,exists=True):
            pm.addAttr( target, sn='smt', ln='smoothness', dv=0.0, min=0.0  )
            pm.setAttr( target+'.smt', k=True )
 
        #create the inflType attr if it doesn't exist
        if not pm.attributeQuery('inflType',n=target,exists=True):
            pm.addAttr( target, at='short', sn='ift', ln='inflType', dv=2, min=1, max=2  )
 
        pm.connectAttr(targetShape+'.worldMesh',wrapNode+'.driverPoints[0]')
        pm.connectAttr(baseShape+'.worldMesh',wrapNode+'.basePoints[0]')
        pm.connectAttr(target+'.inflType',wrapNode+'.inflType[0]')
        pm.connectAttr(target+'.smoothness',wrapNode+'.smoothness[0]')
 
    #if type nurbsCurve or nurbsSurface
    if pm.nodeType(targetShape) == 'nurbsCurve' or pm.nodeType(targetShape) == 'nurbsSurface':
        #create the wrapSamples attr if it doesn't exist
        if not pm.attributeQuery('wrapSamples',n=target,exists=True):
            pm.addAttr( target, at='short', sn='wsm', ln='wrapSamples', dv=10, min=1  )
            pm.setAttr( target+'.wsm', k=True )
 
        pm.connectAttr(targetShape+'.ws',wrapNode+'.driverPoints[0]')
        pm.connectAttr(baseShape+'.ws',wrapNode+'.basePoints[0]')
        pm.connectAttr(target+'.wsm',wrapNode+'.nurbsSamples[0]')
 
    pm.connectAttr(target+'.dropoff',wrapNode+'.dropoff[0]')