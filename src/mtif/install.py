
from halo import Halo
import subprocess
import shutil
import sys
import os

from matplotlib.pyplot import pause

FEMTIC_URL          = "https://github.com/yoshiya-usui/femtic.git"
MAKETETRAMESH_URL   = "https://github.com/yoshiya-usui/makeTetraMesh.git"
MAKEMTR_URL         = "https://github.com/yoshiya-usui/makeMtr.git"
TETGEN2FEMTIC_URL   = "https://github.com/yoshiya-usui/TetGen2Femtic.git"
MESHTRAN_URL        = "https://github.com/molivag/MeshTran.git"
TETGEN_URL          = "https://github.com/TetGen/TetGen.git"
MERGERESULT_URL     = "https://github.com/yoshiya-usui/mergeResultOfFEMTIC.git"

bsname = 'Makefile'
dirdep = 'dependencies'
dirpat = 'patches'
# Mapeo: (url, destino, patch_makefile_origen, makefile_destino_relativo)
# patch_makefile_origen = None si no requiere patch
DEPENDENCIES = [
#       url,               destino,                   patches,      makefile_destino   src_subdir       binname
    # (FEMTIC_URL,        f"{dirdep}/femtic",     f"{bsname}_femtic",   "src/Makefile",     "src",     "femtic"        ),
    # (MAKETETRAMESH_URL, f"{dirdep}/dep1",       f"{bsname}_dep1",     "src/Makefile",     "src",     "makeTetraMesh" ),
    # (MAKEMTR_URL,       f"{dirdep}/dep2",       f"{bsname}_dep2",     "src/Makefile",     "src",     "makeMtr"       ),
    # (TETGEN2FEMTIC_URL, f"{dirdep}/dep3",       f"{bsname}_dep3",     "src/Makefile",     "src",     "TetGen2Femtic" ),
    (MESHTRAN_URL,      f"{dirdep}/meshtran",         None,                None  ,        "",      "meshTran"      ),
    # (TETGEN_URL,        f"{dirdep}/tetgen",           None,                None  ,        "",     "tetgen"        ), 
    # (MERGERESULT_URL,   f"{dirdep}/dep4",       f"{bsname}_dep4",     "src/Makefile",     "src",     "mergeResult"   ),
]


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#
# Revisar herramientas necesarias en el sistema
#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
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




def build_repo(repo_path, src_subdir, binary_name):
    #Crea la ruta de destino + src_dir 
    build_dir = os.path.join(repo_path, src_subdir)
    print(f"  Building {repo_path} ...")
    subprocess.run(["make"], cwd=build_dir, check=True)
    binary_src = os.path.join(build_dir, binary_name)

    if os.path.exists(binary_src):
        shutil.copy(binary_src, "bin/")
        print(f"  Binary '{binary_name}' copied to bin/")
    else:
        print(f"  WARNING: binary '{binary_name}' not found after build.")




def run_install():
    check_environment()
    os.makedirs("dependencies",exist_ok=True)
    os.makedirs("dependencies/logs", exist_ok=True)
    os.makedirs("bin", exist_ok=True)
    
    # with Halo(spinner="dots") as spinner:
    # for url, dest, patches, makefile_dest, src_subdir,binName in DEPENDENCIES:
    #     clone_repo(url,dest)
    #     # Sustituir Makefile original por el tuyo
    #     if patches is not None:
    #         if os.path.exists(f"{dirpat}/{patches}"):
    #             print(f"Replacing {binName} Makefile with {patches}")
    #             shutil.copy(f"{dirpat}/{patches}", f"{dest}/{makefile_dest}" )
    #         else:
    #             print(f"{patches} not found in {dirpat}/")
    #             sys.exit(1)
    #
    #     build_repo(dest,src_subdir,binName)
    #
    #     print(f"{binName} installed correctly.")
    with Halo(spinner="dots12", placement="right") as spinner:
        for url, dest, patches, makefile_dest, src_subdir, binName in DEPENDENCIES:
            log_file = f"dependencies/logs/{binName}.log"

            # spinner.text = f" Cloning {binName}..."
            # try:
            #     with open(log_file, "w") as log:
            #         subprocess.run(
            #             ["git", "clone", url, dest],
            #             check=True, stdout=log, stderr=log
            #         )
            # except subprocess.CalledProcessError:
            #     spinner.fail(f"Failed cloning {binName}")
            #     print(open(log_file).read())
            #     sys.exit(1)
            #

            needs_build = False

            if not os.path.exists(dest):
                # CASO 1: El repo NO existe, lo clonamos
                spinner.text = f" Cloning {binName}..."
                try:
                    with open(log_file, "w") as log:
                        subprocess.run(
                            ["git", "clone", url, dest],
                            check=True, stdout=log, stderr=log
                        )
                    needs_build = True
                except subprocess.CalledProcessError:
                    spinner.fail(f"Failed cloning {binName}")
                    print(open(log_file).read())
                    sys.exit(1)
            else:
                # CASO 2: El repo YA existe, verificamos si hay cambios
                spinner.text = f" Checking for updates in {binName}..."
                try:
                    # Traemos info del remoto
                    subprocess.run(["git", "fetch"], cwd=dest, check=True, capture_output=True)
                    pause(2) 
                    # Comparamos Local vs Remoto
                    local = subprocess.check_output(["git", "rev-parse", "@"], cwd=dest).decode().strip()
                    remote = subprocess.check_output(["git", "rev-parse", "@{u}"], cwd=dest).decode().strip()

                    if local != remote:
                        spinner.stop() # Pausamos el spinner para que el input se vea bien
                        print(f"\n[!] Update available for {binName}.")
                        ans = input(f"    Do you want to pull and rebuild? (y/n): ").lower()
                        if ans == 'y':
                            spinner.start(f" Updating {binName}...")
                            subprocess.run(["git", "pull"], cwd=dest, check=True)
                            needs_build = True
                        else:
                            spinner.start(f" Skipping update for {binName}...")
                    else:
                        # Si no hay cambios y el binario ya existe, no hace falta compilar
                        if not os.path.exists(os.path.join("bin", binName)):
                            needs_build = True
                except Exception as e:
                    spinner.warn(f" Could not check updates for {binName}, skipping...")

            if needs_build:
                if patches is not None:
                    # spinner.text = f"Patching {binName}..."
                    patch_path = f"{dirpat}/{patches}"
                    if not os.path.exists(patch_path):
                        spinner.fail(f"Patch not found: {patch_path}")
                        sys.exit(1)
                    shutil.copy(patch_path, f"{dest}/{makefile_dest}")

                spinner.text = f" Building {binName}..."
                try:
                    with open(log_file, "a") as log:
                        subprocess.run(
                            ["make"], cwd=os.path.join(dest, src_subdir),
                            check=True, stdout=log, stderr=log
                        )
                    shutil.copy(os.path.join(dest, src_subdir, binName), "bin/")
                except subprocess.CalledProcessError:
                    spinner.fail(f"Failed building {binName}")
                    print(open(log_file).read())
                    sys.exit(1)

        spinner.succeed(" All dependencies installed correctly.")

