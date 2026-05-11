#!/usr/bin/env python3

import argparse
from mtif.config import read_config
from mtif.createNew import run_new
from mtif.download import run_download
from mtif.install import run_install
from mtif.doctor import run_doctor
from mtif.meshing import run_mesh
from mtif.postprocessing import run_post 
from mtif.runInversion import run_inversion
from mtif.upload import run_upload

def main():
    parser = argparse.ArgumentParser(
        prog="mtif",
        description="""
        MTIF - Magnetotelluric Inversion Framework © 2026
        An Integrated framework for preprocessing, inversion and postprocessing of
        3D magnetotelluric data using FEMTIC as inversion engine.

        Author: Marco A Oliva Gutierrez
            University of Barcelona - Geomodels Research Institute
        """,
        epilog="""
    Examples:
      mtif create
      mtif install
      mtif mesh
      mtif run
      mtif post job_284 --sites 1-10 --mode impz --iter 8 --proc 2 --axis freq
    
    For detailed help on a command:
      mtif <command> --help
    """,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--version",
        action="version",
        version="MTIF v0.1.0"
    )



    subparsers = parser.add_subparsers(
    dest="command",
    required=True
    )
    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    create_parser = subparsers.add_parser(
        "create",
        help="  Create a new MTIF project",
        description="Create a new MTIF project directory with predefined structure."
    )
    create_parser.add_argument(
        "project_name",
        help="Name of the new project directory"
    )
    
    # --------------------------------------------------
    # INSTALL
    # --------------------------------------------------
    install_parser = subparsers.add_parser(
        "install",
        help="Install required third-party dependencies",
        description="Clone and compile required tools such as FEMTIC and TetGen."
    )
    
    # --------------------------------------------------
    # DOCTOR
    # --------------------------------------------------
    doctor_parser = subparsers.add_parser(
        "doctor",
        help="Check dependencies",
        description="Execute a complete checker of dependencies and version installed."
    )

    # --------------------------------------------------
    # MESH
    # --------------------------------------------------
    mesh_parser = subparsers.add_parser(
        "mesh",
        help="Run mesh preprocessing",
        description="Execute MeshTran preprocessing pipeline."
    )
    
    mesh_parser.add_argument(
        "--mesh",
        choices=["native", "external"],
        help="Site range (native (default)  or external)"
    )

    mesh_parser.add_argument(
        "--check",
        action="store_true",
        help="Only check and plot existing mesh (no mesh generation)"
    )
    
    # --------------------------------------------------
    # RUN
    # --------------------------------------------------
    run_parser = subparsers.add_parser(
        "run",
        help="Run inversion",
        description="Launch FEMTIC inversion locally or in cluster mode."
    )
    # --------------------------------------------------
    # UPLOAD
    # --------------------------------------------------
    download_parser = subparsers.add_parser(
        "upload",
        help="Upload computing/ folder contents to cluster into <project_name>/",
        description="Establish a ssh conexion to create a folder called <project_name> then by rsync upload files to cluster."
    )
    # download_parser.add_argument(
    #     "jobs",
    #     nargs="+",
    #     help="Job prefixes to download (e.g. job_284 job_293 job_301)"
    # )
    # --------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------
    download_parser = subparsers.add_parser(
        "download",
        help="Download job folders from cluster into postprocessing/",
        description="Validate remote job folders first, then download contents into local postprocessing/job_XXX/."
    )
    download_parser.add_argument(
        "jobs",
        nargs="+",
        help="Job prefixes to download (e.g. job_284 job_293 job_301)"
    )
    
    # --------------------------------------------------
    # POST
    # --------------------------------------------------
    post_parser = subparsers.add_parser(
        "post",
        help="Run postprocessing",
        description="Merged results and generate plots from inversion outputs."
    )
    
    post_parser.add_argument(
        "job",
        nargs="?",
        help="Job name (folder inside postprocessing)"
    )
    
    post_parser.add_argument(
        "--sites",
        help="Site range (e.g., 1-10)"
    )

    post_parser.add_argument(
    "--comp",
    nargs="+",                    # acepta uno o más valores
    choices=["xx", "xy", "yx", "yy"],
    default=["xy", "yx"],         # default si no se pasa nada
    help="Componentes a plotear (e.g. --comp xy yx)"
    )
    
    post_parser.add_argument(
        "--mode",
        choices=["impz", "rhoph"],
        help="Postprocessing mode"
    )
    
    post_parser.add_argument(
        "--iter",
        type=int,
        help="Number of iterations"
    )
    
    post_parser.add_argument(
        "--proc",
        type=int,
        help="Number of processes"
    )

    post_parser.add_argument(
        "--axis",
        help="Set x axis (e.g., freq or period)"
    )


    args = parser.parse_args()

    if args.command == "create":
        run_new(args.project_name)

    elif args.command == "install":
        run_install()

    elif args.command == "doctor":
        run_doctor()

    elif args.command == "mesh":
        run_mesh(args)

    elif args.command == "run":
        config = read_config()
        run_inversion(config)

    elif args.command == "upload":
        run_upload()

    elif args.command == "download":
        run_download(args)

    elif args.command == "post":
        run_post(args)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
