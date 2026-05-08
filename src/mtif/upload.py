from pathlib import Path
from halo import Halo
import subprocess
import time
import sys
import os

from mtif.config import read_config

def run_upload():
    config = read_config()

    # --- Lee config ---
    if "cluster" not in config:
        print("ERROR: Missing [cluster] section in mtif.toml")
        sys.exit(1)

    if "post" not in config or "post_path" not in config["post"]:
        print("ERROR: Missing [post].post_path in mtif.toml")
        sys.exit(1)

    cluster = config["cluster"]
    host = cluster.get("host")
    user = cluster.get("user")

    control_path = f"/tmp/mtif_mux_{os.getpid()}"
    ssh_opts = [
        "-o", "ControlMaster=auto",
        "-o", f"ControlPath={control_path}",
        "-o", "ControlPersist=600"
    ]

    project_name = Path.cwd().name
    print("   Opening SSH master connection...")

    subprocess.run(
        [
            "ssh",
            "-MNf",
            "-o", "ControlMaster=yes",
            "-o", f"ControlPath={control_path}",
            "-o", "ControlPersist=600",
            f"{user}@{host}"
        ],
        check=True
    )

    print("   SSH master connection established.")

    subprocess.run(
        ["ssh", *ssh_opts, f"{user}@{host}",
         f"mkdir -p ~/{project_name}"],
        check=True
    )
    print()  # pequeño espacio visual

    spinner = Halo(
        text=f"   Uploading computing/ to {host}...",
        spinner="shark",
        placement="right",
        color="green"
    )
    spinner.start()
    
    result = subprocess.run(
        [
            "rsync",
            "-az",
            "-e", f"ssh {' '.join(ssh_opts)}",
            "--exclude", "*.log",
            "./computing/",
            f"{user}@{host}:~/{project_name}"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    
    if result.returncode == 0:
        spinner.succeed(f"   Upload computing/ to {project_name} in {host} completed.")
    else:
        spinner.fail(f"   Upload to {host} failed.")
        print("   Closing SSH master connection...")
    
