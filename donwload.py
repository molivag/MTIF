from tqdm import tqdm
import subprocess
import shutil
import sys
import os


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

    print("== MTIF DOWNLOAD ==")
    print(f"Remote: {user}@{host}:{remote_base}")
    print(f"Local:  {post_path}/")
    print("Step 1) Validating remote folders...")

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
        proc = subprocess.run(
            ["ssh", f"{user}@{host}", remote_cmd],
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

    print("\nStep 2) Downloading...")
    downloaded = []
    skipped_exists = []
    failed = []

    # tqdm por job
    for prefix in tqdm(list(resolved.keys()), desc="Downloading jobs", unit="job"):
        remote_folder = resolved[prefix]
        local_dest = os.path.join(post_path, prefix)

        if os.path.exists(local_dest):
            print(f"\nWARNING: Local folder exists, skipping: {local_dest}")
            skipped_exists.append(prefix)
            continue

        os.makedirs(local_dest, exist_ok=True)

        # Copiar CONTENIDO del folder remoto al folder local job_XXX/
        #  - Traemos /remote_base/remote_folder/. (contenido)
        #  - Lo ponemos en local_dest/
        remote_src = f"{user}@{host}:{remote_base}/{remote_folder}/."
        try:
            subprocess.run(
                ["scp", "-r", remote_src, local_dest],
                check=True
            )
            downloaded.append(prefix)
        except subprocess.CalledProcessError as e:
            print(f"\nWARNING: Download failed for {prefix} ({remote_folder}). returncode={e.returncode}")
            failed.append(prefix)
            # dejamos la carpeta vacía si falló; si quieres, luego la borramos, pero no lo hago sin que lo pidas

    print("\n== Download summary ==")
    print(f"Downloaded:      {downloaded}")
    print(f"Skipped (exist): {skipped_exists}")
    print(f"Missing:         {missing}")
    print(f"Ambiguous:       {ambiguous}")
    print(f"Failed:          {failed}")
