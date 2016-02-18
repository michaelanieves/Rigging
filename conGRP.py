import pymel.core as pm

'''
Usage:
   add_con_grps()
'''   

# create Offset Group for selected objects    
def add_con_grps(*args):
    sel = pm.ls(sl=True)
    for obj in sel:
        con_grp( obj )
        pm.select(clear= True)
        pm.select(sel, add= True) 

# Create con Group and parent to selected object if childern exist parent to con grp
def con_grp( transform, *args ):
    children = transform.listRelatives( type='transform') 
    grp_name = add_conGrp_suffix(transform.name())
    parent_pivot = transform.getScalePivot(space = 'world')
    grp = pm.group( n = grp_name, em=True )
    grp.translate.set( parent_pivot )
    grp.setParent( transform, a=True )
    
    for child in children:
        child.setParent( grp, a=True )
    
# Name Offset_GRP
def add_conGrp_suffix( name, *args ):
    suffixes = ['_GEO', '_FOL', '_IOM', '_INF', '_GRP', '_REF', '_BSP', '_BLD', '_CRV', '_JNT', '_LOC']
    grp_suffix = 'Con_GRP'
    name_changed = False
    for suffix in suffixes:
        if suffix in name:
            name = name.replace( suffix, grp_suffix )
            name_changed = True
    if not name_changed:
        name += grp_suffix
    return name