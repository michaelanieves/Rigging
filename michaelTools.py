#!/usr/bin/env python
"""
    :module: Michaels Tools UI
    :platform: Maya
    :synopsis: This module contains the nessacery tools to change the appearance of maya curves
    :plans: add more functions & clean up code (anotate, convert to pymel)
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm
import maya.mel as mel

# Import functions
import Rigging.offSetGRP as offSetGRP
import Rigging.sdkGRP as sdkGRP
import Rigging.conGRP as conGRP
import Rigging.under_locator as unLoc
import Rigging.newPosition as nPos
import Rigging.rgbColorOverride as rgbColor
import Rigging.parentShapes as prntShps
import Rigging.quick_connect as quickCon
import Rigging.quick_constrain as quickConstrain
import Rigging.newPivot as newPivot
import Rigging.center_pivot_each as cpe
import Rigging.newPosition as newPosition
import Rigging.snap_to_object as snapObj
import Rigging.crv_piv_start as crvPivStart
import Rigging.snap_first_cv as snapFirstCv
import Rigging.flexi_plane as flexi_plane
import Rigging.jnts_onCrv as jntsOnCrv

# Refresh Functions to latest each run
reload(offSetGRP)
reload(sdkGRP)
reload(conGRP)
reload(unLoc)
reload(nPos)
reload(rgbColor)
reload(prntShps)
reload(newPivot)
reload(cpe)
reload(quickCon)
reload(quickConstrain)
reload(newPosition)
reload(snapObj)
reload(crvPivStart)
reload(snapFirstCv)
reload(flexi_plane)
reload(jntsOnCrv)

# color range class
class ColorRange(object):
    def __init__(self, rgb):
        self.r, self.g, self.b = rgb
    
    def get_range(self, num, min = 0.00, max =.4):
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
        
# UI class
class michaelToolUI(object):
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
        self.winlayout = pm.columnLayout( adj = True )
        self.tabs = pm.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        # Modeling Tools TAB
        self.modelingTools_layout = pm.columnLayout(parent = self.tabs, adj = True )
        self.modelingToolsText = pm.button( parent = self.modelingTools_layout, w = 244, h = 24, label = 'Modeling Tools' )
        self.modelingToolsToComeText = pm.button( parent = self.modelingTools_layout, w = 244, h = 24, label = 'Modeling Tools Coming Soon!' )
        modelingTools_gradParent=self.modelingTools_layout
        
        modelingTools_color_range = ColorRange([0.0, 0.2, 0.0])
        
        for modelingTools_grad, color in zip(modelingTools_gradParent.children(), modelingTools_color_range.get_range(len(modelingTools_gradParent.children())) ):
            print modelingTools_grad, color
            modelingTools_grad.setBackgroundColor(color)
        
        # Rigging Tools TAB
        self.riggingTools_layout = pm.columnLayout(parent = self.tabs, adj = True )
        # grouping Functions frame and contents
        self.grpFrame = pm.frameLayout( parent = self.riggingTools_layout, w =244, label='Grouping Functions', borderStyle='out', cll = True, cl = True )
        self.grplayout = pm.rowColumnLayout(parent = self.grpFrame, numberOfColumns = 2, columnWidth = [(1, 120), (2, 120)] )
        self.offSetGRP_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Add Offset Group", command = offSetGRP.add_offset_grps )
        self.sdkGRP_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Add SDK Group", command = sdkGRP.add_SDK_grps )
        self.conGRP_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Add Control Group", command = conGRP.add_con_grps )
        self.underLoc_Btn = pm.button(parent=self.grplayout,w = 100, h = 24, label="Under Locator", command = unLoc.under_locator )
        # color overrides frame and contents
        self.colorFrame = pm.frameLayout( parent = self.riggingTools_layout, w =244, label='Color Overrides', borderStyle='out', cll = True, cl = True )
        self.colorlayout = pm.columnLayout( parent = self.colorFrame, columnWidth = 120 )
        self.colorSlider = pm.colorIndexSliderGrp( parent = self.colorlayout,cw3 = [40, 60, 130], label='Color  ', min=1, max=32, value=0 )
        self.changeColor_Btn = pm.button(parent=self.colorlayout,w = 240, h = 24, label="Override Color", command = self.exe_sliderColor )
        self.orRGBText = pm.text( parent=self.colorlayout, w = 240, label='Or Use', align='center' )
        self.changeColor_Btn = pm.button(parent=self.colorlayout,w = 240, h = 24, label="RGB Color Picker", command = rgbColor.rgbColorOverride )
        # Shape Functions Frame and Contents
        self.shapeFrame = pm.frameLayout( parent = self.riggingTools_layout, w =244, label='Shape Functions', borderStyle='out', cll = True, cl = True )
        self.shapelayout = pm.columnLayout(parent = self.shapeFrame, columnWidth = 240 )
        self.parentShape_Btn = pm.button(parent=self.shapelayout,w = 240, h = 24, label="Parent Shapes To Last", command = prntShps.parentShapes )
        # Connect Functions Frame and Contents
        self.connectFrame = pm.frameLayout( parent = self.riggingTools_layout, w =244, label='Connect', borderStyle='out', cll = True, cl = True )
        self.conTChkBoxGRP = pm.checkBoxGrp( parent = self.connectFrame, cw = ( [ 1, 78 ], [ 2, 78 ], [ 3, 78 ] ), numberOfCheckBoxes=3, labelArray3=['Translate X', 'Translate Y', 'Translate Z'], v1 = 1, v2 = 1, v3 =  1 )
        self.conRChkBoxGRP = pm.checkBoxGrp( parent = self.connectFrame, cw = ( [ 1, 78 ], [ 2, 78 ], [ 3, 78 ] ),numberOfCheckBoxes=3, labelArray3=['Rotate X', 'Rotate Y', 'Rotate Z'], v1 = 1, v2 = 1, v3 =  1 )
        self.conSChkBoxGRP = pm.checkBoxGrp( parent = self.connectFrame, cw = ( [ 1, 78 ], [ 2, 78 ], [ 3, 78 ] ),numberOfCheckBoxes=3, labelArray3=['Scale X', 'Scale Y', 'Scale Z'], v1 = 1, v2 = 1, v3 =  1 )
        self.conVChkBox = pm.checkBox( parent = self.connectFrame, label='Visibility', v = 1 )
        self.conTX_Btn = pm.button(parent = self.connectFrame, w = 244, h = 24, label="Connect All To Last", command = self.quick_connect)
        # Constrain Functions Frame and Contents
        self.constrainFrame = pm.frameLayout( parent = self.riggingTools_layout, w =244, label='Constrain', borderStyle='out', cll = True, cl = True )
        self.constrainFrame_layout = pm.rowColumnLayout(parent = self.constrainFrame)
        self.constrain_ChkBox = pm.checkBox( parent = self.constrainFrame_layout, label='Maintain Offset', v = 1 )
        self.constPar_Btn = pm.button(parent = self.constrainFrame_layout, w = 244, h = 24, label="Parent Constrain All To Last Selected", command = self.quick_constParent )
        self.constPoint_Btn = pm.button(parent = self.constrainFrame_layout, w = 244, h = 24, label="Point Constrain All To Last Selected", command = self.quick_constPoint )
        self.constOri_Btn = pm.button(parent = self.constrainFrame_layout, w = 244, h = 24, label="Orient Constrain All To Last Selected", command = self.quick_constOrient )
        self.constScale_Btn = pm.button(parent = self.constrainFrame_layout, w = 244, h = 24, label="Scale Constrain All To Last Selected", command = self.quick_constScale )
        # Other Functions 
        self.newPiv_Btn = pm.button(parent = self.riggingTools_layout, w = 244, h = 24, label="Match All Piviots To Last Selected", command = newPivot.set_newPivot )
        self.newPos_Btn = pm.button(parent = self.riggingTools_layout, w = 244, h = 24, label="Match All Positions To Last Selected", command = newPosition.set_newPosition )
        self.cnt_piv_all_Btn = pm.button(parent = self.riggingTools_layout, w = 244, h = 24, label="Center Pivot For Each", command = self.exe_center_pivot_each)
        # self.snap_objects = pm.button(parent = self.riggingTools_layout, w = 244, h = 24, label="Snap All To Last Selected At Closest Points", command = self.exe_snap_objects )
        self.crvPiv_atStart_Btn = pm.button(parent = self.riggingTools_layout, w = 244, h = 24, label="Set Piviot Of Seleced Curves To cv0", command = crvPivStart.crv_piv_start )
        self.snap_first_cv_Btn = pm.button(parent = self.riggingTools_layout, w = 244, h = 24, label="Snap cv0 For All To Last Selected ", command = self.exe_snap_first_cv )

        riggingTools_gradParent=self.riggingTools_layout
        riggingTools_gradParent.getNumberOfChildren()
        riggingTools_color_range = ColorRange([0.2, 0.0, 0.0])
        
        for riggingTools_grad, color in zip(riggingTools_gradParent.children(), riggingTools_color_range.get_range(len(riggingTools_gradParent.children())) ):
            print riggingTools_grad, color
            riggingTools_grad.setBackgroundColor(color)
            
        # Shading Tools TAB
        self.shadingTools_layout = pm.columnLayout(parent = self.tabs, adj = True )
        self.shadingToolsText = pm.button( parent = self.shadingTools_layout, w = 244, h = 24, label = 'Shadeing Tools' )
        self.shadingToolsToComeText = pm.button( parent = self.shadingTools_layout, w = 244, h = 24, label = 'Shading Tools Coming Soon!' )
        shadingTools_gradParent=self.shadingTools_layout
        
        shadingTools_color_range = ColorRange([0.0, 0.2, 0.2])
        
        for shadingTools_grad, color in zip(shadingTools_gradParent.children(), shadingTools_color_range.get_range(len(shadingTools_gradParent.children())) ):
            print shadingTools_grad, color
            shadingTools_grad.setBackgroundColor(color)

        # Layout Tools TAB
        self.layoutTools_layout = pm.columnLayout(parent = self.tabs, adj = True )
        self.layoutToolsText = pm.button( parent = self.layoutTools_layout, w = 244, h = 24, label = 'Layout Tools' )
        self.layoutToolsToComeText = pm.button( parent = self.layoutTools_layout, w = 244, h = 24, label = 'Layout Tools Coming Soon!' )
        layoutTools_gradParent=self.layoutTools_layout
        
        layoutTools_color_range = ColorRange([0.0, 0.0, 0.2])
        
        for layoutTools_grad, color in zip(layoutTools_gradParent.children(), layoutTools_color_range.get_range(len(layoutTools_gradParent.children())) ):
            print layoutTools_grad, color
            layoutTools_grad.setBackgroundColor(color)

        # Module Tools TAB
        self.moduleTools_layout = pm.columnLayout(parent = self.tabs, adj = True )
        self.flexi_plane_Mod_Btn = pm.button(parent = self.moduleTools_layout, w = 244, h = 24, label="Create A Flexi Plane", command = self.exe_flexi_plane_Mod )
        self.jnts_on_crv_Btn = pm.button(parent = self.moduleTools_layout, w = 244, h = 24, label="Joints On Curve", command = self.exe_jnts_on_crv )
        
        moduleTools_gradParent=self.moduleTools_layout
        moduleTools_gradParent.getNumberOfChildren()
        ctrlTools_color_range = ColorRange([0.5, 0.5, 0.0])
        
        for moduleTools_grad, color in zip(moduleTools_gradParent.children(), ctrlTools_color_range.get_range(len(moduleTools_gradParent.children())) ):
            print moduleTools_grad, color
            moduleTools_grad.setBackgroundColor(color)
        
        # Edit Tab Layout labels
        pm.tabLayout( self.tabs, edit=True, tabLabel=( (self.riggingTools_layout, 'Rigging'), (self.moduleTools_layout, 'Modules'), ( self.modelingTools_layout, 'Modeling'), (self.shadingTools_layout, 'Shading'), (self.layoutTools_layout, 'Layout') ) )
        
        # Window Functions
        self.closeTool_Btn = pm.button(parent = self.winlayout,w = 330, h = 24, label="Close Tool", command = self.closeWin)
        self.delete = []
        self.win.show()

    def exe_sliderColor(self, *args, **kwargs):
        """ This function can set the override color for shape nodes of the selected objects based on the UI slider
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
                
    def quick_connect(self, *args, **kwargs):
        """ This function can center the pivot for each selected object
        Args:
            None
        Returns (None)
        """
        if pm.checkBoxGrp(self.conTChkBoxGRP, q=True, value1=True):
            quickCon.quick_connectTranslateX()
        if pm.checkBoxGrp(self.conTChkBoxGRP, q=True, value2=True):
            quickCon.quick_connectTranslateY()
        if pm.checkBoxGrp(self.conTChkBoxGRP, q=True, value3=True):
            quickCon.quick_connectTranslateZ()
        if pm.checkBoxGrp(self.conRChkBoxGRP, q=True, value1=True):
            quickCon.quick_connectRotateX()
        if pm.checkBoxGrp(self.conRChkBoxGRP, q=True, value2=True):
            quickCon.quick_connectRotateY()
        if pm.checkBoxGrp(self.conRChkBoxGRP, q=True, value3=True):
            quickCon.quick_connectRotateZ()
        if pm.checkBoxGrp(self.conSChkBoxGRP, q=True, value1=True):
            quickCon.quick_connectScaleX()
        if pm.checkBoxGrp(self.conSChkBoxGRP, q=True, value2=True):
            quickCon.quick_connectScaleY()
        if pm.checkBoxGrp(self.conSChkBoxGRP, q=True, value3=True):
            quickCon.quick_connectScaleZ()
        if pm.checkBox(self.conVChkBox, q=True, value=True):
            quickCon.quick_connectVisibiity()
            
    def quick_constParent(self, *args, **kwargs):
        """ This function can center the pivot for each selected object
        Args:
            None
        Returns (None)
        """
        if pm.checkBox(self.constrain_ChkBox, q=True, value=True):
            quickConstrain.quick_constrainParentOffset()
        else:
            quickConstrain.quick_constrainParent()

    def quick_constPoint(self, *args, **kwargs):
        """ This function can center the pivot for each selected object
        Args:
            None
        Returns (None)
        """
        if pm.checkBox(self.constrain_ChkBox, q=True, value=True):
            quickConstrain.quick_constrainPointOffset()
        else:
            quickConstrain.quick_constrainPoint()

    def quick_constOrient(self, *args, **kwargs):
        """ This function can center the pivot for each selected object
        Args:
            None
        Returns (None)
        """
        if pm.checkBox(self.constrain_ChkBox, q=True, value=True):
            quickConstrain.quick_constrainOreintOffset()
        else:
            quickConstrain.quick_constrainOreint()

    def quick_constScale(self, *args, **kwargs):
        """ This function can center the pivot for each selected object
        Args:
            None
        Returns (None)
        """
        if pm.checkBox(self.constrain_ChkBox, q=True, value=True):
            quickConstrain.quick_constrainScaleOffset()
        else:
            quickConstrain.quick_constrainScale()

    def exe_center_pivot_each(self, *args, **kwargs):
        """ This function can center the pivot for each selected object
        Args:
            None
        Returns (None)
        """
        cpe.center_pivot_each(pm.ls(sl=True))

    def exe_snap_first_cv(self, *args, **kwargs):
        """ This function can snap the fist cv of selected curves to the last selected object
        Args:
            None
        Returns (None)
        """
        snapFirstCv.snap_first_cv(pm.ls(sl=True, fl=True)[:-1], pm.ls(sl=True)[-1])
        
    def exe_snap_objects(self, *args, **kwargs):
        """ This function can snap the closest point of of the selected objects to the closest point of the last selected object
        Args:
            None
        Returns (None)
        """
        snapObj.snap_object(pm.ls(sl=True)[:-1], pm.ls(sl=True)[-1])
        
    def exe_flexi_plane_Mod(self, *args, **kwargs):
        """ This function can run the flexi plane creator UI
        Args:
            None
        Returns (None)
        """
        flexi_plane.flexi_planeUI()
        
    def exe_jnts_on_crv(self, *args, **kwargs):
        """ This function can run the joints on curves UI
            None
        Returns (None)
        """
        jntsOnCrv.Joint_curveUI()

    def closeWin(self, *args, **kwargs):
        """ This function can Close the UI
        Args:
            None
        Returns (None)
        """
        if kwargs.get('debug'):
            print "NO STOP IT!!!"
        pm.deleteUI(self.win)

# Open UI        
if __name__ == '__main__':
    my_ui = michaelToolUI()