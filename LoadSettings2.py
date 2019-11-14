############################################################################
################    CONFIGURATION PART (CUSTOMIZE THIS)   ##################
############################################################################

# The following variable contains the list of PVs which should
# be saved
# each entry constitutes a list of 3 parameters:
#  (1) identifier string used in the settings file
#  (2) PV name as referenced within CSS
#  (3) default restore behaviour (True=do restore, False=don't restore, can be overridden by user)
s = \
[
    ['Sample', 'tango://set/sample/voltage/voltage_w', True],
    ['Extr', 'tango://ktof/logic/lens1/Ext_VUSet', True],
    ['Foc', 'tango://ktof/logic/lens1/Foc_VUSet', True],
    ['Z1', 'tango://ktof/logic/lens1/Z1_VUSet', True],
    ['Z2', 'tango://ktof/logic/lens1/Z2_VUSet', True],
    ['A', 'tango://ktof/logic/lens1/A_VUSet', True],
    ['B', 'tango://ktof/logic/lens1/B_VUSet', True],
    ['C', 'tango://ktof/logic/lens1/C_VUSet', True],
    ['D', 'tango://ktof/logic/lens1/D_VUSet', True],
    ['E', 'tango://ktof/logic/lens1/E_VUSet', True],
    ['F', 'tango://ktof/logic/lens1/F_VUSet', True],

    #stg1
    ['DeflY', 'tango://ktof/stg1/col1/DeflY', True],
    ['DeflX', 'tango://ktof/stg1/col1/DeflX', True],    
    ['Stig2a', 'tango://ktof/stg1/col1/Stig2a', True],    
    ['Stig2b', 'tango://ktof/stg1/col1/Stig2b', True],    
    ['Stig4', 'tango://ktof/stg1/col1/Stig4', True],    
    ['Offset', 'tango://ktof/stg1/col1/Offset', True],    
    ['Angle', 'tango://ktof/stg1/col1/Angle', True],    
    #stg2
    ['DeflY', 'tango://ktof/stg2/col2/DeflY', True],
    ['DeflX', 'tango://ktof/stg2/col2/DeflX', True],    
    ['Stig2a', 'tango://ktof/stg2/col2/Stig2a', True],    
    ['Stig2b', 'tango://ktof/stg2/col2/Stig2b', True],    
    ['Stig4', 'tango://ktof/stg2/col2/Stig4', True],    
    ['Offset', 'tango://ktof/stg2/col2/Offset', True],    
    ['Angle', 'tango://ktof/stg2/col2/Angle', True],
    #hemisphere
    ['G', 'tango://ktof/hemisphere/lens/G', True],   
    ['IS_factor', 'tango://ktof/hemisphere/lens/IS_factor', True],   
    ['OS_factor', 'tango://ktof/hemisphere/lens/OS_factor', True],   
    ['IS_offset', 'tango://ktof/hemisphere/lens/IS_offset', True],   
    ['OS_offset', 'tango://ktof/hemisphere/lens/OS_offset', True],   

    ['X1_factor', 'tango://ktof/hemisphere/lens/X1_factor', True],   
    ['X1_offset', 'tango://ktof/hemisphere/lens/X1_offset', True],   

    ['X2_factor', 'tango://ktof/hemisphere/lens/X2_factor', True],   
    ['X2_offset', 'tango://ktof/hemisphere/lens/X2_offset', True],   

    ['X3_factor', 'tango://ktof/hemisphere/lens/X3_factor', True],   
    ['X3_offset', 'tango://ktof/hemisphere/lens/X3_offset', True],   

    ['X4_factor', 'tango://ktof/hemisphere/lens/X4_factor', True],   
    ['X4_offset', 'tango://ktof/hemisphere/lens/X4_offset', True],

    #downstream
    ['H', 'tango://ktof/logic/lens1/H_VUSet', True],
    ['I', 'tango://ktof/logic/lens1/I_VUSet', True],
    ['J', 'tango://ktof/logic/lens1/J_VUSet', True],
    ['K', 'tango://ktof/logic/lens1/K_VUSet', True],
    ['L', 'tango://ktof/logic/lens1/L_VUSet', True],
    ['M', 'tango://ktof/logic/lens1/M_VUSet', True],
    ['N', 'tango://ktof/logic/lens1/N_VUSet', True],
    #screen    
    ['1', 'tango://ktof/logic/lens1/1_VUSet', False],
    ['Screen', 'tango://ktof/logic/lens1/Screen_VUSet', False],
    #DLD
    ['MCPb', 'tango://ktof/logic/lens1/MCPb_VUSet', False]
]

# size: the size of the window
size = (800,400)

# title: the title of the window
title = 'Load Settings'

# defaultdir: the directory that is first shown in save/open dialogs
#defaultdir = '/home/user/Settings/2017'
defaultdir = '/media/user/DATADRIVE1/Settings'
# savemode: (True/False) whether the Table should be adapted to saving (True) or opening (False) a setting
savemode = False

############################################################################
#####################    CODE PART (DON'T CHANGE)    #######################
############################################################################

from SettingsTableFrame import SettingsTableFrame

f = SettingsTableFrame(title, size=size, settings_config=s, widget=widget, savemode=savemode, defaultdir=defaultdir)
if f.OKstatus:
    f.visible = True

