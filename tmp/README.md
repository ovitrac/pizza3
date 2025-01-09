## Overview

The `tmp/` folder contains the output files generated by various demonstrators and example scripts that use the **Pizza3** toolkit for LAMMPS simulations. This directory acts as a workspace for temporary data, including LAMMPS input scripts, DSCRIPT files, debugging logs, and visualization outputs.

## Contents

The `tmp/` folder typically includes the following types of files:

1. **LAMMPS Input Scripts (`*.txt`)**:
   - Generated input files for LAMMPS simulations. These scripts define regions, forcefields, group assignments, and other simulation parameters.
   - Examples:
     - `example2.txt`: A complete LAMMPS script for initializing a simulation with cylindrical regions and bead types.
     - `example2bis.txt`: An updated script introducing physics via forcefields.

2. **DSCRIPT Files (`*.d.txt`)**:
   - Modular and reusable representations of the LAMMPS scripts in the DSCRIPT format.
   - These files can be reloaded and dynamically modified for future simulations.
   - Examples:
     - `example2.d.txt`: DSCRIPT representation of `example2.txt`.
     - `example2bis.d.txt`: DSCRIPT representation of the updated script with forcefields.

3. **Debugging and Visualization Files**:
   - **HTML Reports** (`*.html`):
     - Variable reports generated during script analysis and debugging.
     - Example: `example2.d.var.html` contains detailed information about variables in `example2.d.txt`.
   - **Dump Files** (`dump.*`):
     - LAMMPS dump files capturing the initial geometry of the simulation setup.
     - Example: `dump.initial_geometry`.

4. **Forcefield Configuration Files (`*.txt`)**:
   - Serialized forcefield configurations for reuse and debugging.
   - Example: `FFbase.default.txt`: Default forcefield configuration used in `example2bis`.

## Usage

1. **Generating LAMMPS Scripts**:
   - Run example scripts to generate LAMMPS input files (`*.txt`) in this folder.
   - Examples:
     - `example2.txt` demonstrates setting up a simulation box and defining regions.
     - `example2bis.txt` integrates physics by introducing forcefields.

2. **Reusing DSCRIPT Files**:
   - DSCRIPT files (`*.d.txt`) allow for modular simulation setups.
   - Reload and modify DSCRIPT files using the `dscript` module.
   - Example:
     ```python
     from pizza.dscript import dscript
     D = dscript.load("tmp/example2.d.txt")
     ```

3. **Debugging and Analysis**:
   - Analyze variable definitions and occurrences using generated HTML reports.
   - Validate reversibility of DSCRIPT-to-LAMMPS conversions.

4. **Visualization**:
   - Use LAMMPS dump files (`dump.*`) to visualize the simulation setup.

## Examples

### Running Example 2

1. Generate `example2.txt`:
   ```bash
   python example2.py
   ```
2. Output files:
   - `tmp/example2.txt`: LAMMPS script.
   - `tmp/example2.d.txt`: DSCRIPT file.
   - `tmp/example2.d.var.html`: Variable report.

### Running Example 2bis (with Forcefields)

1. Generate `example2bis.txt`:
   ```bash
   python example2bis.py
   ```
2. Output files:
   - `tmp/example2bis.txt`: Updated LAMMPS script with forcefields.
   - `tmp/example2bis.d.txt`: DSCRIPT file.
   - `tmp/example2bis.rev.txt`: Reversed LAMMPS script for validation.

## Notes

- **File Management**: Files in this folder are temporary and can be safely deleted after use. However, saving DSCRIPT files (`*.d.txt`) is recommended for reproducibility.
- **Customization**: Modify the example scripts to adapt to specific simulation requirements.

## Contact

**Author**: INRAE\\Olivier Vitrac
**Email**: olivier.vitrac@agroparistech.fr
**Last Revision**: 2025-01-07