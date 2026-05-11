import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import glob
import sys
import os

from mtif.tools.result_visualization import plot_visualization


import argparse

def parse_iterproc(iterproc_arg):
    if iterproc_arg is None:
        print("Falta argumento ipX-M")
        sys.exit(1)
    if not iterproc_arg.startswith("ip"):
        print("Formato incorrecto en iter-proc. Ejemplo: ip11-4")
        sys.exit(1)
    
    try:
        rango = iterproc_arg[2:]        # quita "ip"
        iters, procs = rango.split("-")  # separa X y M
        iters = int(iters)
        procs = int(procs)
    except:
        print("Formato inválido. Usa: stX-Y  (ejemplo: st1-4)")
        sys.exit(1)
    iters = iters+1

    return iters, procs

def parse_sites(sites_arg):
    if not sites_arg.startswith("st"):
        print("Formato de sites incorrecto. Usa por ejemplo: st1-4")
        sys.exit(1)
    try:
        rango = sites_arg[2:]           # quita "st"
        inicio, fin = rango.split("-")  # separa 1 y 4
        inicio = int(inicio)
        fin = int(fin)
    except:
        print("Formato inválido. Usa: stX-Y  (ejemplo: st1-4)")
        sys.exit(1)
    
    if inicio > fin:
        print("El rango está invertido.")
        sys.exit(1)
    
    sites = list(range(inicio, fin + 1))

    return sites


def build_postprocessing_paths(results_path):

    BASE_DIR = os.getcwd()
    paths = {

        "mt_pattern":
            os.path.join(results_path, "result_impedance_iter*.csv"),

        "rms_pattern":
            os.path.join(results_path, "RMS_iter*.out"),

        "rhoph_pattern":
            os.path.join(results_path, "result_rho_phase_iter*.txt"),

        "stats_path":
            os.path.join(results_path, "femtic.cnv"),

        "coord_path":
            os.path.join(
                BASE_DIR,
                "preprocessing",
                "geometry",
                "sites_coord_elev.dat"
            ),

        "coast_path":
            os.path.join(
                BASE_DIR,
                "preprocessing",
                "geometry",
                "coast_line.dat"
            ),

        "domain_path":
            os.path.join(
                BASE_DIR,
                "preprocessing",
                "geometry",
                "analysis_domain.dat"
            ),

    }

    return paths



def merge_impedance(results_path, iters, procs):
    print("→ Ejecutando mergeResult para impedance tensor option...")
    for ii in range(iters):
        os.system(f"cd {results_path} && mergeResult {ii} {procs} -csv && sleep 0.5")
        print('Continua iteracion: ',ii)
        os.system(f"cd {results_path} && mv result_MT.csv result_impedance_iter{ii}.csv ")
        os.system(f"cd {results_path} && mv RMS.out RMS_iter{ii}.out ")


def merge_rhoph(results_path, iters, procs):
    print("→ Ejecutando mergeResult para Rhooa and phase optionp...")
    # ╰─❯ mergeResult 0 2 -appphs ; sleep 1 ; mv result_MT.csv result_rho_phase_iter0.csv

    for ii in range(iters):

        print("iteracion",ii)
        os.system(f"cd {results_path} && mergeResult {ii} {procs} -appphs && sleep 0.5")
        os.system(f"cd {results_path} && mv result_MT.txt result_rho_phase_iter{ii}.txt ")
        os.system(f"cd {results_path} && mv RMS.out RMS_iter{ii}.out ")
        print(f'esto es la iteracion {ii}')

def load_iteration_results(archivos_MT, archivos_RMS, archivos_RHOPHASE,last_it):
    #Inicializo mi diccionario a  0
    z_iter = {}
    rms_iter = {}
    rhoph_iter = {}
    #El diccionario tendra la forma
    #iter {1:DataFrameZ_iter1, 2:DataFramZ_iter2,...}
    for ii in archivos_MT:
        nombre = os.path.basename(ii)
        numero = int(nombre.replace("result_impedance_iter","").replace(".csv",""))
        dfZ= pd.read_csv(ii)
        z_iter[numero]=dfZ
    
    for ii in archivos_RMS:
        nombre = os.path.basename(ii)
        numero = int(nombre.replace("RMS_iter","").replace(".out",""))
        dfRMS = pd.read_csv(ii,sep=r'\s+')
        dfRMS.columns = dfRMS.columns.str.strip() # --> trim espacios
        rms_iter[numero] = dfRMS
    
    for ii in archivos_RHOPHASE:
        nombre = os.path.basename(ii)
        numero = int(nombre.replace("result_rho_phase_iter","").replace(".txt",""))
        dfRHOPHASE = pd.read_csv (ii,sep=r'\s+')
        dfRHOPHASE.columns = dfRHOPHASE.columns.str.strip() # --> trim espacios
        rhoph_iter[numero] = dfRHOPHASE
    
    #Mis tres diccionarios
    ## z_iter ; rms_iter ; rhoph_iter


    #Definimos la frecuencia
    freq = z_iter[last_it][z_iter[last_it]["Site"] == 1]["Frequency"]

    return z_iter, rms_iter, rhoph_iter, freq

