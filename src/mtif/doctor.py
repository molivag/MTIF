import sys
import platform
import shutil


def check_system():
    print("[System]")
    print(f"Operating system: {platform.system()}")


def status_ok(msg):
    print(f"[✅ OK    ] {msg}")


def status_error(msg):
    print(f"[❌ ERROR ] {msg}")


def check_dependency(executable_name):

    executable_path = shutil.which(executable_name)

    if executable_path is not None:
        status_ok(f"{executable_name} found at {executable_path}")
    else:
        status_error(f"{executable_name} not found")
    

def check_dependencies():


    print("\n[Dependencies]")
    DEPENDENCIES = [
        "gfortran",
        "ifort",
        "make",
        "tetgen",
        "meshTran",
    ]

    for dep in DEPENDENCIES:
        check_dependency(dep)   


def check_paths():
    pass

def check_python():

    print(f"Python version: {sys.version.split()[0]}")

    print("")


    # check_dependency("gfortran")
    # check_dependency("ifort")
    # check_dependency("make")



def print_summary():
    pass

def print_header():
    print("")
    print("- - - - MTIF Doctor 🩺 - - - -")
    print("")


def run_doctor():
    print_header()
    
    check_python()
    check_system()
    check_paths()
    check_dependencies()

    print_summary()
