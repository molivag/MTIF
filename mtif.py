#!/usr/bin/env python3

import subprocess
import argparse
import shutil
import sys
import os

MAKETETRAMESH_URL = "https://github.com/yoshiya-usui/makeTetraMesh.git"
TETGEN2FEMTIC_URL = "https://github.com/yoshiya-usui/TetGen2Femtic.git"
MAKEMTR_URL_URL = "https://github.com/yoshiya-usui/makeMtr.git"
MERGERESULT_URL = "https://github.com/yoshiya-usui/mergeResultOfFEMTIC.git"
FEMTIC_URL = "https://github.com/yoshiya-usui/femtic.git"
TETGEN_URL = "https://github.com/TetGen/TetGen.git"


def read_config(config_file="mtif.conf"):
    config = {}
    if not os.path.exists(config_file):
        print(f"ERROR: {config_file} not found.")
        sys.exit(1)

    with open(config_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    return config


def run_mesh(args):
    target_path = os.path.join("..", "postprocessing", "buildMesh", "reindexing_tetgen.py")
    if not os.path.exists(target_path):
        print(f"ERROR: reindexing_tetgen.py not found at {target_path}")
        sys.exit(1)

    if not os.path.exists("set_meshtran.io"):
        print("ERROR: set_meshtran.io not found.")
        sys.exit(1)

    print("== Running MeshTran ==")
    subprocess.run(["./meshTranPreprocess"], check=True)

    config = read_config()

    mesh = args.mesh if args.mesh else config["default_mesh"]

    subprocess.run(
        [
            # mtif post job_284 --axis freq --sites 1-10 --mode impz --iter 8 --proc 2
            "./bin/meshTranPreprocess", mesh
        ],
        check=True
    )

    if os.path.exists("plot_inputs.py"):
        print("== Plotting input geometry ==")
        subprocess.run(["python3", "plot_inputs.py"], check=True)



def run_inversion(config):
    inversion_dir = config.get("inversion_dir", "computing")
    cluster_mode = config.get("cluster_mode", "false").lower() == "true"
    slurm_script = config.get("slurm_script", "run.slurm")

    if not os.path.exists(inversion_dir):
        print(f"ERROR: inversion directory '{inversion_dir}' not found.")
        sys.exit(1)

    if cluster_mode:
        slurm_path = os.path.join(inversion_dir, slurm_script)
        if not os.path.exists(slurm_path):
            print(f"ERROR: SLURM script '{slurm_path}' not found.")
            sys.exit(1)

        print("== Submitting job to SLURM ==")
        subprocess.run(["sbatch", slurm_path], check=True)
    else:
        print("== Running FEMTIC locally ==")
        subprocess.run(["femtic"], cwd=inversion_dir, check=True)


def run_post(args):
    print("== Running Postprocessing ==")
    config = read_config()

    job = args.job if args.job else config["last_job"]
    sites = args.sites if args.sites else config["default_sites"]
    iters = args.iter if args.iter else config["default_iter"]
    procs = args.proc if args.proc else config["default_proc"]
    xaxis = args.axis if args.axis else config["default_axis"]

    if args.mode is not None:
        mode = args.mode                        #Si usuario pasa --mode impz → usa impz
    elif config.get("default_mode") in ["impz", "rhoph"]:
        mode = config.get("default_mode")       #Si no pasa nada y el config tiene impz o rhoph → usa eso
    else:
        mode = "none"                           #Si no hay nada válido → usa "none"

    results_path = f"postprocessing/{job}"
    st_arg = f"st{sites}"
    ip_arg = f"ip{iters}-{procs}"

    print("Job:", job)
    print("Sites:", sites)
    print("Mode:", mode)

    mode = str(mode)
    subprocess.run(
        [
            # mtif post job_284 --axis freq --sites 1-10 --mode impz --iter 8 --proc 2
            "./bin/MTpostprocess.py", results_path,
            st_arg,
            mode,
            ip_arg,
            xaxis
        ],
        check=True
    )
    


def check_tool(tool_name):
    if shutil.which(tool_name) is None:
        print(f"ERROR: Required tool '{tool_name}' not found in PATH.")
        sys.exit(1)


def check_environment():
    print("== Checking required tools ==")

    required_tools = ["git", "make"]

    for tool in required_tools:
        check_tool(tool)

    # compilador
    if shutil.which("gfortran") is None and shutil.which("ifort") is None:
        print("ERROR: No Fortran compiler found (gfortran or ifort).")
        sys.exit(1)

    print("Environment OK.\n")

def clone_repo(url, path):
    if not os.path.exists(path):
        print(f"Cloning {url} into {path}")
        subprocess.run(["git", "clone", url, path], check=True)
    else:
        print(f"{path} already exists. Skipping clone.")

    # shutil.copy(f"{path}dependencies/femtic/femtic", "bin/")


def run_install():
    check_environment()
    os.makedirs("dependencies",exist_ok=True)
    os.makedirs("bin", exist_ok=True)
    if not os.path.exists("dependencies/femtic"):
        subprocess.run(["git", "clone", FEMTIC_URL, "dependencies/femtic"], check=True)
    # subprocess.run(["patch", "Makefile", "../../patches/femtic.patch"],
    #                cwd="dependencies/femtic",
    #                check=True)

        # Sustituir Makefile original por el tuyo
    if os.path.exists("patches/Makefile_IntelMPI"):
        print("Replacing FEMTIC Makefile with Makefile_IntelMPI")
        shutil.copy(
            "patches/Makefile_IntelMPI",
            "dependencies/femtic/src/Makefile"
        )
    else:
        print("Makefile_IntelMPI not found in patches/")
        sys.exit(1)
    subprocess.run(["make"], cwd="dependencies/femtic/src", check=True)
    shutil.copy("dependencies/femtic/src/femtic", "bin/")
    print("FEMTIC installed correctly.")


def run_new(project_name):
    if os.path.exists(project_name):
        print(f"Error: Folder '{project_name}' already exists.")
        sys.exit(1)
    print(" ")
    print(f" Creating new MTIF project: {project_name}")
   
    os.makedirs(os.path.join(project_name, "preprocessing"))
    os.makedirs(os.path.join(project_name, "preprocessing/PlotWithPython"))
    os.makedirs(os.path.join(project_name, "preprocessing/geometry"))
    os.makedirs(os.path.join(project_name, "preprocessing/inv"))
    os.makedirs(os.path.join(project_name, "preprocessing/DEM"))
    os.makedirs(os.path.join(project_name, "preprocessing/edi_files"))
    os.makedirs(os.path.join(project_name, "preprocessing/buildMesh"))
    os.makedirs(os.path.join(project_name, "computing"))
    os.makedirs(os.path.join(project_name, "postprocessing"))
    
    # Crear mtif.conf básico
    with open(os.path.join(project_name, "mtif.conf"), "w") as f:
        f.write(
        """
        # ---- Execution Mode ----
        cluster_mode = true
        
        # ---- Directories ----
        inversion_dir = computing
        
        # ---- SLURM ----
        slurm_script = run.slurm
        
        # ---- Automation ----
        post_path = postprocessing
        default_sites = 1-10
        default_mode = none
        default_iter = 5
        default_proc = 2
        last_job = job_001
        """
        )
    
    print("     Project created successfully.")
    print(f" now run:")
    print(f" cd {project_name}")
    print(" mtif install")






def main():
    parser = argparse.ArgumentParser(
        prog="mtif",
        description="""
    MTIF - Magnetotelluric Inversion Framework © 2026
    
 An Integrated framework for preprocessing, inversion and postprocessing of
    3D magnetotelluric data using FEMTIC as inversion engine.

    Author: Marco A Oliva Gutierrez
            University of Barcelona - Geomodels Research Institute
    """,
        epilog="""
    Examples:
      mtif create
      mtif install
      mtif mesh
      mtif run
      mtif post job_284 --sites 1-10 --mode impz --iter 8 --proc 2 --axis freq
    
    For detailed help on a command:
      mtif <command> --help
    """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--version",
        action="version",
        version="MTIF v0.1.0"
    )



    subparsers = parser.add_subparsers(
    dest="command",
    required=True
    )
    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    create_parser = subparsers.add_parser(
        "create",
        help="  Create a new MTIF project",
        description="Create a new MTIF project directory with predefined structure."
    )
    create_parser.add_argument(
        "project_name",
        help="Name of the new project directory"
    )
    
    # --------------------------------------------------
    # INSTALL
    # --------------------------------------------------
    install_parser = subparsers.add_parser(
        "install",
        help="Install required third-party dependencies",
        description="Clone and compile required tools such as FEMTIC and TetGen."
    )
    
    # --------------------------------------------------
    # MESH
    # --------------------------------------------------
    mesh_parser = subparsers.add_parser(
        "mesh",
        help="Run mesh preprocessing",
        description="Execute MeshTran preprocessing pipeline."
    )
    
    mesh_parser.add_argument(
        "--mesh",
        choices=["native", "external"],
        help="Site range (native (default)  or external)"
    )

    
    # --------------------------------------------------
    # RUN
    # --------------------------------------------------
    run_parser = subparsers.add_parser(
        "run",
        help="Run inversion",
        description="Launch FEMTIC inversion locally or in cluster mode."
    )
    
    # --------------------------------------------------
    # POST
    # --------------------------------------------------
    post_parser = subparsers.add_parser(
        "post",
        help="Run postprocessing",
        description="Merged results and generate plots from inversion outputs."
    )
    
    post_parser.add_argument(
        "job",
        nargs="?",
        help="Job name (folder inside postprocessing)"
    )
    
    post_parser.add_argument(
        "--sites",
        help="Site range (e.g., 1-10)"
    )
    
    post_parser.add_argument(
        "--mode",
        choices=["impz", "rhoph"],
        help="Postprocessing mode"
    )
    
    post_parser.add_argument(
        "--iter",
        type=int,
        help="Number of iterations"
    )
    
    post_parser.add_argument(
        "--proc",
        type=int,
        help="Number of processes"
    )

    post_parser.add_argument(
        "--axis",
        help="Set x axis (e.g., freq or period)"
    )


    args = parser.parse_args()

    if args.command == "create":
        run_new(args.project_name)

    elif args.command == "install":
        run_install()

    elif args.command == "mesh":
        run_mesh(args)

    elif args.command == "run":
        config = read_config()
        run_inversion(config)

    elif args.command == "post":
        run_post(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
