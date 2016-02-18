#!/usr/bin/env python
"""
    :module: makeHalo
    :platform: Maya
    :synopsis: This module has the nessacery components to create a halo CTRL for a selected ctrl (eg.Global_CTRL)
    :plans: None
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm


class Make_haloUI(object):
    """ View -- contains user interface
    """
    def __init__(self):
        title="Make Halo"
        if(pm.windowPref(title, q=True, ex=True)):
            pm.windowPref(title, remove=True)
        if(pm.window(title, q=True, ex=True)):
            pm.deleteUI(title)
            
        #splineIK UI
        self.win = pm.window(title, title=title)
        self.layout = pm.rowColumnLayout()
        self.names = {'Halo Curve':None, 'Halo Parent':None, 'Control':None}
        for name in self.names:
            self.names[name] = pm.textFieldButtonGrp(cw= ((1, 76), (2, 176)), label= name, 
                                                     placeholderText= 'Enter New Name Here   or   >>>> ', buttonLabel= 'load selected', 
                                                     buttonCommand= pm.Callback( self.nameField_load, name))
        self.goBtn = pm.button(parent=self.layout, enable=True,w = 40, h = 20, label="Build", command=self.execute)  
        self.noBtn = pm.button(parent=self.layout, enable=True,w = 40, h = 20, label="NO DONT DO IT!", command=self.close)
        self.delete = []
        self.win.show()
            
    #Load curve Name Field
    def nameField_load(self, *args):
        """ This function will update the curve to be used
        Args:
            None
        Returns (None)
        """
        cur_btn = self.names[args[0]]
        selection = pm.ls(sl=True)
        if len(selection) > 1:
            print "Too many objects selected"
            cur_btn.setText("Too many objects selected")
 
        elif len(selection) < 1:
            print "Nothing Selected"
            cur_btn.setText("Nothing selected")
            
        else:
            print "Good job you have one object selected"
            cur_btn.setText(selection[0])
            
    #Excecute UI selections 
    def execute(self, *args, **kwargs):
            pass

    def close(self, *args, **kwargs):
        """ This function can Close the UI
        Args:
            None
        Returns (None)
        """
        if kwargs.get('debug'):
            print "NO STOP IT!!!"
        pm.deleteUI(self.win)
                
if __name__ == '__main__':
    my_ui = Make_haloUI()