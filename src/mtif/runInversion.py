
import subprocess
import sys
import os

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#
# Revisar herramientas necesarias en el sistema
#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
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



