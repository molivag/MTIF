# MTIF — Magnetotelluric Inversion Framework

🧭 **MTIF** is a command-line driven framework designed to streamline the workflow
of **3-D magnetotelluric inversion using FEMTIC** and related preprocessing and postprocessing tools.

The framework focuses on **automation and reproducibility of CLI-based scientific workflows**, integrating mesh
preparation, inversion execution, cluster interaction, and postprocessing into a single command-line interface.

MTIF does **not replace FEMTIC**. Instead, it provides a structured environment around it to manage the complete inversion workflow.

---

# Philosophy

MTIF follows a **CLI-first design philosophy**.

Many geophysical modeling tools — such as **FEMTIC, TetGen, MPI tools, and HPC schedulers** — are inherently command-line oriented. 
MTIF embraces this approach and builds a structured framework around it.

Key principles:

- CLI-based workflow  
- Minimal GUI dependency  
- Reproducible project structure  
- Automation of repetitive tasks  
- Integration with HPC clusters  
- Lightweight Python implementation  

The goal is to make complex MT inversion workflows **faster, more organized, and reproducible**.

---

# Core Capabilities

MTIF provides tools to manage the full FEMTIC workflow.

# Project management

Create a standardized project structure for MT inversion studies.

```
mtif create <project_name>
```

This generates a ready-to-use directory layout for preprocessing, computing, and postprocessing.

---

## Dependency installation

Automatic download and compilation of required third-party tools:

- FEMTIC
- makeTetraMesh
- TetGen2Femtic
- makeMtr
- mergeResultOfFEMTIC
- TetGen
- MeshTran

```
mtif install
```

---

## Mesh generation

Run the preprocessing pipeline to generate FEM meshes.

```bash
mtif mesh
```

Includes optional geometry checks:

```bash
mtif mesh --check
```

---

## Inversion execution

Run FEMTIC inversions locally or through cluster workflows.

```bash
mtif run
```

---

## Cluster integration

Upload computation inputs to a remote cluster:

```bash
mtif upload
```

Download inversion results:

```bash
mtif download <job_id> <job_id> <job_id>
```

Features include:

- SSH multiplexing
- rsync transfer
- automatic job folder resolution

---

## Postprocessing

Process FEMTIC inversion outputs and generate plots.

```bash
mtif post job_305
```

Supports:

- impedance and resistivity-phase modes
- site range selection
- iteration control
- flexible plotting axes

---

# Mesh Generation Pipeline — MeshTran

MTIF integrates **MeshTran-FEMTIC**, a Fortran-based preprocessing and meshing pipeline
designed to prepare geometries and generate finite-element meshes compatible with FEMTIC.

MeshTran acts as a wrapper around the **makeTetraMesh preprocessing workflow** and automates the preparation of input data required for TetGen and FEMTIC.

The pipeline handles:

- DEM and bathymetry preprocessing
- Coastline and analysis domain generation (in progress)
- Coordinate transformations
- FEMTIC input file generation
- Execution of the makeTetraMesh pipeline

The resulting mesh is then used directly by FEMTIC for forward modelling and inversion.

---

# MeshTran Workflow

The preprocessing pipeline performs the following steps:

```
1. Read EDI files → extract site coordinates (lat/lon/elevation)

2. Convert geographic coordinates
   lat/lon → UTM coordinates

3. Convert units
   meters → kilometers

4. Compute mesh reference center

5. Transform coordinates to mesh system
   siteXmesh = siteXkm − x0
   siteYmesh = siteYkm − y0

6. Define analysis domain
   (domain extents and padding)

7. Validate geometry
   DEM coverage vs analysis domain

8. Generate FEMTIC input files
   ├─ topography.dat
   ├─ bathymetry.dat
   ├─ coastline.dat
   ├─ observing_site.dat
   └─ analysis_domain.dat
```

These files are then used by **makeTetraMesh** to generate the tetrahedral mesh.

---

# Automated makeTetraMesh Execution

MeshTran orchestrates the standard **makeTetraMesh workflow (steps 1–4)** and integrates it with the FEMTIC preprocessing pipeline.

This includes:

- Surface triangulation
- Mesh refinement around MT sites
- Region tagging
- TetGen execution
- Mesh validation utilities

The final output is a FEMTIC-compatible mesh stored in the `computing/` directory.

---

# Workflow Architecture

```
MTIF (Python CLI framework)
        │
        │ orchestrates workflow
        ▼
MeshTran (Fortran preprocessing pipeline)
        │
        │ generates FEM mesh
        ▼
FEMTIC
        │
        │ inversion
        ▼
Postprocessing tools
```

---

# Project Structure

Each MTIF project follows a consistent layout:

```
project_name/

├── preprocessing/
│
├── computing/
│
├── postprocessing/
│
├── patches/
│
└── mtif.toml
```

This separation allows clean management of:

- mesh generation
- inversion execution
- result analysis

---

# Configuration

MTIF uses a **TOML configuration file**:

```
mtif.toml
```

This file defines:

- cluster settings
- mesh parameters
- preprocessing configuration
- postprocessing defaults

Example sections:

```toml
[cluster]
host = "cluster.host"
user = "username"

[mesh]
default_mesh = "native"

[post]
post_path = "postprocessing"
```

---

# Installation (Development Mode)

Clone the repository:

```bash
git clone <repository>
cd mtif-framework
```

Install in editable mode:

```bash
pip install -e .
```

This allows modifications to the framework while keeping the `mtif` command available system-wide.

---

# Command Overview

```
mtif create <project_name>
mtif install
mtif mesh
mtif run
mtif upload
mtif download <jobs>
mtif post <job>
```

For detailed help:

```bash
mtif --help
mtif <command> --help
```

---

# Current Status

MTIF is under active development.

Recent milestones include:

- Migration from monolithic scripts to modular architecture
- Integration of CLI entrypoints
- SSH multiplexed cluster transfers
- rsync-based job management
- Integration of Python tools into the framework

---

# Author

Marco A. Oliva Gutiérrez  
Geomodels Research Institute  
University of Barcelona

---

# Acknowledgements

MTIF builds upon the work of **Yoshiya Usui** author of the FEMTIC.

---

# Contributing and Feedback

Contributions, suggestions, and bug reports are welcome.

If you encounter an issue, have ideas for improvements, or would like to
collaborate on the project, please open an Issue or submit a Pull Request.

Feedback from the magnetotelluric and geophysical modeling community is
especially appreciated.

