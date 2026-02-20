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


def run_mesh():
    if not os.path.exists("set_meshtran.io"):
        print("ERROR: set_meshtran.io not found.")
        sys.exit(1)

    print("== Running MeshTran ==")
    subprocess.run(["./meshTranPreprocess"], check=True)

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
    subprocess.run(
        ["python3", "MTpostproess.py"] + args,
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
    subprocess.run(["patch", "Makefile", "../../patches/femtic.patch"],
                   cwd="dependencies/femtic",
                   check=True)
    subprocess.run(["make"], cwd="dependencies/femtic", check=True)
    shutil.copy("dependencies/femtic/femtic", "bin/")
    print("FEMTIC installed correctly.")






def main():
    parser = argparse.ArgumentParser(description="MTIF - Magnetotelluric Inversion Framework")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("mesh", help="Run mesh preprocessing")
    subparsers.add_parser("run", help="Run inversion")
    
    post_parser = subparsers.add_parser("post", help="Run postprocessing")
    post_parser.add_argument("args", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if args.command == "mesh":
        run_mesh()
    elif args.command == "run":
        config = read_config()
        run_inversion(config)
    elif args.command == "post":
        run_post(args.args)
    elif args.command == "install":
        run_install()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
