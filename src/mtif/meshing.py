from mtif.config import read_config
from mtif.config import update_meshtran_io_from_toml
from mtif.tools.check_domain import run
import subprocess
import sys
import os

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#
# Comando para construir la malla 
#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def run_mesh(args):
# --- MODO CHECK ---
    if args.check:
        target_path = os.path.join("bin", "check_domain.py")
        if os.path.exists(target_path):
            print("     == Checking mesh geometry ==")
            run()
        else:
            print("check_domain.py not found.")
        return   # <-- IMPORTANTE (sale de la función)

    # target_path = os.path.join( "preprocessing", "buildMesh", "reindexing_tetgen.py")
    # if not os.path.exists(target_path):
    #     print(f"ERROR: reindexing_tetgen.py not found at {target_path}")
    #     sys.exit(1)
    #

    if not os.path.exists("bin/set_meshtran.io"):
        print("ERROR: set_meshtran.io not found.")
        sys.exit(1)


    config = read_config()
    mesh_cfg = config["mesh"]

    mesh_type = args.mesh if args.mesh else mesh_cfg["default_mesh"]

    print("== Updating set_meshtran.io from mtif.toml ==")
    update_meshtran_io_from_toml(config, mesh_type)
    
    print("     == Running meshTran ==")
    subprocess.run(["bin/meshTranPreprocessing"], check=True)