def getting_results_FEMTIC(paths):
    # sitesRMS = pd.read_csv(coord_path,sep=r'\s+', header=None)
    sitesRMS = pd.read_csv(paths["coord_path"],sep=r'\s+', header=None)
    sitesRMS = sitesRMS.iloc[:,0:3]
    sitesRMS.columns = ["SiteName","X","Y"]
    #adding an extra column to be able the merge with RMS file data
    sitesRMS["Site"] = np.arange(1,len(sitesRMS)+1)

    coast      = np.loadtxt(paths["coast_path"], skiprows=1)
    domain = np.loadtxt(paths["domain_path"])

    run_statistics = pd.read_csv(paths["stats_path"] , sep=r'\s+',usecols=[0,4,6])

    return run_statistics, sitesRMS, coast, domain





# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
# = = = = = =                   MAIN ROUTINE                = = = = = = = = = = = 
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
def run(results_path, sites_arg, iterproc_arg, plot_x_axis, post_options=None, components=None):
    
    
    # Si solo hay 3 argumentos totales: path st1-3 freq
    if post_options in ["freq", "period"] and iterproc_arg is None and plot_x_axis is None:
        plot_x_axis = post_options
        post_options = None
    
    iters, procs = parse_iterproc(iterproc_arg)
    last_it = iters-1    #       ---> aqui le quitamos el + 1 del range agregado al inicio
    sites = parse_sites(sites_arg)
    print(f"DEBUG: iters={iters}, last_it={last_it}")  # ← añade esta línea
    
    #Ahora iters y procs representan los argumentos para mergeResulst
    if post_options == "impz":
        merge_impedance(results_path, iters, procs)
    
    # elif post_options == "rhoph":
        merge_rhoph(results_path, iters, procs)

    # elif post_options == "None":
    elif post_options == "none":
        print(f"Preprocessing option '{post_options}' selected.") 
        print("Results already merged")
    
    else:
        print(f"❌ ❌ ❌ ❌ ❌  Preprocessing option '{post_options}' not defined.") 
        print("Opciones válidas: Z, rhoph or none")
        sys.exit(1)
    
    # os.system(f"cd {results_path} && ls -la")
    print(f"  \n     📂Leyendo resultados de: {results_path}")
    print(f"     📌Sites seleccionados: {sites}")
    
    
    paths = build_postprocessing_paths(results_path)
    archivos_MT = sorted(glob.glob(paths["mt_pattern"]))
    archivos_RMS = sorted(glob.glob(paths["rms_pattern"]))
    archivos_RHOPHASE = sorted(glob.glob(paths["rhoph_pattern"]))
    
    
    z_iter, rms_iter, rhoph_iter, freq = load_iteration_results(archivos_MT, archivos_RMS, archivos_RHOPHASE,last_it)
    run_statistics, sitesRMS, coast, domain = getting_results_FEMTIC(paths)

    
    #Site,Frequency,
    # ReZxxCal,ImZxxCal,ReZxyCal,ImZxyCal,ReZyxCal,ImZyxCal,ReZyyCal,ImZyyCal
    # ReZxxObs,ImZxxObs,ReZxyObs,ImZxyObs,ReZyxObs,ImZyxObs,ReZyyObs,ImZyyObs
    # ReZxxErr,ImZxxErr,ReZxyErr,ImZxyErr,ReZyxErr,ImZyxErr,ReZyyErr,ImZyyErr
    
    #Site Frequency      AppRxxCal PhsxxCal AppRxyCal PhsxyCal AppRyxCal PhsyxCal AppRyyCal PhsyyCal
    #AppRxxObs  PhsxxObs  AppRxyObs PhsxyObs AppRyxObs PhsyxObs AppRyyObs  PhsyyObs AppRxxErr  PhsxxErr AppRxyErr  PhsxyErr      AppRyxErr       PhsyxErr      AppRyyErr       PhsyyErr
    #       Site     #Data            RMS
    
   


    plot_visualization(
        sites, 
        components, 
        freq, 
        domain, 
        coast, 
        iters, 
        plot_x_axis, 
        archivos_MT, 
        rms_iter, 
        rhoph_iter, 
        sitesRMS, 
        run_statistics,
        last_it
    )



    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("results_path")
    parser.add_argument("sites_arg")
    parser.add_argument("iterproc_arg")
    parser.add_argument("plot_x_axis")
    parser.add_argument("post_options", nargs="?")
    
    args = parser.parse_args()
    
    run(
        args.results_path,
        args.sites_arg,
        args.iterproc_arg,
        args.plot_x_axis,
        args.post_options
    )

