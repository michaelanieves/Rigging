import pymel.core as pm

'''
Usage:
   add_offset_grps()
'''   

# create Offset Group for selected objects    
def add_offset_grps(*args):
    sel = pm.ls(sl=True)
    for obj in sel:
        offset_grp( obj )
        pm.select(clear= True)
        pm.select(sel, add= True)     

# Create Offset Group and parent selected object to group 
def offset_grp( transform, *args ):
    parent = transform.getParent()
    grp_name = add_offsetGrp_suffix(transform.name())
    child_pivot = transform.getScalePivot(space = 'world')
    grp = pm.group( n = grp_name, em=True )
    grp.setScalePivot( child_pivot )
    grp.setRotatePivot( child_pivot )

    if parent:
        grp.setParent( parent, a=True ) 
    
    transform.setParent( grp, r=True )
    
# Name Offset_GRP
def add_offsetGrp_suffix( name, *args ):
    suffixes = ['_GEO', '_FOL', '_IOM', '_INF', '_GRP', '_REF', '_BSP', '_BLD', '_CRV', '_JNT', '_LOC']
    grp_suffix = 'Offset_GRP'
    name_changed = False
    for suffix in suffixes:
        if suffix in name:
            name = name.replace( suffix, grp_suffix )
            name_changed = True
    if not name_changed:
        name += grp_suffix
    return name