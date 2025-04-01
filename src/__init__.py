import os
import sys
# ignore warnings
os.environ['XDG_RUNTIME_DIR'] = os.path.join("/tmp", f"runtime-{os.environ['USER']}")
os.environ['QT_XCB_NO_XI2'] = "1"
os.environ['QT_XCB_NO_XRANDR'] = "1"
os.environ['QT_XCB_GL_INTEGRATION'] = "none"

if 'WORK_AREA_ROOT_DIR' not in os.environ:
    os.environ['WORK_AREA_ROOT_DIR'] = os.path.join(os.getcwd(), "lotus_work_area") ##????
else:
    os.environ['LOTUS_ROOT_DIR'] = os.path.join(os.environ['WORK_AREA_ROOT_DIR'], "Lotus")

# FUB NAME
if '-fub' or '--fub' in sys.argv:
    os.environ['FUB_NAME'] = sys.argv[sys.argv.index('-fub') + 1]

