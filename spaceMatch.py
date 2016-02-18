#!/usr/bin/env python
"""
    :module: spaceMatch
    :platform: Maya
    :synopsis: This module has the nessacery components to space match objects
    :plans: None
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm
from functools import partial

widgets = {}

def spaceMatchUI():
    if (pm.window('window', exists = True)):
        pm.deleteUI('window', window = True)
        
    #create our window
    widgets['win'] = pm.window( 'window', title = 'SpaceMatch!', w = 300, h = 400 )
        
    #create top frame
    widgets['topFrame'] = pm.frameLayout( l = 'object selection', w = 300 )
    widgets['topColumn'] = pm.columnLayout()
        
    #create object selection area
    widgets['objTFG'] = pm.textFieldGrp(l = 'selected Object', w = 300 )
    widgets['objButton'] = pm.button( l = 'select obj', w = 300, c = getObj )
        
    #go back to window
    pm.setParent(widgets['win'])
        
    #create button frame
    widgets['bottomFrame'] = pm.frameLayout( l = 'space selection', w = 300 )
    widgets['bottomColumn'] = pm.columnLayout()
       
    #show window
    pm.showWindow( widgets['win'] )

def getObj(*args):
    #clear list
    clearList()
    
    #get selected obj and put it in field
    sel = pm.ls( sl = True ) [0]
    pm.textFieldGrp( widgets['objTFG'], e = True, tx = sel )
    
    attr = '%s.space'%sel
    print attr    
    #for that attr grab all of the values
    valuesRaw = pm.attributeQuery( 'space', node = sel, le = True )[0]
    values = valuesRaw.split( ':')
    
    for i in range( 0, len( values )):
        widgets['value%s'%i] = pm.button( l = values[i], w = 300, h = 50, c = partial(match, i))
        
def clearList(*args):
    #delete the cLayout
    pm.deleteUI( widgets['bottomColumn'] )
    #make a new cLayout
    widgets['bottomColumn'] = pm.columnLayout( p = widgets['bottomFrame'] )
    pass
        
def match(value, *args):
    #get object
    obj = pm.textFieldGrp( widgets['objTFG'], q = True, tx = True )
    
    #get worldspace translation of obj
    wst = pm.xform( obj, q = True, ws = True, t = True )
    
    #get worldspace rotation of obj
    wsr = pm.xform( obj, q = True, ws = True, ro = True )
    
    #set spaceswitch
    pm.setAttr( '%s.space'%obj, value )
    
    #set worldspace translation of object
    pm.xform( obj, ws = True, t = wst)
    
    #set worldspace rotation of object
    pm.xform( obj, ws = True, ro = wsr)
     
    pass
    
def spaceMatch():
    spaceMatchUI()