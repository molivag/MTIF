from tqdm import tqdm
from mtif.config import read_config
import subprocess
import shutil
import sys
import os


def get_remote_size(user, host, remote_path, ssh_opts):
    cmd = [
        "ssh",
        *ssh_opts,
        f"{user}@{host}",
        f"du -sb {remote_path} | cut -f1"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except:
        return None

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#
# Comando para lanzar el postprocesado
#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def rsync_with_progress(user, host, remote_path, local_path, ssh_opts, job_name):
    total_size = get_remote_size(user, host, remote_path, ssh_opts)
    if total_size is None:
        print("  WARNING: Could not determine remote size.")
        return False

    pbar = tqdm(total=total_size, unit="B", unit_scale=True, desc=f"  {job_name}", ncols=100)

    rsync_cmd = [
        "rsync",
        "-az",
        "--info=progress2",
        "--no-human-readable",
        # "--no-inc-recursive",   # fuerza escaneo completo antes de transferir
        "-e",
        f"ssh {' '.join(ssh_opts)}",
        f"{user}@{host}:{remote_path}/",
        local_path
    ]

    process = subprocess.Popen(
        rsync_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    last_bytes = 0

    while True:
        line = process.stdout.readline()
        if not line:
            break

        # rsync --progress imprime líneas tipo:
        # 123456789  12%
        if "%" in line:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1].endswith("%"):
                try:
                    current_bytes = int(parts[0])
                    delta = current_bytes - last_bytes
                    if delta > 0:
                        pbar.update(delta)
                        last_bytes = current_bytes
                except:
                    pass

    process.wait()
    pbar.close()

    return process.returncode == 0

#-------------------------------------------------------------------------
def run_download(args):
    """
    mtif download job_284 job_293 ...
    1) Valida remoto (resuelve folder real con job_284*)
    2) Descarga contenido a postprocessing/job_284/
    """
    config = read_config()

    # --- Lee config ---
    if "cluster" not in config:
        print("ERROR: Missing [cluster] section in mtif.toml")
        sys.exit(1)

    if "post" not in config or "post_path" not in config["post"]:
        print("ERROR: Missing [post].post_path in mtif.toml")
        sys.exit(1)

    cluster = config["cluster"]
    post_cfg = config["post"]

    host = cluster.get("host")
    user = cluster.get("user")
    remote_base = cluster.get("remote_results_base")
    post_path = post_cfg.get("post_path", "postprocessing")

    if not host or not user or not remote_base:
        print("ERROR: cluster.host, cluster.user, cluster.remote_results_base are required in mtif.toml")
        sys.exit(1)

    # --- Herramientas necesarias ---
    if shutil.which("ssh") is None:
        print("ERROR: ssh not found in PATH")
        sys.exit(1)
    if shutil.which("scp") is None:
        print("ERROR: scp not found in PATH")
        sys.exit(1)

    os.makedirs(post_path, exist_ok=True)

    control_path = f"/tmp/mtif_mux_{os.getpid()}"

    print("   == MTIF DOWNLOAD ==")
    print(f"   Remote: {user}@{host}:{remote_base}")
    print(f"   Local:  {post_path}/")

    print("   Opening SSH master connection...")
    print("   Step 1) Validating remote folders...")




    # control_path = "/tmp/mtif_mux_%r@%h:%p"

    master_cmd = [
        "ssh",
        "-MNf",
        "-o", "ControlMaster=yes",
        "-o", f"ControlPath={control_path}",
        "-o", "ControlPersist=600",
        f"{user}@{host}"
    ]

    subprocess.run(master_cmd, check=True)
    
    ssh_opts = [
        "-o", "ControlMaster=auto",
        "-o", f"ControlPath={control_path}",
        "-o", "ControlPersist=600"
    ]
    # ------------------------------------------------------------
    # 1) VALIDACIÓN: resolver nombre real remoto para cada prefijo
    # ------------------------------------------------------------
    resolved = {}     # prefix -> remote_folder_name
    missing = []      # prefixes sin match
    ambiguous = []    # prefixes con >1 match (no esperado)
    for prefix in args.jobs:
        # Pedimos que el remote haga la expansión del wildcard
        # y liste directorios que matcheen job_XXX*
        # Nota: redirigimos stderr para no ensuciar salida si no hay match
        remote_cmd = f"cd {remote_base} && ls -d {prefix}* 2>/dev/null"
        proc = subprocess.run(["ssh", *ssh_opts, f"{user}@{host}", remote_cmd],
            capture_output=True,
            text=True
        )

        # Si ssh falla (host down, auth, etc.)
        if proc.returncode != 0 and proc.stdout.strip() == "":
            # si hay stderr, lo mostramos como warning y seguimos
            err = proc.stderr.strip()
            print(f"WARNING: ssh/ls failed for prefix '{prefix}'. {err if err else ''}".strip())
            missing.append(prefix)
            continue

        matches = [line.strip() for line in proc.stdout.splitlines() if line.strip()]

        if len(matches) == 0:
            print(f"WARNING: Remote job not found: {prefix} (no match for {prefix}*)")
            missing.append(prefix)
            continue

        if len(matches) > 1:
            # Tú dices que nunca pasará, pero lo manejamos para que no rompa
            print(f"WARNING: Ambiguous remote matches for {prefix}: {matches}. Skipping.")
            ambiguous.append(prefix)
            continue

        # matches[0] trae el nombre real remoto (ej: job_284_femtic_alpha5_...)
        resolved[prefix] = matches[0]

    # ------------------------------------------------------------
    # 2) DESCARGA: copiar contenido remoto a postprocessing/job_XXX/
    # ------------------------------------------------------------
    if len(resolved) == 0:
        print("Nothing to download. (All jobs missing or ambiguous)")
        print(f"Missing: {missing}")
        print(f"Ambiguous: {ambiguous}")
        return

    print("   \nStep 2) Downloading...")
    downloaded = []
    skipped_exists = []
    failed = []

    # 2️⃣ Loop de descargas
    # tqdm por job
    # for prefix in tqdm(list(resolved.keys()), desc="Downloading jobs", unit="job"):
    started_download = False
    for prefix in resolved.keys():
        remote_folder = resolved[prefix]
        local_dest = os.path.join(post_path, prefix)

        if os.path.exists(local_dest):
            print(f"\nWARNING: Local folder exists, skipping: {local_dest}")
            skipped_exists.append(prefix)
            continue

        os.makedirs(local_dest, exist_ok=True)

        # Si llega aquí, va a descargar algo real
        if not started_download:
            print()   # ← solo una vez
            started_download = True

        success = rsync_with_progress(
            user,
            host,
            f"{remote_base}/{remote_folder}",
            local_dest,
            ssh_opts,
            prefix
        )

        if success:
            downloaded.append(prefix)
        else:
            print(f"\nWARNING: Download failed for {prefix} ({remote_folder})")
            failed.append(prefix)



    # 3️⃣ Cerrar master UNA vez
    print("Closing SSH master connection...")

    close_cmd = [
        "ssh",
        "-O", "exit",
        "-o", f"ControlPath={control_path}",
        f"{user}@{host}"
    ]

    subprocess.run(close_cmd)




    print("\n== Download summary ==")
    print(f"Downloaded:      {downloaded}")
    print(f"Skipped (exist): {skipped_exists}")
    print(f"Missing:         {missing}")
    print(f"Ambiguous:       {ambiguous}")
    print(f"Failed:          {failed}")

