#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os


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
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
