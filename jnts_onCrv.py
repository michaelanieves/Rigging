#!/usr/bin/env python
"""
    :module: jnts_on_crv
    :platform: Maya
    :synopsis: This module has the nessacery components to create joints along a curve
    :plans: None
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import aw.maya
import pymel.core as pm
import Rigging.offSetGRP as offSetGRP
import Rigging.conGRP as conGRP
import Rigging.newPosition as nPos


class Curve_info(object):
    """ Model -- contains curve data 
    """
    def __init__(self, node):
        self.transform = node
        self.refresh_curve()
    
    def refresh_curve(self):
        """ This function refreshes the specified curve data when called
        Args:
            None
        Returns (None)
        """
        self.numCVs = self.transform.getShape().numCVs()
        self.numSpans = self.transform.getShape().numSpans()
        self.crvCVs = pm.ls( self.transform.getShape().cv[:], fl=True )


class Joint_curveUI(object):
    """ View -- contains user interface
    """
    def __init__(self):
        title="joints_on_curve"
        if(pm.windowPref(title, q=True, ex=True)):
            pm.windowPref(title, remove=True)
        if(pm.window(title, q=True, ex=True)):
            pm.deleteUI(title)
        #splineIK UI
        self.win = pm.window(title, title="Joints on Curve")
        self.layout = pm.rowColumnLayout()
        self.jntPlaceBtn = pm.radioButtonGrp(parent=self.layout, numberOfRadioButtons=2, label="Joint Placement", labelArray2=("CV's", "Even"), cc=self.jntPlaceBtn_change)
        self.jntSnapBtn = pm.radioButtonGrp(parent=self.layout, enable=False, numberOfRadioButtons=2, sl = 1,  label="Snap To", labelArray2=("CV", "Closest Point On Curve"))
        self.jntLayoutBtn = pm.radioButtonGrp(parent=self.layout, enable=False, numberOfRadioButtons=2, sl = 1,  label="Joint Layout", labelArray2=("Solo", "Hierarchy"), on1 = self.jntLayoutBtn_on)
        self.jntNumSlider = pm.intSliderGrp(enable=False, field=True, label='number of joints', minValue=4, maxValue=100, fieldMinValue=4, fieldMaxValue=100, value=0)
        self.crvNameField = pm.textFieldButtonGrp(enable=False, label='Target Curve', placeholderText='Enter Curve Name Here', buttonLabel='load selected', buttonCommand=self.crvNameField_load)
        self.jntNameFeild = pm.textFieldGrp(parent=self.layout,enable=False, label='Joint Base Name', placeholderText="name your joints", editable=True, tcc=self.jntNameFeild_change)
        self.chkboxGrp = pm.checkBoxGrp(enable=False, numberOfCheckBoxes=3, label='Add', labelArray3=['splineIK', 'CTRLs', 'stretchy'])
        self.goBtn = pm.button(parent=self.layout, enable=False,w = 100, h = 24, label="GO!", command=self.execute)  
        self.noBtn = pm.button(parent=self.layout, enable=False,w = 100, h = 24, label="NO DONT DO IT!", command=self.close)   
        self.format_string = "{PREFIX}_{INDEX}_{SUFFIX}"
        self.delete = []
        self.win.show()

    #enable/disable UI parts
    def jntPlaceBtn_change(self, *args):
        """ This is what my function can do
        Args:
            None
        Returns (None)
        """
        if self.jntPlaceBtn.getSelect()==1:
            self.jntLayoutBtn.setEnable(True)
            self.jntSnapBtn.setEnable(True)
            self.jntNumSlider.setEnable(False)
            self.crvNameField.setEnable(True)
            self.jntNameFeild.setEnable(True)
    
        else:
            self.jntLayoutBtn.setEnable(True)
            self.jntSnapBtn.setEnable(True)
            self.jntNumSlider.setEnable(True)
            self.crvNameField.setEnable(True)
            self.jntNameFeild.setEnable(True)
            
    def jntLayoutBtn_on(self, *args):
        """ This function can disable the Add checkBoxGrp
        Args:
            None
        Returns (None)
        """
        self.chkboxGrp.setEnable(False)
        
    #Load curve Name Field
    def crvNameField_load(self, *args):
        """ This function will update the curve to be used and refresh the curve model data
        Args:
            None
        Returns (None)
        """
        selection = pm.ls(sl=True)
        if len(selection) > 1:
            print "Too many objects selected"
            self.crvNameField.setText(selection[0])
 
        elif len(selection) < 1:
            print "Nothing selected"
            self.crvNameField.setText("")
            
        else:
            print "Good job you have one object selected"
            self.crvNameField.setText(selection[0])
            self.model = Curve_info(selection[0])
    
    #enable final UI parts  
    def jntNameFeild_change(self, *args):
        """ This function can enable the execution buttons of the user interface
        Args:
            None
        Returns (None)
        """
        if self.jntLayoutBtn.getSelect()==1:
            self.chkboxGrp.setEnable(False)
        else:
            self.chkboxGrp.setEnable(True)
        self.goBtn.setEnable(True)
        self.noBtn.setEnable(True)
    
    #Excecute UI selections    
    def execute(self, *args, **kwargs):
        """ This function can execute other functions based on user selection
        Args:
            None
        Returns (None)
        """
        crv_name = self.crvNameField.getText()
        new_crv_name = self.jntNameFeild.getText() + '_CRV'
        if kwargs.get('debug'):
            print "GO!!!"
        if self.jntPlaceBtn.getSelect()==2:
            self.evenly_spaced_crv()
        else:
            pm.rename(crv_name, new_crv_name)
            pm.select(clear = True)
            
        self.create_joints()
        
        if self.chkboxGrp.getValue1()==1:
            self.splineIK_jntsOnCrv()
            
        if self.chkboxGrp.getValue2()==1:
            self.splineIK_controls()
            
        if self.chkboxGrp.getValue3()==1:
            self.splineIK_stretch()
                    
        self.splineIK_organizeOutliner()
        pm.select(clear = True)  
        pm.delete(self.delete)

    def close(self, *args, **kwargs):
        """ This function can Close the UI
        Args:
            None
        Returns (None)
        """
        if kwargs.get('debug'):
            print "NO STOP IT!!!"
        pm.deleteUI(self.win)

    def evenly_spaced_crv(self, *args):
        """ Rebuilds selected curve number of cv's based on jntNumSlider
        Args:
            None
        Returns (None)
        """
        crv_name = self.crvNameField.getText()
        new_crv_name = self.jntNameFeild.getText() + '_CRV'
        num_crv_cvs = self.jntNumSlider.getValue() -1

        if pm.objExists( crv_name ):
            crv = pm.PyNode( crv_name )

            pm.rebuildCurve( crv, rt=0, s=num_crv_cvs, kep=True, ch=True )
            pm.delete( crv.getShape().cv[1] )
            pm.delete( crv.getShape().cv[-2] )
            self.model.refresh_curve()
            pm.rename(crv_name, new_crv_name)
    
    def create_joints(self, *args):
        """ Creates jnts on each cv of selected curve 
        Args:
            None
        Returns (None)
        """
        orig_sel = pm.ls(sl=True)
        new_crv = pm.PyNode('%s_CRV' % self.jntNameFeild.getText())
        curve_or_cv = self.jntPlaceBtn.getSelect()
        jnt_prefix = self.jntNameFeild.getText()
        # Converting chain flag to boolean value
        chain = self.jntLayoutBtn.getSelect() - 1
        
        positions = self.get_cv_positions_on_curve(new_crv, jnt_prefix, on_curve=curve_or_cv)
        self.create_jnts_on_points(positions, jnt_prefix, chain=chain)

        pm.select(orig_sel, r=True)
        return self.joints
    
    def get_cv_positions_on_curve(self, curve, prefix, on_curve=False):
        """ Get points on a curve
        Args:
            curve (pm.nt.Transform): the transform for the given curve to be queried
            on_curve (bool): Whether to return CV positions or position on curve relative to each CV
        Returns [tuple]: list of positions
        """
        print 'get_cv_positions_on_curve'
        positions = []
        npoCrv = pm.createNode ("closestPointOnCurve", n=prefix + '_npoCrv')
        
        pm.scriptEditorInfo(e=True, suppressWarnings=True)
        for cv in self.model.crvCVs:
            position = (0,0,0)
            if on_curve:
                # Get the position on the curve of the nearest CV
                curve.getShape().worldSpace.connect(npoCrv.inCurve, f=True)
                #tempLoc = pm.spaceLocator(n = prefix + '_LOC', a = True)
                npoCrv.inPosition.set(cv.getPosition())
                # Append to our position list
                position = npoCrv.position.get()
            else:
                position = cv.getPosition()
            positions.append(position)
            if self.jntLayoutBtn.getSelect()==1:
                pm.select(clear = True)
        self.delete.append(npoCrv)
        pm.scriptEditorInfo(e=True, suppressWarnings=False)
        return positions
        
    def create_jnts_on_points(self, points, prefix, chain=True):
        """ Create joints over a series of points
        Args:
            points (tuple): tuple of size 3, 3d position
            prefix (str): joint name prefix
            chain (bool): whether or not to create a joint chain or free floating
        Returns [pm.nt.Joint]: list of joints created
        """
        print 'create_jnts_on_points'
        self.joints = []
        
        for index, point in enumerate(points):
            jnt_name = self.format_string.format(PREFIX = prefix,
                                                 INDEX = '%03d' % (index+1),
                                                 SUFFIX = 'JNT')
            jnt = pm.joint(p=point, n=jnt_name)
            self.joints.append(jnt)
            
            if len(self.joints) > 1 and chain:
                jnt.setParent(self.joints[index-1])
                pm.select(self.joints[0], r=True)
                pm.joint(e = True, ch = True, oj = 'yxz', secondaryAxisOrient = 'zup', zso = True)
                pm.select(clear = True)
            if not chain:
                jnt.setParent("")

    def splineIK_jntsOnCrv(self, *args):
        """ Build splineIK
        Args:
            None
        Returns (None)
        """
        new_crv_name = self.jntNameFeild.getText() + '_CRV'
        splineIK_name = self.jntNameFeild.getText() + '_SIK'
        splineIK_effectorName = self.jntNameFeild.getText() + '_EFF'
        
        pm.select(self.joints[0], r=True)
        pm.select(self.joints[-1], add=True)
        pm.ikHandle(n=splineIK_name, sol='ikSplineSolver',c= new_crv_name, ccv=False, pcv=False)
        
        splineIK_effector = self.joints[0].listRelatives(ad = True, type = 'ikEffector')
        pm.rename(splineIK_effector, splineIK_effectorName)
        pm.select(clear = True)

    def splineIK_controls(self, *args):
        """ Build splineIK Controls
        Args:
            None
        Returns (None)
        """
        jnt_prefix = self.jntNameFeild.getText()
        midJnt = self.model.numCVs / 2
        
        #Create and place joints
        baseJoint = pm.joint( p = self.model.crvCVs[0].getPosition(), n = self.jntNameFeild.getText() + '_base_JNT')
        pm.select(clear = True)
        midJoint = pm.joint( p = self.model.crvCVs[midJnt].getPosition(), n = self.jntNameFeild.getText() + '_mid_JNT')
        pm.select(clear = True)
        endJoint = pm.joint( p = self.model.crvCVs[-1].getPosition(), n = self.jntNameFeild.getText() + '_end_JNT')
        pm.select(clear = True)                                              

        #Create CTRL curves
        pm.circle(c = (0, 0, 0), nr = (0, 1, 0), sw = 360, r = 1, d = 3, ut = False, tol = 3.80125e-10, s = 8, ch = False, n = self.jntNameFeild.getText() + '_base_CTRL')
        pm.select(self.jntNameFeild.getText() + '_base_CTRL', r=True)
        pm.select(self.jntNameFeild.getText() + '_base_JNT', add=True)
        nPos.set_newPosition()
        pm.select(self.jntNameFeild.getText() + '_base_CTRL', r=True)
        offSetGRP.add_offset_grps()
        conGRP.add_con_grps()
        pm.select(clear = True)
        
        pm.circle(c = (0, 0, 0), nr = (0, 1, 0), sw = 360, r = 1, d = 3, ut = False, tol = 3.80125e-10, s = 8, ch = False, n = self.jntNameFeild.getText() + '_mid_CTRL')
        pm.select(self.jntNameFeild.getText() + '_mid_CTRL', r=True)
        pm.select(self.jntNameFeild.getText() + '_mid_JNT', add=True)
        nPos.set_newPosition()
        pm.select(self.jntNameFeild.getText() + '_mid_CTRL', r=True)
        offSetGRP.add_offset_grps()
        conGRP.add_con_grps()
        pm.select(clear = True)
        
        pm.circle(c = (0, 0, 0), nr = (0, 1, 0), sw = 360, r = 1, d = 3, ut = False, tol = 3.80125e-10, s = 8, ch = False, n = self.jntNameFeild.getText() + '_end_CTRL')
        pm.select(self.jntNameFeild.getText() + '_end_CTRL', r=True)
        pm.select(self.jntNameFeild.getText() + '_end_JNT', add=True)
        nPos.set_newPosition()
        pm.select(self.jntNameFeild.getText() + '_end_CTRL', r=True)
        offSetGRP.add_offset_grps()
        conGRP.add_con_grps()
        pm.select(clear = True)
        
        #Skin jnt's to crv
        pm.select(self.jntNameFeild.getText() + '_base_JNT', r=True)
        pm.select(self.jntNameFeild.getText() + '_mid_JNT', add=True) 
        pm.select(self.jntNameFeild.getText() + '_end_JNT', add=True)       
        pm.select(self.jntNameFeild.getText() + '_CRV', add=True) 
        pm.skinCluster(n=self.jntNameFeild.getText() + '_smoothSkin', mi=3, sm=0, nw=2)

        #Constrain joints to ctrl grps
        pm.parentConstraint( self.jntNameFeild.getText() + '_base_CTRLCon_GRP', self.jntNameFeild.getText() + '_base_JNT')
        pm.parentConstraint( self.jntNameFeild.getText() + '_mid_CTRLCon_GRP', self.jntNameFeild.getText() + '_mid_JNT')
        pm.parentConstraint( self.jntNameFeild.getText() + '_end_CTRLCon_GRP', self.jntNameFeild.getText() + '_end_JNT')
        pm.select(clear = True)
        
    def splineIK_stretch(self, *args):   
        """ This function can enable a stretching attribute to a splineIk joint chain 
        Args:
            None
        Returns (None)
        """
        print 'Sweet that Ik chain is stretchy'
        
    def splineIK_organizeOutliner(self, *args):
        """ This function can group and organize created objects 
        Args:
            None
        Returns (None)
        """
        if self.jntLayoutBtn.getSelect()==1:
            pm.group(self.joints[:], name=self.jntNameFeild.getText() + '_JNT_GRP')
            pm.group(self.jntNameFeild.getText() + '_CRV', self.jntNameFeild.getText() + '_JNT_GRP', name=self.jntNameFeild.getText() + '_GRP')

        if self.jntLayoutBtn.getSelect()==2:
            pm.group(self.joints[0], name=self.jntNameFeild.getText() + '_IK_JNT_GRP')
            if self.chkboxGrp.getValue1()==1:
                pm.group(self.jntNameFeild.getText() + '_CRV', self.jntNameFeild.getText() + '_SIK', name=self.jntNameFeild.getText() + '_noTouch_GRP')
                pm.setAttr(self.jntNameFeild.getText() + '_noTouch_GRP.visibility', False)
            if self.chkboxGrp.getValue2()==0:
                pm.group(self.jntNameFeild.getText() + '_IK_JNT_GRP', self.jntNameFeild.getText() + '_noTouch_GRP', name=self.jntNameFeild.getText() + '_GRP')
            if self.chkboxGrp.getValue2()==1:
                pm.group(self.jntNameFeild.getText() + '_base_JNT', self.jntNameFeild.getText() + '_mid_JNT', self.jntNameFeild.getText() + '_end_JNT', name=self.jntNameFeild.getText() + '_INF_GRP')
                pm.setAttr(self.jntNameFeild.getText() + '_INF_GRP.visibility', False)
                pm.group(self.jntNameFeild.getText() + '_base_CTRLOffset_GRP', self.jntNameFeild.getText() + '_mid_CTRLOffset_GRP', self.jntNameFeild.getText() + '_end_CTRLOffset_GRP', name=self.jntNameFeild.getText() + '_CTRL_GRP')
                pm.group(self.jntNameFeild.getText() + '_IK_JNT_GRP', self.jntNameFeild.getText() + '_INF_GRP', name=self.jntNameFeild.getText() + '_JNT_GRP')
                pm.group(self.jntNameFeild.getText() + '_JNT_GRP', self.jntNameFeild.getText() + '_CTRL_GRP', self.jntNameFeild.getText() + '_noTouch_GRP', name=self.jntNameFeild.getText() + '_GRP')

if __name__ == '__main__':
    my_ui = Joint_curveUI()