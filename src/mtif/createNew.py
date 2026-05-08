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



    # Crear mtif.conf básico
    with open(os.path.join(project_name, "patches/Makefile_femtic"), "w") as f:
        f.write(
    """# ======================================================
    # Makefile para Intel oneAPI 2024 + Intel MPI + MKL
    # ======================================================
    
    # Compiladores Intel MPI (oneAPI)
    CXX           = mpiicx
    CC            = mpiicx
    
    # Directorios de Intel oneAPI
    ONEAPI_ROOT   = /opt/intel/oneapi
    MKLROOT       = $(ONEAPI_ROOT)/mkl/latest
    COMPILER_ROOT = $(ONEAPI_ROOT)/compiler/latest
    
    # Flags de compilación
    CXXFLAGS      = -O3 -m64\\
                    -qopenmp\\
                    -D_LINUX\\
                    -DMKL_ILP64\\
                    -D_USE_OMP\\
                    -DNDEBUG\\
                    -I$(MKLROOT)/include\\
    
    # Flags de enlace
    LDFLAGS       = -L$(MKLROOT)/lib/intel64
                    -L$(COMPILER_ROOT)/lib/intel64_lin
    
    # -lmkl_intel_ilp64 -lmkl_intel_thread -lmkl_core
    # Enlace con MKL ILP64 + Intel MPI Threading
    LIBS          = -Wl,--start-group
                    -lmkl_intel_ilp64 -lmkl_intel_thread -lmkl_core
                    -Wl,--end-group
                    -liomp5 -lpthread -lm -ldl -lstdc++
    
    # Archivos objeto
    OBJS          = AnalysisControl.o
                    ComplexSparseMatrix.o
                    ComplexSparseSquareMatrix.o
                    ComplexSparseSquareSymmetricMatrix.o
                    ComplexSparseSquareUnsymmetricMatrix.o
                    DoubleSparseMatrix.o
                    DoubleSparseSquareMatrix.o
                    DoubleSparseSquareSymmetricMatrix.o
                    DoubleSparseSquareUnsymmetricMatrix.o
                    Forward2D.o
                    Forward2DQuadrilateralElement.o
                    Forward2DNonConformingQuadrilateralElement0thOrderEdgeBased.o
                    Forward2DQuadrilateralElementEdgeBased.o
                    Forward2DSquareElement.o
                    Forward2DSquareElement0thOrderEdgeBased.o
                    Forward2DSquareElement1stOrderEdgeBased.o
                    Forward2DSquareElement1stOrderNodeBased.o
                    Forward2DSquareElement2ndOrderNodeBased.o
                    Forward2DSquareElementEdgeBased.o
                    Forward2DSquareElementNodeBased.o
                    Forward2DTriangleElement.o
                    Forward2DTriangleElement0thOrderEdgeBased.o
                    Forward2DTriangleElement1stOrderNodeBased.o
                    Forward2DTriangleElementEdgeBased.o
                    Forward2DTriangleElementNodeBased.o
                    Forward3D.o
                    Forward3DBrickElement0thOrder.o
                    Forward3DNonConformingHexaElement0thOrder.o
                    Forward3DTetraElement0thOrder.o
                    Inversion.o
                    InversionGaussNewtonModelSpace.o
                    InversionGaussNewtonDataSpace.o
                    main.o
                    MeshData.o
                    MeshDataBrickElement.o
                    MeshDataNonConformingHexaElement.o
                    MeshDataTetraElement.o
                    AdditinalOutputPoint.o
                    ObservedDataStation.o
                    ObservedDataStationPoint.o
                    ObservedDataStationMT.o
                    ObservedDataStationApparentResistivityAndPhase.o
                    ObservedDataStationHTF.o
                    ObservedDataStationVTF.o
                    ObservedDataStationPT.o
                    ObservedDataStationNMT.o
                    ObservedDataStationNMT2.o
                    ObservedDataStationNMT2ApparentResistivityAndPhase.o
                    ObservedData.o
                    OutputFiles.o
                    PARDISOSolver.o
                    PARDISOSolverComplex.o
                    PARDISOSolverDouble.o
                    ResistivityBlock.o
                    RougheningMatrix.o
                    RougheningSquareMatrix.o
                    Util.o
    
    PROGRAM       = femtic
    
    all: $(PROGRAM)
    
    $(PROGRAM): $(OBJS)
    \t$(CXX) $(CXXFLAGS) $(OBJS) $(LDFLAGS) $(LIBS) -o $(PROGRAM)
    
    clean:
	\trm -f *.o *~ $(PROGRAM)
    
    """
    )
    with open(os.path.join(project_name, "patches/Makefile_dep4"), "w") as f:
        f.write(
            """
            CXX           = icpx
            CC            = icpx
            CXXFLAGS      = -O2 \
                            -DNDEBUG 
            DEST          = ./
            
            PROGRAM       = mergeResult
            
            all:            $(PROGRAM)
            
            $(PROGRAM): mergeResult.cpp 
            	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(LIBS) -o $(PROGRAM) mergeResult.cpp 
            
            
            clean:;		rm -f *.o *~ $(PROGRAM)
        """
        )

    with open(os.path.join(project_name, "patches/Makefile_dep3"), "w") as f:
        f.write(
            """
            CXX           = icpx
            CC            = icpx
            CXXFLAGS      = -O2 \
                            -DNDEBUG
            DEST          = ./
            LIBS          = 
            OBJS          = TopographicData.o MeshData.o main.o
            PROGRAM       = TetGen2Femtic
            
            all:            $(PROGRAM)
            
            $(PROGRAM):     $(OBJS)
            	$(CXX) $(CXXFLAGS) $(OBJS) $(LDFLAGS) $(LIBS) -o $(PROGRAM)
            
            clean:;		rm -f *.o *~ $(PROGRAM)
            """
        )


    with open(os.path.join(project_name, "patches/Makefile_dep2"), "w") as f:
        f.write(
        """
            CXX           = icpx
            CC            = icpx
            CXXFLAGS      = -O2 \
                            -DNDEBUG 
            DEST          = ./
            OBJS          = ObservationPoint.o \
                            ObservationLine.o \
                            main.o
            PROGRAM       = makeMtr
            
            all:            $(PROGRAM)
            
            $(PROGRAM):     $(OBJS)
            	$(CXX) $(CXXFLAGS) $(OBJS) $(LDFLAGS) $(LIBS) -o $(PROGRAM)
            
            clean:;		rm -f *.o *~ $(PROGRAM)
        """
        )

    with open(os.path.join(project_name, "patches/Makefile_dep1"), "w") as f:
        f.write(
            """
            CXX           = icpx
            CC            = icpx
            CXXFLAGS      = -O3 \
                            -qopenmp \
                            -D_USE_OMP \
                            -D_THICKNESS_FUNC \
                            -DNDEBUG 
            DEST          = ./
            LIBS          = -qmkl=parallel
            OBJS          = AnalysisDomain.o \
                            BoundaryCurve.o \
                            BoundaryCurveInner.o \
                            BoundaryCurveList.o \
                            BoundaryCurveOuter.o \
                            BoundaryCurveSubInner.o \
                            CoastLine.o \
                            CoastLineList.o \
                            Control.o \
                            Ellipsoids.o \
                            main.o \
                            LakeList.o \
                            Node.o \
                            NodeList.o \
                            ObservationLine.o \
                            ObservationPoint.o \
                            ObservingSiteList.o \
                            OutputFiles.o \
                            TopographyData.o \
                            TopographyDataList.o \
                            Triangle.o \
                            TriangleList.o \
                            Util.o
            PROGRAM       = makeTetraMesh
            
            all:            $(PROGRAM)
            
            $(PROGRAM):     $(OBJS)
            	$(CXX) $(CXXFLAGS) $(OBJS) $(LDFLAGS) $(LIBS) -o $(PROGRAM)
            
            clean:;		rm -f *.o *~ $(PROGRAM)
            """
        )

    
    print(f"     Project {project_name} created successfully.")
    print(f" now run:")
    print(f" cd {project_name}")
    print(" mtif install")

