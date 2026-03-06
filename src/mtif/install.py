
import subprocess
import shutil
import sys
import os

MAKETETRAMESH_URL = "https://github.com/yoshiya-usui/makeTetraMesh.git"
TETGEN2FEMTIC_URL = "https://github.com/yoshiya-usui/TetGen2Femtic.git"
MAKEMTR_URL_URL = "https://github.com/yoshiya-usui/makeMtr.git"
MERGERESULT_URL = "https://github.com/yoshiya-usui/mergeResultOfFEMTIC.git"
FEMTIC_URL = "https://github.com/yoshiya-usui/femtic.git"
TETGEN_URL = "https://github.com/TetGen/TetGen.git"
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

