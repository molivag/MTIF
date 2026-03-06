import sys
import os

def run_new(project_name):
    if os.path.exists(project_name):
        print(f"Error: Folder '{project_name}' already exists.")
        sys.exit(1)
    
    print(" ")
    print(f" Creating new MTIF project: {project_name}")
    os.makedirs(os.path.join(project_name, "preprocessing"))
    os.makedirs(os.path.join(project_name, "preprocessing/PlotWithPython"))
    os.makedirs(os.path.join(project_name, "preprocessing/geometry"))
    os.makedirs(os.path.join(project_name, "preprocessing/inv"))
    os.makedirs(os.path.join(project_name, "preprocessing/DEM"))
    os.makedirs(os.path.join(project_name, "preprocessing/edi_files"))
    os.makedirs(os.path.join(project_name, "preprocessing/buildMesh"))
    os.makedirs(os.path.join(project_name, "computing"))
    os.makedirs(os.path.join(project_name, "patches"))
    os.makedirs(os.path.join(project_name, "postprocessing"))
    
    # Crear mtif.conf básico
    with open(os.path.join(project_name, "mtif.toml"), "w") as f:
        f.write(
        """
        [cluster]
        cluster_mode = false
        inversion_dir = "computing"
        script = "run.slurm"
        host = "host or ip"
        user = "user_name"
        remote_results_base = "~/"
        
        # ------------------------
        # Mesh Defaults
        # ------------------------
        [mesh]
        default_mesh = "native"

        # ---- Domain ----
        domain_x = [0.0, 0.0]
        domain_y = [0.0, 0.0]
        domain_z = [0.0, 0.0]
        
        pad_x = 0.0
        pad_y = 0.0

        # ---- Topography ----
        dem_file = "file.xyz"
        dem_units = "kilometers"
        
        topo_file = "topography_for.dat"
        bathy_file = "bathymetry_for.dat"
        coast_file = "coast_line.dat"
        
        # ---- Sea ----
        has_sea = false
        sea_level = 0.0

        # ---- Refinement ----
        tet_refinement = x
        
        [mesh.surface]
        core_radius_padding = 5.0   # Margen extra sobre el radio de los sites (km)
        boundary_resolution = 20.0  # Tamaño máximo de triángulo en el borde (km)
        core_resolution = 0.5       # len en el centro (km)
        growth_factor = 3.0         # Cuánto aumenta 'len' en cada elipse hacia afuera
        levels = 3                  # Número de elipses en control.dat
        
        [mesh.sites]
        num_spheres = 5
        min_radius = 0.1            # Primera esfera (km)
        max_radius = 5.0            # Última esfera (km)
        min_edge = 0.02             # Resolución más fina (20m)
        # El 'max_edge' lo tomará automáticamente de mesh.surface.core_resolution

        
        # ------------------------
        # Postprocessing
        # ------------------------
        [post]
        post_path = "postprocessing"
        auto_post = false
        post_data = "rho_phase"
        default_axis = "period"
        
        last_job = "job_284"
        default_sites = "M-N"
        default_mode = "none"
        default_iter = A
        default_proc = B
        """
        )
    
    print(f"     Project {project_name} created successfully.")
    print(f" now run:")
    print(f" cd {project_name}")
    print(" mtif install")

