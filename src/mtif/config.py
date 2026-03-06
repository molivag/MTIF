import tomllib
import sys

def read_config():
    try:
        with open("mtif.toml", "rb") as f:
            config = tomllib.load(f)
        return config
    except FileNotFoundError:
        print("ERROR: mtif.toml not found.")
        sys.exit(1)

def update_meshtran_io_from_toml(config,mesh_type):
    mesh_cfg = config["mesh"]

    #from TOML to io
    replacements = {
        
        "MESH_NATURE": mesh_type,
        "DEM_FILE": mesh_cfg["dem_file"],
        "DEM_UNITS": mesh_cfg["dem_units"],
        "XMIN_DOM": mesh_cfg["domain_x"][0],
        "XMAX_DOM": mesh_cfg["domain_x"][1],
        "YMIN_DOM": mesh_cfg["domain_y"][0],
        "YMAX_DOM": mesh_cfg["domain_y"][1],
        "ZMIN_DOM": mesh_cfg["domain_z"][0],
        "ZMAX_DOM": mesh_cfg["domain_z"][1],
        "PAD_X":mesh_cfg["pad_x"],
        "PAD_Y": mesh_cfg["pad_y"],
        "HAS_SEA":"YES" if mesh_cfg["has_sea"]else "NO",
        "SEA_LEVEL": mesh_cfg["sea_level"],
        "ITER_TET_REFI": mesh_cfg["tet_refinement"],
        "TOPO_FILE": mesh_cfg["topo_file"],
        "BATHY_FILE": mesh_cfg["bathy_file"],
        "COSLI_FILE": mesh_cfg["coast_file"],
    }
    with open("bin/set_meshtran.io","r") as f:
        lines = f.readlines()
    
    new_lines = []
    
    for line in lines:
        stripped = line.strip()

        if "=" in stripped:
            key = stripped.split("=")[0].strip()

            if key in replacements:
                new_value = replacements[key] 
                new_line = f"{key} = {new_value}\n"
                new_lines.append(new_line)
                continue

        new_lines.append(line)

    with open("bin/set_meshtran.io", "w") as f:
        f.writelines(new_lines)

    print(" 📖 set_meshtran.io updated from mtif.toml")

