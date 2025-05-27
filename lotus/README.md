# Lotus GUI Application

A GUI application for managing and analyzing configuration files for circuit design.

## Overview

Lotus is a PyQt5-based application designed for managing user's
configuration files for circuit design projects.\
It provides a user-friendly interface for editing, validating, and analyzing these configuration files.

## Prerequisites

- Python 3.6 or higher
- PyQt5
- FlyNetlist library


## Running the Application

The application requires specific command-line arguments to run properly:

```bash
bin/LOTUS -fub <FUB_NAME> [-spice <SPICE_FILE>] [-af <AF_FILE>]
```

### Required Arguments / Environment Variables

- `-fub`, `--fub`: The FUB (Functional Unit Block) name for the circuit design
- `WORK_AREA_ROOT_DIR`: The root directory of the work area.\
  This is a must-have environment variable and should point to the base directory where your project files are located.
  Specifically, it should point to the directory containing the `netlists` and `drive` folders.
### Optional Arguments

- `-spice`, `--spice`: Path to the spice file (`<FUB>.sp`). If not provided, the application will look for it in the default location, i.e., `<WORK_AREA>/netlists/spice/<SPICE_FILE>.sp`.
- `-af`, `--af`: Path to the Activity Factor configuration file (`<FUB>.af.dcfg`). If not provided, the application will look for it in the default location, i.e., `<WORK_AREA>/drive/cfg/<AF_FILE>.af.dcfg`.

[//]: # (- `-mutex`, `--mutex`: Path to the Mutual Exclusivity configuration file &#40;`<FUB>.mutex.dcfg`&#41;. If not provided, the application will look for it in the default location.)

## Example Usage

```bash
bin/LOTUS -fub mydesign -spice ./path/to/mydesign.sp -af ./path/to/mydesign.af.dcfg
```

## File Format Requirements

### Spice File (`.sp`)

The spice file should contain the circuit netlist in standard SPICE format.

### Activity Factor File (`.af.dcfg`)

Each line in the AF file should follow this format:

```
{template:net} AF_VALUE [flags]
```

Where:
- `template`: (Optional) The template name, given by a raw string or by regex
- `net`: The net name, given by a raw string or by regex
- `AF_VALUE`: The activity factor value, float between [0,1]
- `flags`: (Optional) Additional flags like `template-regexp`, `template-regular`, `net-regexp`, `net-regular`, `_em`, `_sh`


Lines starting with `#` are treated as comments.

