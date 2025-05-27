#!/bin/bash

# Determine the location of this script and set up paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOTUS_ROOT_DIR="$(dirname "${SCRIPT_DIR}")"
LOTEM_ROOT_DIR="$(dirname "${LOTUS_ROOT_DIR}")"
LOTUS_SRC_DIR="${LOTUS_ROOT_DIR}/src"
FLY_ROOT_DIR="${LOTEM_ROOT_DIR}/fly"

# Set environment variables
export LOTUS_ROOT_DIR

# Set up Python path
if [ -n "$PYTHONPATH" ]; then
    export PYTHONPATH="${LOTUS_ROOT_DIR}:${LOTUS_SRC_DIR}:${FLY_ROOT_DIR}:${LOTEM_ROOT_DIR}/src/external_modules:${PYTHONPATH}"
else
    export PYTHONPATH="${LOTUS_ROOT_DIR}:${LOTUS_SRC_DIR}:${FLY_ROOT_DIR}:${LOTEM_ROOT_DIR}/src/external_modules"
fi

# Set up library path for PyQt5
if [ -n "$LD_LIBRARY_PATH" ]; then
    export LD_LIBRARY_PATH="/usr/intel/pkgs/gcc/14.2.0/lib/:${LD_LIBRARY_PATH}"
else
    export LD_LIBRARY_PATH="/usr/intel/pkgs/gcc/14.2.0/lib/"
fi

# Set up QT environment variables to avoid warnings
export XDG_RUNTIME_DIR="/tmp/runtime-${USER}"
export QT_XCB_NO_XI2="1"
export QT_XCB_NO_XRANDR="1"
export QT_XCB_GL_INTEGRATION="none"
export QT_QPA_PLATFORM="xcb"

# Python interpreter
PYTHON="/usr/intel/pkgs/python3/3.11.1/bin/python3"

# Run the application with all arguments passed to this script
exec "${PYTHON}" -m src.ui.app "$@"
