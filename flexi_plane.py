#!/usr/bin/env python
"""
    :module: flexi_plane
    :platform: Maya
    :synopsis: This module has the nessacery components to create a flexi plane rig module
    :plans: clean up code (anotate, convert to pymel)
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import aw.maya
import pymel.core as pm
import Rigging.offSetGRP as offSetGRP
import Rigging.conGRP as conGRP
import Rigging.newPosition as nPos
import maya.mel as mel


class flexi_planeUI(object):
    """ View -- contains user interface
    """
    def __init__(self):
        title="flexi_plane"
        if(pm.windowPref(title, q=True, ex=True)):
            pm.windowPref(title, remove=True)
        if(pm.window(title, q=True, ex=True)):
            pm.deleteUI(title)
        # flexi plane UI
        self.win = pm.window(title, title="flexi plane")
        self.layout = pm.rowColumnLayout()
        self.flexiPlaneNumSlider = pm.intSliderGrp(enable=True, field=True, label='number of joints', minValue=3, maxValue=100, fieldMinValue=3, fieldMaxValue=100, value=5,)
        self.flexiPlaneNameField = pm.textFieldGrp(parent=self.layout,enable=True, label='Name Flexi Plane Module', placeholderText="name your flexi plane", editable=True, tcc=self.flexiPlaneNameField_change)
        self.goBtn = pm.button(parent=self.layout, enable=False,w = 100, h = 24, label="GO!", command=self.execute)  
        self.noBtn = pm.button(parent=self.layout, enable=False,w = 100, h = 24, label="NO DONT DO IT!", command=self.close)   
        self.format_string = "{PREFIX}_{INDEX}_{SUFFIX}"
        self.delete = []
        self.win.show()

  
    #enable UI parts  
    def flexiPlaneNameField_change(self, *args):
        """ This function can enable the execution buttons of the user interface
        Args:
            None
        Returns (None)
        """
        self.goBtn.setEnable(True)
        self.noBtn.setEnable(True)
    
    #Excecute UI selections    
    def execute(self, *args, **kwargs):
        """ This function can execute other functions based on user selection
        Args:
            None
        Returns (None)
        """
        new_crv_name = self.flexiPlaneNameField.getText() + '_CRV'
        if kwargs.get('debug'):
            print "GO!!!"
            
        self.build_plane()
        follicles = self.build_folicle()
        self.build_main_ctrl_crvs()
        self.build_surf_bShp()
        self.build_cluster_crv()
        self.build_wire_deform()
        self.connect_clust_2_crvs()
        self.build_tweek_ctrls(follicles)
        self.build_flexi_jnts(follicles)
        self.build_twist_deform()
        self.connect_twist_2_crvs()
        self.add_squash_n_stretch(follicles)
        self.skinConnect_globalPlane()
        self.clean_outliner()
        self.connect_parts_to_module()


    def close(self, *args, **kwargs):
        """ This function can Close the UI
        Args:
            None
        Returns (None)
        """
        if kwargs.get('debug'):
            print "NO STOP IT!!!"
        pm.deleteUI(self.win)

    def build_plane(self, *args):
        """ builds Nurb plane based on joint slider
        Args:
            None
        Returns (None)
        """
        surface_name = self.flexiPlaneNameField.getText() + '_flexiPlane_SURF'
        num_nurb_patches = self.flexiPlaneNumSlider.getValue()
        nurb_plane_width = self.flexiPlaneNumSlider.getValue() * 2
        nurb_plane_length_ratio = float(2) / nurb_plane_width
        
        surface = pm.nurbsPlane(p= (0, 0, 0), ax= (0, 1, 0), w= nurb_plane_width, lr= nurb_plane_length_ratio, d= 3, u= num_nurb_patches, v= 1, n= surface_name, ch= 0)[0]
        surface_shape = surface.getShape()
        attrs = ['castsShadows', 'receiveShadows', 'motionBlur', 'primaryVisibility', 'smoothShading', 'visibleInReflections', 'visibleInRefractions']
        for attr in attrs:
            surface_shape.attr(attr).set(0)
        surface.setAttr('inheritsTransform', 0)
        return surface

    def build_folicle(self, *args):
        """ builds follicles on Nurb plane based on joint slider value
        Args:
            None
        Returns (None)
        """
        num_jnts_slider = self.flexiPlaneNumSlider.getValue()
        list_follicles=list(range(num_jnts_slider))
        surface = self.flexiPlaneNameField.getText() + '_flexiPlane_SURF'
        flcsGRP = self.flexiPlaneNameField.getText() + '_flexiPlane_FOL_GRP' 
        pm.group( em=True, name=flcsGRP )
        
        follicles = []
        for index,follicle in enumerate(list_follicles):
            follicle_shape = pm.createNode('follicle')
            follicle = follicle_shape.getParent()
            follicle_name = self.format_string.format(PREFIX = self.flexiPlaneNameField.getText(), 
                                                      INDEX = 'flexiPlane_fol%03d' % (index+1), 
                                                      SUFFIX = 'FOL')        
            follicle_num = float(index)
            uVal = follicle_num / float(num_jnts_slider)
            offset = 1 / float(num_jnts_slider) * .5
            u= uVal + offset
            v= 0.5 
            
            pm.rename(follicle, follicle_name)
            pm.connectAttr(surface + 'Shape.local', follicle_shape.inputSurface)
            pm.connectAttr(surface + 'Shape.worldMatrix[0]', follicle_shape.inputWorldMatrix)
            follicle_shape.outRotate.connect(follicle.rotate)
            follicle_shape.outTranslate.connect(follicle.translate)
            follicle_shape.parameterU.set(u)
            follicle_shape.parameterV.set(v)
            pm.parent( follicle_name, flcsGRP )
            pm.setAttr( follicle_name + 'Shape.visibility', 0)
            follicles.append(follicle)
        return follicles
        
    def build_main_ctrl_crvs(self, *args):
        """ builds connect control curves to manipulate the flexi plane surface
        Args:
            None
        Returns (None)
        """
        # name variables
        num_jnts_slider = self.flexiPlaneNumSlider.getValue()
        crvA_name = self.flexiPlaneNameField.getText() + '_flexiPlane_connectA_CTRL'
        crvB_name = self.flexiPlaneNameField.getText() + '_flexiPlane_connectB_CTRL'
        crvMid_name = self.flexiPlaneNameField.getText() + '_flexiPlane_mid_CTRL'
        crvMain_name = self.flexiPlaneNameField.getText() + '_flexiPlane_main_CTRL'
        controlGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_CTRL_GRP'
        
        # value variables
        crvA_pos = num_jnts_slider * -1
        crvB_pos = num_jnts_slider
        
        #create control crvs
        pm.curve( n = crvA_name, d = 1, 
                                 p = [( -0.5, 0, 0.5 ), ( 0.5, 0, 0.5 ), ( 0.5, 0, -0.5 ), ( -0.5, 0, -0.5 ), ( -0.5, 0, 0.5 )], 
                                 k = [0, 1, 2, 3, 4] )
        pm.curve( n = crvB_name, d = 1, 
                                 p = [( -0.5, 0, 0.5 ), ( 0.5, 0, 0.5 ), ( 0.5, 0, -0.5 ), ( -0.5, 0, -0.5 ), ( -0.5, 0, 0.5 )], 
                                 k = [0, 1, 2, 3, 4] )
        pm.curve( n = crvMid_name, d = 1, 
                                 p = [( -0.25, 0.25, -0.25 ), ( -0.25, 0.25, 0.25 ), ( 0.25, 0.25, 0.25 ), ( 0.25, 0.25, -0.25 ), ( -0.25, 0.25, -0.25 ),
                                      ( -0.25, -0.25, -0.25 ), ( 0.25, -0.25, -0.25 ), ( 0.25, 0.25, -0.25 ), ( 0.25, 0.25, 0.25 ), ( 0.25, -0.25, 0.25 ),
                                      ( -0.25, -0.25, 0.25 ), ( -0.25, 0.25, 0.25 ), ( -0.25, 0.25, -0.25 ), ( -0.25, -0.25, -0.25 ), ( -0.25, -0.25, 0.25 ),
                                      ( 0.25, -0.25, 0.25 ), ( 0.25, 0.25, 0.25 )], 
                                 k = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] )
        pm.circle( c = (0, 0, 0 ), nr = ( 0, 1, 0 ), sw = 360, r = 1, d = 3, ut = 0, tol = 0.000129167, s = 8, n = crvMain_name,ch = 0 )
        
        #color and move and set rotation order for crvA
        pm.setAttr( crvA_name + '.overrideEnabled', 1 )
        pm.setAttr( crvA_name + '.overrideColor', 17 )
        pm.setAttr( crvA_name + '.translateX', crvA_pos )
        pm.makeIdentity( crvA_name, apply=True, translate=True, rotate=True, scale=True )
        
        #color and move and set rotation order for crvB
        pm.setAttr( crvB_name + '.overrideEnabled', 1 )
        pm.setAttr( crvB_name + '.overrideColor', 17 )
        pm.setAttr( crvB_name + '.translateX', crvB_pos )
        pm.makeIdentity( crvB_name, apply=True, translate=True, rotate=True, scale=True )
        
        #color and scale mid crv
        pm.setAttr( crvMid_name + '.overrideEnabled', 1 )
        pm.setAttr( crvMid_name + '.overrideColor', 17 )
        pm.setAttr( crvMid_name + '.scaleX', 2 )
        pm.setAttr( crvMid_name + '.scaleY', 2 )
        pm.setAttr( crvMid_name + '.scaleZ', 2 )
        pm.makeIdentity( crvMid_name, apply=True, translate=True, rotate=True, scale=True )
        
        #color and size, and move main crv
        pm.setAttr( crvMain_name + '.overrideEnabled', 1 )
        pm.setAttr( crvMain_name + '.overrideColor', 17 )
        pm.setAttr( crvMain_name + '.scaleX', 0.25 )
        pm.setAttr( crvMain_name + '.scaleY', 0.25 )
        pm.setAttr( crvMain_name + '.scaleZ', 0.25 )
        pm.setAttr( crvMain_name + '.translateZ', -2 )
        pm.makeIdentity( crvMain_name, apply=True, translate=True, rotate=True, scale=True )
        pm.move( 0, 0, 0,  crvMain_name + '.scalePivot', crvMain_name + '.rotatePivot', ws = True )
        
        #create  and move second shape for main crv
        pm.duplicate( crvMain_name, n = crvMain_name + 'Dup' )
        pm.setAttr( crvMain_name + 'Dup.translateZ', 4 )
        pm.makeIdentity( crvMain_name + 'Dup', apply=True, translate=True, rotate=True, scale=True )
        
        #add squash -n- stretch attribute
        pm.select( crvMain_name, r = True )
        pm.addAttr( ln = 'squashN_stretch', at = 'enum', en = 'disable:enable:', keyable = True )
        pm.select( cl = True )
        
        pm.parent( crvMain_name + 'DupShape', crvMain_name, add = True, shape = True )
        pm.delete( crvMain_name + 'Dup' )
              
        pm.select(crvA_name, r=True)
        offSetGRP.add_offset_grps()
        conGRP.add_con_grps()
        
        pm.select(crvB_name, r=True)
        offSetGRP.add_offset_grps()
        conGRP.add_con_grps()
        
        pm.select(crvMid_name, r=True)
        offSetGRP.add_offset_grps()
        conGRP.add_con_grps()
        
        pm.select(crvMain_name, r=True)
        offSetGRP.add_offset_grps()
        conGRP.add_con_grps()
        pm.select(clear = True)
        
        pm.group( em = True, name = controlGRP_name )
        pm.parent( crvA_name + 'Offset_GRP', crvMain_name + 'Con_GRP' )
        pm.parent( crvB_name + 'Offset_GRP', crvMain_name + 'Con_GRP' )
        pm.parent( crvMid_name + 'Offset_GRP', crvMain_name + 'Con_GRP' )
        pm.parent( crvMain_name + 'Offset_GRP', controlGRP_name )
        
        pm.pointConstraint( crvA_name + 'Con_GRP', crvB_name + 'Con_GRP', crvMid_name + 'Offset_GRP' )
        

    def build_surf_bShp(self, *args):
        """ builds a blendShape surface and blendShape node to add deformations
        Args:
            None
        Returns (None)
        """
        surf_name = self.flexiPlaneNameField.getText() + '_flexiPlane_SURF'
        surf_wirebShp_name = self.flexiPlaneNameField.getText() + '_flexiPlane_wire_bShp_SURF'
        surf_bShpNode_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShpNode_SURF'
        surf_tweekNode_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_SURF_tweak01'
        surf_bShpGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_GRP'
        
        pm.duplicate( surf_name, n = surf_wirebShp_name)
        pm.blendShape( surf_wirebShp_name, surf_name, n = surf_bShpNode_name, w = [(0, 1), (1,1)] )
        
        list = pm.listConnections( surf_name + 'Shape' )
        pm.rename( list[-1] , surf_tweekNode_name )
        
        pm.group( em = True, name = surf_bShpGRP_name )
        pm.parent(surf_wirebShp_name, surf_bShpGRP_name )
        
        pm.setAttr( surf_bShpGRP_name + '.visibility', 0 )
        
    def build_cluster_crv(self, *args):
        """ builds a curve with 3 cv's controled by clusters
        Args:
            None
        Returns (None)
        """
        crv_name = self.flexiPlaneNameField.getText() + '_flexiPlane_wire_CRV'
        surf_bShp_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_SURF'
        clusterA_name = self.flexiPlaneNameField.getText() + '_flexiPlane_clustA_CL'
        clusterB_name = self.flexiPlaneNameField.getText() + '_flexiPlane_clustB_CL'
        clusterC_name = self.flexiPlaneNameField.getText() + '_flexiPlane_clustC_CL'
        clusterGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_CLSTR_GRP'
        surf_bShpGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_GRP'
        num_jnts_slider = self.flexiPlaneNumSlider.getValue()
        cvA_pos = num_jnts_slider * -1
        cvC_pos = num_jnts_slider
        
        pm.curve( n = crv_name, d = 2, 
                            p = [( cvA_pos, 0, 0 ), ( 0, 0, 0 ), ( cvC_pos, 0, -0 )], 
                            k = [0, 0, 1, 1] )
        
        pm.select( crv_name +'.cv[0:1]', r = True )
        pm.cluster( n = clusterA_name, en = 1, rel = True )
        pm.setAttr( clusterA_name + 'Handle.originX', cvA_pos )
        pm.move( cvA_pos, 0, 0,  clusterA_name + 'Handle.scalePivot', clusterA_name + 'Handle.rotatePivot', ws = True )
        
        pm.select( crv_name +'.cv[1:2]', r = True )
        pm.cluster( n = clusterC_name, en = 1, rel = True )
        pm.setAttr( clusterC_name + 'Handle.originX', cvC_pos )
        pm.move( cvC_pos, 0, 0,  clusterC_name + 'Handle.scalePivot', clusterC_name + 'Handle.rotatePivot', ws = True )
        
        pm.select( crv_name +'.cv[1]', r = True )
        pm.cluster( n = clusterB_name, en = 1, rel = True )
        
        pm.select( crv_name +'.cv[1]', r = True )
        pm.percent( clusterA_name, crv_name +'.cv[1]', v = 0.5 )
        pm.percent( clusterC_name, crv_name +'.cv[1]', v = 0.5 )
        
        pm.group( em = True, name = clusterGRP_name )
        pm.parent(clusterA_name + 'Handle', clusterGRP_name )
        pm.parent(clusterB_name + 'Handle', clusterGRP_name )
        pm.parent(clusterC_name + 'Handle', clusterGRP_name )
        
        pm.parent(clusterGRP_name, surf_bShpGRP_name )
        
        
    def build_wire_deform(self, *args):
        """ builds a curve with 3 cv's controled by clusters
        Args:
            None
        Returns (None)
        """
        crv_name = self.flexiPlaneNameField.getText() + '_flexiPlane_wire_CRV'
        surf_wirebShp_name = self.flexiPlaneNameField.getText() + '_flexiPlane_wire_bShp_SURF'
        surf_bShp_tweekNode_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_SURF_tweak02'
        wireNode_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_wireNode_SURF'
        surf_bShpGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_GRP'
        
        wire_deformer = mel.eval("wire -gw false -en 1.000000 -ce 0.000000 -li 0.000000 -w " + crv_name + " " + surf_wirebShp_name +";")[0]
        
        wireSurf_inputList = pm.listConnections( surf_wirebShp_name + 'Shape' )
        pm.rename( wireSurf_inputList[-1] , surf_bShp_tweekNode_name )
        pm.rename( wireSurf_inputList[-3] , wireNode_name )
        pm.wire( wireNode_name, edit=True, dds = (0, 20.000000) )
        
        pm.parent( crv_name, surf_bShpGRP_name )
        pm.parent( crv_name + 'BaseWire', surf_bShpGRP_name )
        
        pm.select( cl = True )

        
    def build_twist_deform(self, *args):
        """ builds a curve with 3 cv's controled by clusters
        Args:
            None
        Returns (None)
        """
        surf_wireShp_name = self.flexiPlaneNameField.getText() + '_flexiPlane_wire_bShp_SURF'
        wireNode_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_wireNode_SURF'
        twistNode_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_twistNode_SURF'
        twistHandle_name = self.flexiPlaneNameField.getText() + '_flexiPlane_twist_Handle'
        surf_bShpGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_GRP'
        
        pm.select( surf_wireShp_name, r = True )
        twist_deformer = mel.eval("nonLinear -type twist -lowBound -1 -highBound 1 -startAngle 0 -endAngle 0;")[0]
        
        twistSurf_inputList = pm.listConnections( surf_wireShp_name + 'Shape' )
        pm.rename( twistSurf_inputList [-3] , twistNode_name )
        
        twistNode_inputList = pm.listConnections( twistNode_name )
        pm.rename( twistNode_inputList [-1] , twistHandle_name )
        pm.setAttr( twistHandle_name + '.rotateZ', 90 )
        pm.reorderDeformers( wireNode_name, twistNode_name, surf_wireShp_name )
        pm.parent( twistHandle_name, surf_bShpGRP_name )
        
        pm.select( cl = True )

    def connect_clust_2_crvs(self, *args):
        """ builds a curve with 3 cv's controled by clusters
        Args:
            None
        Returns (None)
        """
        crv_base = '%s_flexiPlane' % self.flexiPlaneNameField.getText()
        crvA_name =  '%s_connectA_CTRL' % crv_base
        crvB_name = '%s_connectB_CTRL' % crv_base
        crvMid_name = '%s_mid_CTRL' % crv_base
        clusterA_name = '%s_clustA_CL' % crv_base
        clusterB_name = '%s_clustB_CL' % crv_base
        clusterC_name = '%s_clustC_CL' % crv_base
        
        pm.connectAttr( crvA_name + '.translate', clusterA_name + 'Handle.translate' )
        pm.connectAttr( crvB_name + '.translate', clusterC_name + 'Handle.translate' )
        
        pm.select(clusterB_name + 'Handle', r=True)
        offSetGRP.add_offset_grps()
        
        pm.pointConstraint( clusterA_name + 'Handle', clusterC_name + 'Handle', clusterB_name + 'HandleOffset_GRP' )
        pm.connectAttr( crvMid_name + '.translate', clusterB_name + 'Handle.translate' )
        
    def connect_twist_2_crvs(self, *args):
        """ builds a curve with 3 cv's controled by clusters
        Args:
            None
        Returns (None)
        """
        base_name = '%s_flexiPlane' % self.flexiPlaneNameField.getText()
        crvA_name =  '%s_connectA_CTRL' % base_name
        crvB_name = '%s_connectB_CTRL' % base_name
        main_crv_name =  '%s_main_CTRL' % base_name
        twistHandle_name = '%s_twist_Handle' % base_name
        surf_bShpGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_bShp_GRP'
        
        twistA_LOC = pm.spaceLocator( n = '%s_twistA_LOC' % base_name )
        twistB_LOC = pm.spaceLocator( n = '%s_twistB_LOC' % base_name )
        
        pm.parentConstraint ( crvA_name, twistA_LOC, w = 1 )
        pm.parentConstraint ( crvB_name, twistB_LOC, w = 1 )
        
        pm.connectAttr( twistA_LOC + '.rotateX', twistHandle_name + '.endAngle', f = True )
        pm.connectAttr( twistB_LOC + '.rotateX', twistHandle_name + '.startAngle', f = True )
        
        pm.parent( twistA_LOC , surf_bShpGRP_name )
        pm.parent( twistB_LOC , surf_bShpGRP_name )

    def build_tweek_ctrls(self, follicles):
        """ 
        Args:
            None
        Returns (None)
        """
        base_name = '%s_flexiPlane' % self.flexiPlaneNameField.getText()
        follicle_prefix = '%s_flexiPlane_' % self.flexiPlaneNameField.getText()
        mainCTRLGRP = self.flexiPlaneNameField.getText() + '_flexiPlane_main_CTRLCon_GRP'
        main_crv_name =  '%s_main_CTRL' % base_name
        tweekCTRLGRP = pm.group( em = True, name = self.flexiPlaneNameField.getText() + '_flexiPlane_tweakCTRL_GRP' )
        tweekCTRLGRP.setAttr( 'inheritsTransform', 0 )
        pm.parent( tweekCTRLGRP, mainCTRLGRP )
        

        for index,follicle in enumerate(follicles):
            tweek_crv_name = self.format_string.format(PREFIX = self.flexiPlaneNameField.getText(),
                                                 INDEX = 'flexiPlane_tweak%03d' % (index+1),
                                                 SUFFIX = 'CTRL')
            pm.circle( c = (0, 0, 0 ), nr = ( 0, 1, 0 ), sw = 360, r = 1, d = 3, ut = 0, tol = 0.000129167, s = 8, n = tweek_crv_name, ch = 0 )
            pm.setAttr( tweek_crv_name + '.scaleX', .5 )
            pm.setAttr( tweek_crv_name + '.scaleY', .5 )
            pm.setAttr( tweek_crv_name + '.scaleZ', .5 )
            pm.setAttr( tweek_crv_name + '.overrideEnabled', 1 )
            pm.setAttr( tweek_crv_name + '.overrideColor', 17 )
            pm.makeIdentity( tweek_crv_name, apply=True, translate=True, rotate=True, scale=True )
            pm.setAttr( tweek_crv_name + '.overrideEnabled', 1 )
            pm.setAttr( tweek_crv_name + '.overrideColor', 17 )
            
            pm.duplicate( tweek_crv_name, n= tweek_crv_name + 'A' )
            pm.setAttr( tweek_crv_name + 'A.rotateZ', -90 )
            pm.makeIdentity( tweek_crv_name + 'A', apply=True, translate=True, rotate=True, scale=True )
            
            pm.duplicate( tweek_crv_name, n= tweek_crv_name + 'B' )
            pm.setAttr( tweek_crv_name + 'B.rotateZ', -90 )
            pm.setAttr( tweek_crv_name + 'B.rotateX', -90 )
            pm.makeIdentity( tweek_crv_name + 'B', apply=True, translate=True, rotate=True, scale=True )
            
            pm.parent( tweek_crv_name + 'AShape', tweek_crv_name + 'BShape', tweek_crv_name, add = True, shape = True )
            pm.delete( tweek_crv_name + 'A', tweek_crv_name + 'B')
            
            pm.select(tweek_crv_name, r=True)
            offSetGRP.add_offset_grps()
            conGRP.add_con_grps()
            pm.select(clear = True)
            
            pm.connectAttr( follicle + '.translate', tweek_crv_name + 'Offset_GRP.translate' )
            pm.connectAttr( follicle + '.rotate', tweek_crv_name + 'Offset_GRP.rotate' )
            pm.parent( tweek_crv_name + 'Offset_GRP', tweekCTRLGRP )
            pm.scaleConstraint( main_crv_name, tweek_crv_name + 'Offset_GRP' )
 
            pm.select( clear = True)


    def build_flexi_jnts(self, follicles):
        """ 
        Args:
            None
        Returns (None)
        """
        follicle_prefix = '%s_flexiPlane_' % self.flexiPlaneNameField.getText()
        jntGRP_name = self.flexiPlaneNameField.getText() + '_flexiPlane_JNT_GRP'
        
        pm.group( em = True, name = jntGRP_name )
        
        for index,follicle in enumerate(follicles):
            jnt_name = self.format_string.format(PREFIX = self.flexiPlaneNameField.getText(),
                                                 INDEX = 'flexiPlane_jnt%03d' % (index+1),
                                                 SUFFIX = 'JNT')
            jnt_offset_name = jnt_name.replace('_JNT','Offset_GRP')
            tweek_ctrlCon_name = self.format_string.format(PREFIX = self.flexiPlaneNameField.getText(),
                                                 INDEX = 'flexiPlane_tweak%03d' % (index+1),
                                                 SUFFIX = 'CTRLCon_GRP')

            pm.joint( p = ( follicle.translateX.get(), 0, 0 ), n = jnt_name )
            pm.select(jnt_name, r=True)
            offSetGRP.add_offset_grps()
            
            pm.parent( jnt_offset_name, jntGRP_name )
            pm.select( clear = True )
            
            tweak_ctrl_con = pm.PyNode(tweek_ctrlCon_name)
            joint_offset = pm.PyNode(jnt_offset_name)
            
            pm.parentConstraint( tweek_ctrlCon_name, jnt_offset_name )
            
            pm.setAttr(jnt_name + '.rotateZ', -90)
            pm.makeIdentity( jnt_name, apply=True, translate=True, rotate=True )

    
    @staticmethod        
    def name_cleaner(name):
        # Check for offset group naming
        if '_Offset' in name:
            name = name.replace('_Offset','Offset')
        # Check for preceeding underscore
        if name[0] == '_':
            name = name[1:]
        # Check for succeeding underscore
        if name[-1] == '_':
            name = name[:-1]
        # Check for double underscores
        previous = ''
        checked_name = ''
        for char in name:
            if not (char + previous) == '__':
                checked_name+=char
            previous = char
        return checked_name
    
    def add_squash_n_stretch(self, follicles):
        """ 
        Args:
            None
        Returns (None)
        Usage:
        """
        base_name = '%s_flexiPlane' % self.flexiPlaneNameField.getText()
        wire_name =  '%s_wire_CRV' % base_name
        main_crv_name =  '%s_main_CTRL' % base_name
        
        wire = pm.PyNode(wire_name)
        
        arc_len = pm.arclen(wire, ch = True)
        pm.rename( arc_len, wire_name + 'info' )
        arc_len_val = pm.getAttr( wire_name + 'info.arcLength')
        
        multDiv_length = pm.shadingNode( 'multiplyDivide', asUtility = True )
        pm.rename( multDiv_length, base_name  + '_div_squashStretch_length' )
        pm.setAttr( base_name  + '_div_squashStretch_length.operation', 2 )
        
        pm.connectAttr( wire_name + 'info.arcLength', base_name  + '_div_squashStretch_length.input1X' )
        pm.setAttr( base_name  + '_div_squashStretch_length.input2X', arc_len_val )
        
        multDiv_volume = pm.shadingNode( 'multiplyDivide', asUtility = True )
        pm.rename( multDiv_volume, base_name  + '_div_volume' )
        pm.setAttr( base_name  + '_div_volume.operation', 2 )
        pm.setAttr( base_name  + '_div_volume.input1X', 1 )
        
        pm.connectAttr( base_name  + '_div_squashStretch_length.outputX', base_name  + '_div_volume.input2X', f = True )
        
        conditional_volume = pm.shadingNode( 'condition', asUtility = True )
        pm.rename( conditional_volume, base_name  + '_cond_volume' )
        pm.setAttr( base_name  + '_cond_volume.secondTerm', 1 )
        pm.connectAttr( main_crv_name + '.squashN_stretch', base_name  + '_cond_volume.firstTerm' )

        multDiv_globelScale = pm.shadingNode( 'multiplyDivide', asUtility = True )
        pm.rename( multDiv_globelScale, base_name  + '_mult_globalScale' )
        pm.connectAttr( base_name  + '_div_volume.outputX', base_name  + '_mult_globalScale.input1X' )
        pm.connectAttr( main_crv_name  + '.scaleX', base_name  + '_mult_globalScale.input2X' )
        pm.connectAttr( base_name  + '_mult_globalScale.outputX', base_name  + '_cond_volume.colorIfTrueR' )

        for index,follicle in enumerate(follicles):
            jnt_name = self.format_string.format(PREFIX = self.flexiPlaneNameField.getText(),
                                                 INDEX = 'flexiPlane_jnt%03d' % (index+1),
                                                 SUFFIX = 'JNT')
            jnt_offset_name = jnt_name.replace('_JNT','Offset_GRP')
            tweek_crv_name = self.format_string.format(PREFIX = self.flexiPlaneNameField.getText(),
                                                 INDEX = 'flexiPlane_tweak%03d' % (index+1),
                                                 SUFFIX = 'CTRL')
            
            pm.scaleConstraint( tweek_crv_name + 'Con_GRP', jnt_offset_name )
            pm.connectAttr( base_name  + '_cond_volume.outColorR', jnt_name + '.scaleX')
            pm.connectAttr( base_name  + '_cond_volume.outColorR', jnt_name + '.scaleZ')
            
            pm.select( clear = True )

    def skinConnect_globalPlane(self, *args):
        """ 
        Args:
            None
        Returns (None)
        Usage:
        """
        base_name = '%s_flexiPlane' % self.flexiPlaneNameField.getText()
        surface = '%s_SURF' % base_name
        surfaceSkinJNT = '%s_surfSkin_JNT' % base_name
        main_CTRLCon = '%s_main_CTRLCon_GRP' % base_name
        
        pm.joint( p = (0, 0, 0), a = True, n = surfaceSkinJNT )
        pm.parentConstraint( main_CTRLCon, surfaceSkinJNT )
        pm.skinCluster( surfaceSkinJNT, surface, bm = 0, sm = 0, nw = 1, wd = 0, mi = 1, omi = 1, dr = 4.0 )
        
    def clean_outliner(self, *args):
        """ 
        Args:
            None
        Returns (None)
        """
        base_name = '%s_flexiPlane' % self.flexiPlaneNameField.getText()
        surface =  '%s_SURF' % base_name
        surfaceSkinJNT = '%s_surfSkin_JNT' % base_name
        fol_grp =  '%s_FOL_GRP' % base_name
        ctrl_grp =  '%s_CTRL_GRP' % base_name
        jnt_grp =  '%s_JNT_GRP' % base_name
        bShp_grp =  '%s_bShp_GRP' % base_name
        
        flexi_GRP = pm.group( em = True, name = base_name + '_GRP' )
        parts_GRP = pm.group( em = True, name = base_name + '_parts_GRP' )
        
        pm.parent( surface, parts_GRP )
        pm.parent( surfaceSkinJNT, parts_GRP )
        pm.parent( fol_grp, parts_GRP )
        pm.parent( ctrl_grp, flexi_GRP )
        pm.parent( jnt_grp, flexi_GRP )
        pm.parent( bShp_grp, parts_GRP )
        pm.parent( parts_GRP, flexi_GRP )
        
        pm.setAttr( surface + '.visibility', 0)
        pm.select( cl = True )
        
    def connect_parts_to_module(self, *args):
        """ 
        Args:
            None
        Returns (None)
        """
        base_name = '%s_flexiPlane' % self.flexiPlaneNameField.getText()
        module_grp =  pm.PyNode('%s_GRP' % base_name)
        surface =  pm.PyNode('%s_SURF' % base_name)
        ctrl_grp =  pm.PyNode('%s_CTRL_GRP' % base_name)
        jnt_grp =  pm.PyNode('%s_JNT_GRP' % base_name)
        parts_grp =  pm.PyNode('%s_parts_GRP' % base_name)

        module_grp.addAttr( 'module', at = 'enum', en = 'Visibility', k = True )
        module_grp.setAttr( 'module', k = False, cb = True )
        module_grp.addAttr( 'modelVis', at = 'long', min = 0, max = 1, k = True )
        module_grp.setAttr( 'modelVis', k = False, cb = True )
        module_grp.addAttr( 'skeletonVis', at = 'long', min = 0, max = 1, k = True )
        module_grp.setAttr( 'skeletonVis', k = False, cb = True )
        module_grp.addAttr( 'controlVis', at = 'long', min = 0, max = 1, k = True )
        module_grp.setAttr( 'controlVis', 1, k = False, cb = True, )
        module_grp.addAttr( 'Module', at = 'enum', en = 'Type', k = True )
        module_grp.setAttr( 'Module', k = False, cb = True )
        module_grp.addAttr( 'modelType', at = 'enum', en = 'Normal:Template:Reference', k = True )
        module_grp.setAttr( 'modelType', 2, k = False, cb = True )
        module_grp.addAttr( 'skeletonType', at = 'enum', en = 'Normal:Template:Reference', k = True )
        module_grp.setAttr( 'skeletonType', 2, k = False, cb = True )
        module_grp.addAttr( 'controlType', at = 'enum', en = 'Normal:Template:Reference', k = True )
        module_grp.setAttr( 'controlType', k = False, cb = True )
        
        module_grp.modelVis.connect( surface.visibility )
        module_grp.skeletonVis.connect( jnt_grp.visibility )
        module_grp.skeletonVis.connect( parts_grp.visibility )
        module_grp.controlVis.connect( ctrl_grp.visibility )
        
        surface.setAttr( 'overrideEnabled', 1)
        module_grp.modelType.connect( surface.overrideDisplayType )
        jnt_grp.setAttr( 'overrideEnabled', 1)
        module_grp.skeletonType.connect( jnt_grp.overrideDisplayType )
        parts_grp.setAttr( 'overrideEnabled', 1)
        module_grp.skeletonType.connect( parts_grp.overrideDisplayType )
        ctrl_grp.setAttr( 'overrideEnabled', 1)
        module_grp.controlType.connect( ctrl_grp.overrideDisplayType )
        

if __name__ == '__main__':
    my_ui = flexi_planeUI()