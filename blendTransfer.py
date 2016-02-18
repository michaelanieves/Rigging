#!/usr/bin/env python
"""
    :module: blendTransfer
    :platform: Maya
    :synopsis: This module has the nessacery components to transfer blendShapes from source mesh to target mesh
    :plans: None
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm
import Rigging.wrapTarget as wrapTgt
from functools import partial
reload(wrapTgt)

class blend_transfer(object):
    """ View -- contains user interface
    """
    suffixes = ['GEO', 'FOL', 'IOM', 'INF', 'GRP', 'REF', 'BSP', 'BLD', 'CRV', 'JNT', 'LOC', 'Offset_GRP']
    def __init__(self, debug=0):
        title="TransferBlendShapes"
        if(pm.windowPref(title, q=True, ex=True)):
            pm.windowPref(title, remove=True)
        if(pm.window(title, q=True, ex=True)):
            pm.deleteUI(title)
            
        self.win = pm.window(title, title="Transfer BlendShapes Tool")
        self.rowColumnLayoutA = pm.rowColumnLayout()
        self.intro = pm.text( label='complete the following steps in order' )
        self.frameLayoutA = pm.frameLayout(parent=self.rowColumnLayoutA, cl=True, cll=True, label='Step 1   Load Target Mesh', borderStyle='in' )
        self.columnlayoutA = pm.columnLayout()
        self.frameLayoutB = pm.frameLayout(parent=self.rowColumnLayoutA, cl=True, cll=True, label='Step 2   Import Mask', borderStyle='in' )
        self.columnlayoutA = pm.columnLayout()
        self.frameLayoutC = pm.frameLayout(parent=self.rowColumnLayoutA, cl=True, cll=True,  label='Step 3   Manipulate Match Mesh', borderStyle='in' )
        self.columnlayoutB = pm.columnLayout()
        self.frameLayoutD = pm.frameLayout(parent=self.rowColumnLayoutA, cl=True, cll=True, label='Step 4   Transfer Blends', borderStyle='in' )
        self.columnlayoutC = pm.columnLayout()
        #self.dockControl = pm.dockControl(label=title, area='right', content=title, allowedArea=['right', 'left'], sizeable=True)
        
        # fameA content
        self.names = {'Target':None}
        
        # Generating x number of fields based on dictionary keys of self.names
        for name in self.names:
            self.names[name] = pm.textFieldButtonGrp(cw = ((1, 76), (2, 176)), parent=self.frameLayoutA,
                                                     label = name, 
                                                     placeholderText = 'Enter Name Here   or   >>>> ',
                                                     buttonLabel = 'load selected', tcc= self.prepTargetMeshOn,
                                                     buttonCommand = pm.Callback(self.nameField_load, name))
        self.btn_prepTgt = pm.button(parent=self.frameLayoutA, enable=False, w=40, h=20, label="Prep Target", command=self.prepTargetMesh)
        self.fA_fillText = pm.text(parent=self.frameLayoutA, label='    ' )
            
        # fameB content
        self.importText = pm.text(parent=self.frameLayoutB, label='Import the desired facial mask' )
        self.manipulateText = pm.text(parent=self.frameLayoutB, label='Use the avalable controls to manipulate the mask' )
        self.fitText = pm.text(parent=self.frameLayoutB, label='Roughly fit the mask to the target mesh' )
        self.btn_trueHuman = pm.button(parent=self.frameLayoutB, enable=True, w=40, h=20, label="Human Anatomy", command=self.humanAnatomyImport)  
        self.btn_trueMuzzle = pm.button(parent=self.frameLayoutB, enable=False, w=40, h=20, label="Muzzle Anatomy", command=self.muzzleAnatomyImport)
        self.btn_toonHuman = pm.button(parent=self.frameLayoutB, enable=False, w=40, h=20, label="Human Toon", command=self.humanToonImport)  
        self.btn_toonMuzzle = pm.button(parent=self.frameLayoutB, enable=False, w=40, h=20, label="Muzzle Toon", command=self.muzzleToonImport)
        self.fB_fillText = pm.text(parent=self.frameLayoutB, label='    ' )
        
        # fameC content
        self.matchMeshText = pm.text(parent=self.frameLayoutC, label='activate match mesh and refine your geometry to better match the target' )
        self.btn_trueHuman = pm.button(parent=self.frameLayoutC, enable=True, w=40, h=20, label="Activate Match Mesh", command=self.matchMesh)
        self.btn_templateHuman = pm.button(parent=self.frameLayoutC, enable=True, w=40, h=20, label="template Target Mesh", command=self.tempTgt)
        self.btn_referenceHuman = pm.button(parent=self.frameLayoutC, enable=True, w=40, h=20, label="reference Target Mesh", command=self.refTgt)
        self.sldr_smooth = pm.intSliderGrp(parent=self.frameLayoutC, field=True, label='Match Mesh Divisions', minValue=-0, maxValue=4, fieldMinValue=-0, fieldMaxValue=4, value=0, cc=self.div_Slider_change)
        self.fC_fillText = pm.text(parent=self.frameLayoutC, label='    ' )
        
        # fameD content
        self.btn_go = pm.button(parent=self.frameLayoutD, enable=True, w=40, h=20, label="Transfer Shapes", command=self.execute)  
        self.btn_no = pm.button(parent=self.frameLayoutD, enable=True, w=40, h=20, label="NO DONT DO IT!", command=self.close)
        self.fE_fillText = pm.text(parent=self.frameLayoutD, label='    ' )
        self.win.show()
        if debug:
            test = ['mask_blendPipe_GEO', 'mask_hiRes_GEO']
            for name, test_val in zip(self.names, test):
                self.names[name].setText(test_val)

    def nameField_load(self, *args):
        """ This function will return the blendShapes on the source mesh
        Args:
            None
        Returns (None)
        """
        cur_btn = self.names[args[0]]
        selection = pm.selected()
        if len(selection) > 1:
            cur_btn.setText("Too many objects selected") 
        elif len(selection) < 1:
            cur_btn.setText("Nothing selected")
        else:
            cur_btn.setText(selection[0])

    def prepTargetMeshOn(self, btn):
        """ This function can execute all functions related to activating the Prep Mesh Button
        Args:
            None
        Returns (None)
        """
        self.btn_prepTgt.setEnable(True)

    def prepTargetMesh(self, btn,):
        """ This function can execute all functions related to preparing the target mesh
        Args:
            None
        Returns (None)
        """
        print 'SWEET THAT MESH IS PREPED'
        #TODO: add clean duplicate function
        target = self.names['Target'].getText()
        tgt_dup = self.get_dup_name(target)
        
        pm.duplicate(target, n=self.get_dup_name(target))
        pm.setAttr(target+'.visibility', 0)
        pm.setAttr(tgt_dup+'.overrideEnabled', 1)
        pm.setAttr(tgt_dup+'.overrideDisplayType', 2)
        pm.parent(tgt_dup, w=True)
                
    def humanAnatomyImport(self, btn):
        """ This function can execute all functions related to importing the human anatomy shaping mesh
        Args:
            None
        Returns (None)
        """
        print 'YOU DID IT ENJOY THAT HUMAN ANATOMY!'
        path = '/jobs/tvcUsers2015/michael-ni/michael-ni_sequence/maya/scenes/model/blendShapeMask_RnD/skinMask_Import_v002_man.ma'
        importHuman = pm.createReference(path, type="mayaAscii", ignoreVersion=True, gl=True, loadReferenceDepth = "all", mergeNamespacesOnClash = False, namespace = "tempMask")

    def muzzleAnatomyImport(self, btn):
        """ This function can execute all functions related to importing the muzzle anatomy shaping mesh
        Args:
            None
        Returns (None)
        """
        print 'YOU DID IT ENJOY THAT MUZZLE ANATOMY!'
        
    def humanToonImport(self, btn):
        """ This function can execute all functions related to importing the toon human shaping mesh
        Args:
            None
        Returns (None)
        """
        print 'YOU DID IT ENJOY THAT TOONY HUMAN!'
        
    def muzzleToonImport(self, btn):
        """ This function can execute all functions related to importing the toon muzzle shaping mesh
        Args:
            None
        Returns (None)
        """
        print 'YOU DID IT ENJOY THAT TOONY MUZZLE!'
        
    def matchMesh(self, btn):
        """ This function can execute all functions related to creating a match mesh
        Args:
            None
        Returns (None)
        """
        smoothMesh = self.get_smooth_mesh()
        skinMesh = self.get_skin_mesh()
        pm.hide(skinMesh)
        pm.showHidden(smoothMesh)
        print smoothMesh
        print 'YOU DID IT NOW MATCH THAT MESH!'
        
    def tempTgt(self, btn):
        """ This function can execute all functions related to creating a match mesh
        Args:
            None
        Returns (None)
        """
        target = self.names['Target'].getText()
        tgt_dup = self.get_dup_name(target)
        pm.setAttr(tgt_dup+'.overrideEnabled', 1)
        pm.setAttr(tgt_dup+'.overrideDisplayType', 1)
        print 'Sweet That Mesh is Templated!'
        
    def refTgt(self, btn):
        """ This function can execute all functions related to creating a match mesh
        Args:
            None
        Returns (None)
        """
        print 'Sweet That Mesh is Referenced!'        

    def div_Slider_change(self, btn,):
        """ This function can execute all functions related to changing the smooth mesh division levels
        Args:
            None
        Returns (None)
        """
        sldrVal = pm.intSliderGrp(self.sldr_smooth, query=True, value=True)
        smooth_node = self.get_smooth_node()
        pm.setAttr(smooth_node+'.divisions', sldrVal)
        print smooth_node
        print 'Slide those divisions'  
        
    def execute(self, btn):
        """ This function can execute all functions related to blendTransfer
        Args:
            None
        Returns (None)
        """
        target = self.get_target_mesh()
        source = self.get_source_mesh()
        print target, type(target)
        print source, type(source)
        print 'WHAT!!!'
        pm.select(clear= True)
        # First store the GUI objects then wrap them
        wrapTgt.wrap_target(source, target)
        
        # Now get the blendshape and create the new shapes based on the alias list on the target
        blend, shapes = self.get_blendshapes(source)
        self.create_newShapes(blend, shapes, target)
        pm.select(clear= True)

    def close(self, btn):
        """ This function can Close the UI
        Args:
            None
        Returns (None)
        """
        if kwargs.get('debug'):
            print "NO STOP IT!!!"
        pm.deleteUI(self.win)

    def get_target_mesh(self):
        """ Returns the text from both the target and source fields as PyNodes
        Args:
            None
        Returns [pm.nt.Transform, pm.nt.Transform]: list of 2 transforms for source and target respectively
                                                    None for either if either does not exist
        """
        #for transform in transform if transform.shape
        tgt_str = self.names['Target'].getText()
        target = None
        if pm.objExists(tgt_str):
            target = pm.PyNode(tgt_str)
        return target

    def get_source_mesh(self):
        """ Returns the name of the parellel blend mesh
        Args:
            None
        Returns (string)
        """
        try:
            min_blend = min([blend for blend in pm.ls(type='blendShape')], key=lambda x: len(x.listAliases()))
            return min_blend.listConnections(type='mesh')[0] or None
        except ValueError:
            print "Sorry, no blends in scene"

    def get_smooth_node(self):
        """ This function will return the blendShapes on the source mesh
        Args:
            None
        Returns (None)
        """
        try:
            smoothNode = min([mesh for mesh in pm.ls(type='polySmoothFace')])
            return smoothNode
        except ValueError:
            print "Sorry, no smoothed mesh in scene"

    def get_smooth_mesh(self):
        """ This function will return the blendShapes on the source mesh
        Args:
            None
        Returns (None)
        """
        try:
            smoothMesh = min([mesh for mesh in pm.ls(type='polySmoothFace')], key=lambda x: len(x.listAliases()))
            return smoothMesh.listConnections(type='mesh')[0] or None
        except ValueError:
            print "Sorry, no smoothed mesh in scene"

    def get_skin_mesh(self):
        """ This function will return the blendShapes on the source mesh
        Args:
            None
        Returns (None)
        """
        try:
            skinMesh = min([mesh for mesh in pm.ls(type='skinCluster')], key=lambda x: len(x.listAliases()))
            return skinMesh.listConnections(type='mesh')[0] or None
        except ValueError:
            print "Sorry, no skined mesh in scene"      
    
    def get_dup_name(self, dag_name):
        """ This function can execute all functions related to preparing the target mesh
        Args:
            dag_name (str): DAG name of object you want to rename
        Returns (str): the resulting name
        """
        dup_suffix = 'dup_GEO'
        name_changed = False
        for suffix in self.suffixes:
            if suffix in dag_name:
                return dag_name.replace(suffix, dup_suffix)
        return dag_name + dup_suffix

    @staticmethod
    def get_blendshapes(source):
        """ This function will find the blendShapes on the source mesh
        Args:
            None
        Returns [pm.nt.BlendShape]: list of blendshapes attached to source mesh
        """
        facial_shapes = max([blend for blend in pm.ls(type='blendShape')], key=lambda x: len(x.listAliases()))
        shapes = pm.listAttr(facial_shapes + '.w', m=True)
        return [facial_shapes, shapes]
        
    
    @staticmethod
    def create_newShapes(facial_shapes, shapes, target):
        """ This function will duplicate the target mesh creating new blendshapes based on source shapes
        Args:
            None
        Returns (None)
        """
        newShapesGrp = pm.group(n= 'newShapes_GRP')
        for i, shape in enumerate(shapes):
            pm.setAttr(facial_shapes + '.' + shape, 1)
            newShape = pm.duplicate(target, n= shape)
            pm.setAttr(shape + '.translateX', (i * 3 + 3) )
            pm.setAttr(facial_shapes + '.' + shape, 0)
            pm.parent(shape, newShapesGrp)

if __name__ == '__main__':
    my_ui = blend_transfer()