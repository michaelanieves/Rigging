#!/usr/bin/env python
"""
    :module: crv_piv_start
    :platform: Maya
    :synopsis: This module places the piviot for selected curves at their cv0 
    :plans: None
"""
__author__ = "Michael Nieves"
__email__ = "michaelanieves@gmail.com"
__version__ = 1.0

import pymel.core as pm

def crv_piv_start(*args):
    """ This function can plave selected curves piviot at their cv0
    Args:
        None
    Returns:
        (None)
    usage:
        crv_piv_start()
    """
    crvs = pm.selected()
    for crv in crvs:
        pos = crv.getShape().getCV(0)
        crv.setPivots(pos)