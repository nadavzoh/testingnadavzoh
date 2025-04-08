import os
import sys
############################ IGNORE WARNINGS ############################
os.environ['XDG_RUNTIME_DIR'] = os.path.join("/tmp", f"runtime-{os.environ['USER']}")
os.environ['QT_XCB_NO_XI2'] = "1"
os.environ['QT_XCB_NO_XRANDR'] = "1"
os.environ['QT_XCB_GL_INTEGRATION'] = "none"
############## IGNORE WARNINGS ##############

############################ MANDATORY ENVIRONMENT VARIABLES ############################
# WARD
if 'WORK_AREA_ROOT_DIR' not in os.environ:
    print("WORK_AREA_ROOT_DIR not set, Lotus will now exit.")
    sys.exit(1)
os.environ['LOTUS_ROOT_DIR'] = os.environ['WORK_AREA_ROOT_DIR']
# maybe do it with Lotem root dir.
############################ MANDATORY ENVIRONMENT VARIABLES ############################

############################ MANDATORY COMMANDLINE ARGUMENT ############################
# FUB NAME
if '-fub' not in sys.argv and '--fub' not in sys.argv:
    print(sys.argv)
    print("FUB name not provided, Lotus will now exit.")
    sys.exit(1)
os.environ['LOTUS_FUB'] = sys.argv[sys.argv.index('-fub') + 1]
############################ MANDATORY COMMANDLINE ARGUMENT ############################

############################ OPTIONAL ENVIRONMENT VARIABLES ############################
# In case user provides a .sp file - don't search for it in the directory
if '-spice' in sys.argv or '--spice' in sys.argv:
    os.environ['LOTUS_SPICE_FILE'] = sys.argv[sys.argv.index('-spice') + 1]

# In case user provides a .af.dcfg file - don't search for it in the directory
if '-af' in sys.argv or '--af' in sys.argv:
    os.environ['LOTUS_AF_DCFG_FILE'] = sys.argv[sys.argv.index('-af') + 1]

# In case user provides a .mutex.dcfg file - don't search for it in the directory
if '-mutex' in sys.argv or '--mutex' in sys.argv:
    os.environ['LOTUS_MUTEX_DCFG_FILE'] = sys.argv[sys.argv.index('-mutex') + 1]
############################ OPTIONAL ENVIRONMENT VARIABLES ############################

 