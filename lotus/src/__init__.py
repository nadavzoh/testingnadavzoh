import os
import sys
from argparse import ArgumentParser


# Get lotus root directory for internal use
lotus_src_dir = os.path.abspath(os.path.dirname(__file__))
lotus_root_dir = os.path.abspath(os.path.join(lotus_src_dir, ".."))

# Set LOTUS_ROOT_DIR if not already set by the wrapper script
if 'LOTUS_ROOT_DIR' not in os.environ:
    os.environ['LOTUS_ROOT_DIR'] = lotus_root_dir

# Mandatory environment check - this is still needed
if 'WORK_AREA_ROOT_DIR' not in os.environ:
    print("WORK_AREA_ROOT_DIR not set, Lotus will now exit.")
    sys.exit(1)

os.environ['LOTUS_USER_WARD'] = os.path.abspath(os.environ['WORK_AREA_ROOT_DIR'])

# FUB related argument parsing - needed regardless of how the module is started
parser = ArgumentParser(description="Lotus GUI")
parser.add_argument("-fub", "--fub", help="FUB name", required=True, type=str)
parser.add_argument("-spice", "--spice", help="Path to <FUB>.sp file", required=False, type=str)
parser.add_argument("-af", "--af", help="Path to <FUB>.af.dcfg file", required=False, type=str)
parser.add_argument("-mutex", "--mutex", help="Path to <FUB>.mutex.dcfg file", required=False, type=str)
args = parser.parse_args()

os.environ['LOTUS_FUB'] = args.fub

if args.spice:
    os.environ['LOTUS_SPICE_FILE'] = args.spice
if args.af:
    os.environ['LOTUS_AF_DCFG_FILE'] = args.af
if args.mutex:
    os.environ['LOTUS_MUTEX_DCFG_FILE'] = args.mutex
