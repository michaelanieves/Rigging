import pymel.core as pm

'''
Usage:
   under_locator()
'''   

# create Offset Group for selected objects    
def under_locator(*args):
    sel = pm.ls(sl=True)
    for obj in sel:
        offset_grp( obj )
        pm.select(clear= True)
        pm.select(sel, add= True)     

# Create Offset Group and parent selected object to group 
def offset_grp( transform, *args ):
    parent = transform.getParent()
    loc_name = add_loc_suffix(transform.name())
    child_pivot = transform.getScalePivot(space = 'world')
    loc = pm.spaceLocator( n = loc_name )
    loc.setScalePivot( child_pivot )
    loc.setRotatePivot( child_pivot )

    if parent:
        loc.setParent( parent, a=True ) 
    
    transform.setParent( loc, r=True )
    
# Name Offset_GRP
def add_loc_suffix( name, *args ):
    suffixes = ['_GEO', '_FOL', '_IOM', '_INF', '_GRP', '_REF', '_BSP', '_BLD', '_CRV', '_JNT', '_LOC']
    loc_suffix = '_LOC'
    name_changed = False
    for suffix in suffixes:
        if suffix in name:
            name = name.replace( suffix, loc_suffix )
            name_changed = True
    if not name_changed:
        name += loc_suffix
    return name