#!/usr/bin/env python
"""
    :module: curveTools
    :platform: Maya
    :synopsis: This module contains the nessacery tools to change the appearance of maya curves
    :plans: add more functions & clean up code (anotate, convert to pymel)
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm
import maya.mel as mel
import Rigging.offSetGRP as offSetGRP
import Rigging.sdkGRP as sdkGRP
import Rigging.conGRP as conGRP
import Rigging.under_locator as unLoc
import Rigging.newPosition as nPos
import Rigging.rgbColorOverride as rgbColor
import Rigging.parentShapes as prntShps
import Rigging.newPivot as newPivot
import Rigging.newPosition as newPosition


reload(offSetGRP)
reload(sdkGRP)
reload(conGRP)
reload(unLoc)
reload(nPos)
reload(rgbColor)
reload(prntShps)
reload(newPivot)
reload(newPosition)

class ColorRange(object):
    def __init__(self, rgb):
        self.r, self.g, self.b = rgb
    
    def get_range(self, num, min = 0.25, max =.5):
        max = [max]*3 if (isinstance(max, float) or isinstance(max, int)) else max
        min = [min]*3 if (isinstance(min, float) or isinstance(min, int)) else min
        vals = []
        
        for component, max_component, min_component in zip([self.r, self.g, self.b], max, min):
            component_list = []
            cur_val = component if not min_component > component else min_component
            min_component = cur_val
            
            incr = (max_component - min_component) / (float(num)-1)
            
            for n in range(0, num):
                component_list.append(cur_val)
                cur_val += incr
            vals.append(component_list)
            
        colors = []
        for r,g,b in zip(vals[0], vals[1], vals[2]):
            colors.append([r,g,b])
        
        return colors

class curveToolsUI(object):
    """ View -- contains user interface
    """
    def __init__(self):
        title="michaelTools"
        if(pm.windowPref(title, q=True, ex=True)):
            pm.windowPref(title, remove=True)
        if(pm.window(title, q=True, ex=True)):
            pm.deleteUI(title)
            
        # Michael's Tools UI
        self.win = pm.window(title, title="Michael's Tools")
        self.winlayout = pm.columnLayout()
        self.tabs = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        
        # CTRL Tools TAB
        self.ctrlTools_layout = pm.columnLayout(parent = self.tabs)
        # grouping Functions frame and contents
        self.grpFrame = pm.frameLayout( parent = self.ctrlTools_layout, w =244, label='Grouping Functions', borderStyle='out', cll = True, cl = True )
        self.grplayout = pm.rowColumnLayout(parent = self.grpFrame, numberOfColumns = 2, columnWidth = [(1, 120), (2, 120)] )
        self.offSetGRP_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Add Offset Group", command = offSetGRP.add_offset_grps )
        self.sdkGRP_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Add SDK Group", command = sdkGRP.add_SDK_grps )
        self.conGRP_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Add Control Group", command = conGRP.add_con_grps )
        self.underLoc_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Under Locator", command = unLoc.under_locator )
        # color overrides frame and contents
        self.colorFrame = pm.frameLayout( parent = self.ctrlTools_layout, w =244, label='Color Overrides', borderStyle='out', cll = True, cl = True )
        self.colorlayout = pm.columnLayout( parent = self.colorFrame, columnWidth = 120 )
        self.colorSlider = pm.colorIndexSliderGrp( parent = self.colorlayout,cw3 = [40, 60, 130], label='Color  ', min=1, max=32, value=0 )
        self.changeColor_Btn = pm.button(parent=self.colorlayout,w = 240, h = 24, label="Override Color", command = self.exe_sliderColor )
        self.orRGBText = pm.text( parent=self.colorlayout, w = 240, label='Or Use', align='center' )
        self.changeColor_Btn = pm.button(parent=self.colorlayout,w = 240, h = 24, label="RGB Color Picker", command = rgbColor.rgbColorOverride )
        # Shape Functions Frame and Contents
        self.shapeFrame = pm.frameLayout( parent = self.ctrlTools_layout, w =244, label='Shape Functions', borderStyle='out', cll = True, cl = True )
        self.shapelayout = pm.columnLayout(parent = self.shapeFrame, columnWidth = 240 )
        self.parentShape_Btn = pm.button(parent=self.shapelayout,w = 240, h = 24, label="Parent Shapes To Last", command = prntShps.parentShapes )

        ctrlTools_gradParent=self.ctrlTools_layout
        ctrlTools_gradParent.getNumberOfChildren()
        color_range = ColorRange([0.0, 0.4, 0.4])
        
        for ctrlTools_grad, color in zip(ctrlTools_gradParent.children(), color_range.get_range(len(ctrlTools_gradParent.children())) ):
            print ctrlTools_grad, color
            ctrlTools_grad.setBackgroundColor(color)
        
        # TRANSFORM TOOLS TAB
        self.transformTools_layout = pm.columnLayout(parent = self.tabs)
        self.newPivBtn = pm.button(parent = self.transformTools_layout, w = 244, h = 24, label="Match All Piviots To Last Selected", command = newPivot.set_newPivot )
        self.newPosBtn = pm.button(parent = self.transformTools_layout, w = 244, h = 24, label="Match All Positions To Last Selected", command = newPosition.set_newPosition )
        
        # Edit Tab Layout labels
        pm.tabLayout( self.tabs, edit=True, tabLabel=((self.ctrlTools_layout, 'Control Tools'), (self.transformTools_layout, 'Transform Tools')) )
        
        # Window Functions
        self.closeToolBtn = pm.button(parent = self.winlayout,w = 251, h = 24, label="Close Tool", command = self.closeWin)
        self.delete = []
        self.win.show()

    def exe_sliderColor(self, *args, **kwargs):
        """ This function can Close the UI
        Args:
            None
        Returns (None)
        """
        sel = pm.ls(sl=True)
        sldrVal = self.colorSlider.getValue()
        
        for obj in sel:
            for shape in obj.getShapes():
                shape.overrideEnabled.set(1)
                shape.overrideRGBColors.set(0)
                shape.overrideColor.set( sldrVal - 1 )

    def closeWin(self, *args, **kwargs):
        """ This function can Close the UI
        Args:
            None
        Returns (None)
        """
        if kwargs.get('debug'):
            print "NO STOP IT!!!"
        pm.deleteUI(self.win)
        
if __name__ == '__main__':
    my_ui = curveToolsUI()