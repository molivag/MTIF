import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import glob
import sys
import os


import argparse

def run(results_path, sites_arg, iterproc_arg, plot_x_axis, post_options=None):
    
    
    # Si solo hay 3 argumentos totales: path st1-3 freq
    if post_options in ["freq", "period"] and iterproc_arg is None and plot_x_axis is None:
        plot_x_axis = post_options
        post_options = None
    
    # coord="../PREprocessing/MeshTranFemtic/input_data/geometry/sites_coord_elev.dat"
    # df_coord = pd.read_csv (coord,sep=r'\s+')
    # =========================
    # 0) CONFIGURACIÓN DESDE TERMINAL
    # =========================
    
    # if len(sys.argv) != 6:
    #     print("Uso: ./MTpostprocess.py <path_to_results> <siteM-N> <flag> <ipX-M> <flag2>")
    #     print(" flag: ")
    #     print("     * rhoph: Write Re and Im components of Impedance Tensor")
    #     print("     * impz:  Write Re and Im components of Impedance Tensor")
    #     print(" flag2: ")
    #     print("     * freq:     Plot a loglog data against frequency")
    #     print("     * period:   Plot a log10 period in x axis")
    #     print("Ejemplo: ./global_check.py test_data_No_Topo/pureOpenMP site1-4")
    #     sys.exit(1)
    
    # =======================
    # 2) ARGUMENTO DE STES
    # =========================
    
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
    
    
    # =======================
    # 2) ARGUMENTO DE ITER and PROCESSES
    # =========================
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
    
    
    #Ahora iters y procs representan los argumentos para mergeResulst
    
    print(post_options)
    if post_options == "impz":
        print("→ Ejecutando mergeResult para impedance tensor option...")
        for ii in range(iters):
            os.system(f"cd {results_path} && mergeResult {ii} {procs} -csv && sleep 0.5")
            print('Continua iteracion: ',ii)
            os.system(f"cd {results_path} && mv result_MT.csv result_impedance_iter{ii}.csv ")
            os.system(f"cd {results_path} && mv RMS.out RMS_iter{ii}.out ")
    
    # elif post_options == "rhoph":
        print("→ Ejecutando mergeResult para Rhooa and phase optionp...")
        # ╰─❯ mergeResult 0 2 -appphs ; sleep 1 ; mv result_MT.csv result_rho_phase_iter0.csv
        for ii in range(iters):
            print(' ')
            print("iteracion",ii)
            os.system(f"cd {results_path} && mergeResult {ii} {procs} -appphs && sleep 0.5")
            os.system(f"cd {results_path} && mv result_MT.txt result_rho_phase_iter{ii}.txt ")
            os.system(f"cd {results_path} && mv RMS.out RMS_iter{ii}.out ")
    # elif post_options == "None":
    elif post_options is None:
        print(f"Preprocessing option '{post_options}' selected .") 
        print("Not merging results")
    
    else:
        print(f"❌❌ ❌ ❌ ❌  Preprocessing option '{post_options}' not defined.") 
        print("Opciones válidas: Z, rhoph or none")
        sys.exit(1)
    
    # os.system(f"cd {results_path} && ls -la")
    
    
    
    # =========================
    # 1) CONFIGURACIÓN BÁSICA
    # =========================
    # Componente a evaluar: "Zxy", "Zyx", "Zxx", "Zyy"
    print(f"  \n     📂Leyendo resultados de: {results_path}")
    print(f"     📌Sites seleccionados: {sites}")
    
    # Si tus archivos merged se llaman distinto, ajusta esto:
    PATTERN_MT = os.path.join(results_path, "result_impedance_iter*.csv")  # ejemplo: result_MT_iter05.csv
    PATTERN_RMS = os.path.join(results_path, "RMS_iter*.out")  # ejemplo: result_MT_iter05.csv
    PATTERN_RHOPH = os.path.join(results_path, "result_rho_phase_iter*.txt")  # ejemplo: result_MT_iter05.csv
    
    
    
    archivos_MT = sorted(glob.glob(PATTERN_MT))
    archivos_RMS = sorted(glob.glob(PATTERN_RMS))
    archivos_RHOPHASE = sorted(glob.glob(PATTERN_RHOPH))
    
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
    
    
    #Site,Frequency,
    # ReZxxCal,ImZxxCal,ReZxyCal,ImZxyCal,ReZyxCal,ImZyxCal,ReZyyCal,ImZyyCal
    # ReZxxObs,ImZxxObs,ReZxyObs,ImZxyObs,ReZyxObs,ImZyxObs,ReZyyObs,ImZyyObs
    # ReZxxErr,ImZxxErr,ReZxyErr,ImZxyErr,ReZyxErr,ImZyxErr,ReZyyErr,ImZyyErr
    
    #Site Frequency      AppRxxCal PhsxxCal AppRxyCal PhsxyCal AppRyxCal PhsyxCal AppRyyCal PhsyyCal
    #AppRxxObs  PhsxxObs  AppRxyObs PhsxyObs AppRyxObs PhsyxObs AppRyyObs  PhsyyObs AppRxxErr  PhsxxErr AppRxyErr  PhsxyErr      AppRyxErr       PhsyxErr      AppRyyErr       PhsyyErr
    
    #       Site     #Data            RMS
    
    n_sites = len(sites)
    # site=sites[0]
    last_it = 5
    # site = rhoph_iter[0]["Site"]==1
    
    
    #Definimos la frecuencia
    if post_options == "impz":
        freq = z_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
    
    elif post_options == "rhoph":
        freq = rhoph_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
    
    else: 
        freq = rhoph_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
        freq = z_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
        
        
    # freq_exp = freq.apply(lambda x: f"{x:.3e}")
    # print(freq_exp)
    # rho_obs = rhoph_iter[last_it][site]["AppRxyObs"]
    # phase_obs = rhoph_iter[last_it][site]["PhsxyObs"]
    #
    # rho_cal = rhoph_iter[last_it][site]["AppRxyCal"]
    # phase_cal = rhoph_iter[last_it][site]["PhsxyCal"]
    #
    
    
    #Las figuras Rho and Ph vs freq Obs y Cal en 4 componentes
    fig = plot.figure(figsize=(4*n_sites, 12))
    fig.suptitle(rf"Respuesta calculada vs observada", fontsize=16, y=0.95)
    
    # Grid exterior: 4 componentes × n_sites
    outer = gridspec.GridSpec(
        4, n_sites,
        hspace=0.35,   # espacio entre componentes
        wspace=0.3
    )
    
    #Site Frequency      AppRxxCal PhsxxCal AppRxyCal PhsxyCal AppRyxCal PhsyxCal AppRyyCal PhsyyCal
    #AppRxxObs  PhsxxObs  AppRxyObs PhsxyObs AppRyxObs PhsyxObs AppRyyObs  PhsyyObs AppRxxErr  PhsxxErr AppRxyErr  PhsxyErr      AppRyxErr       PhsyxErr      AppRyyErr       PhsyyErr
    
    axis_x = np.zeros(len(freq))
    match plot_x_axis:
        case "freq":
            axis_x = freq
        case "period":
            axis_x = np.log10(1/freq)
        case _:
            print('Define a x-axis to plot against with')
            
            
    
    component_names = ["xx", "xy", "yx", "yy"]
    
    for i, comp in enumerate(component_names):     # componentes
        for j, site in enumerate(sites):           # sites
    
            # Subgrid interno: ρ y φ pegados
            inner = gridspec.GridSpecFromSubplotSpec(
                2, 1,
                subplot_spec=outer[i, j],
                hspace=0.0
            )
    
            ax_rho = fig.add_subplot(inner[0])
            ax_phi = fig.add_subplot(inner[1], sharex=ax_rho)
    
            # ---- Aquí de momento uso los mismos datos (estructura) ----
            mask = rhoph_iter[last_it]["Site"] == site
    
            # freq = z_iter[last_it][mask]["Frequency"]
    
    
            rho_obs = rhoph_iter[last_it][mask][f"AppR{comp}Obs"]
            phase_obs = rhoph_iter[last_it][mask][f"Phs{comp}Obs"]
            #- - - 
            rho_cal = rhoph_iter[last_it][mask][f"AppR{comp}Cal"]
            phase_cal = rhoph_iter[last_it][mask][f"Phs{comp}Cal"]
    
            match plot_x_axis:
                case "freq":
                    # ---- Rho ----
                    ax_rho.loglog(axis_x, rho_obs, 'ok', markersize=3)
                    ax_rho.loglog(axis_x, rho_cal, '--', color='darkcyan', linewidth=1.25)
                    ax_rho.tick_params(labelbottom=False)
    
                    # ---- Phase ----
                    ax_phi.semilogx(axis_x, phase_obs, 'xk', markersize=3)
                    ax_phi.semilogx(axis_x, phase_cal, '--', color='crimson', linewidth=1.25)
                    # ax_phi.set_ylim(-80, -20)
                case "period":
                    # ---- Rho ----
                    ax_rho.semilogy(axis_x, rho_obs, 'ok', markersize=3)
                    ax_rho.semilogy(axis_x, rho_cal, '--', color='darkcyan', linewidth=1.25)
                    ax_rho.tick_params(labelbottom=False)
    
                    # ---- Phase ----
                    ax_phi.plot(axis_x, phase_obs, 'xk', markersize=3)
                    ax_phi.plot(axis_x, phase_cal, '--', color='crimson' , linewidth=1.25)
                    # ax_phi.set_ylim(-80, -20)
    
            if j == 0:
                ax_rho.set_ylabel(r"$\rho_{_a}$ $\left[\Omega · m \right]$",fontsize=10)
    
            if i == 0:
                ax_rho.set_title(f"Site {site}")
    
            if j == 0:
                ax_phi.set_ylabel(r"$\phi$ ($^\circ$)",fontsize=10)
    
            if i == 3:
                if plot_x_axis == 'freq':
                    ax_phi.set_xlabel("Frequency (Hz)",fontsize=9)
                else:
                    ax_phi.set_xlabel(r"$\log_{10}$ $\left[Period\ (sec) \right]$ ",fontsize=9)
    
    
            # Etiqueta del componente en la esquina
            # if j == n_sites - 1:
            ax_phi.text(
               0.95, 0.15, comp,
               transform=ax_phi.transAxes,
               ha='right',
               fontsize=12,
               fontweight='bold',
               color='blue'
           )
    
    legend_elements = [
        Line2D([0], [0], marker='o', color='k', linestyle='None',
               label=r'Obs $\rho_a$'),
        Line2D([0], [0], marker='*', color='k', linestyle='None',
               label=r'Obs $\phi$'),
        Line2D([0], [0], color='r', linestyle='--',
               label=rf'Calc. Iteration {last_it}')
    ]
    
    fig.legend(
        handles=legend_elements,
        loc='upper center',
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.76, 0.05)
    )
    
    
    
    
    
    rms_global=np.zeros(len(archivos_MT))
    for j in range(len(archivos_MT)):
        rms_global[j] = np.sqrt(np.mean(rms_iter[j]["RMS"])**2)
    
    plot.figure()
    plot.plot(range(len(archivos_MT)),rms_global, '-x', markersize=9)
    plot.xlabel("Iterations")
    plot.ylabel("Global RMS")
    plot.grid(True,which="both")
    # plot.show()
    
    
    #RMS per Site
    #keys devuelve una vista iterable y entonces se le puede apicar max()
    last_iter=max(rms_iter.keys())
    
    #Luego selecciono del diccionario el datafram de la iteracion deseada
    df = rms_iter[last_iter]
    #luego al dataframe de Site convierto toda esa fila a numeros, por lo tanto el Total
    #al final de la columna pasara a ser NaN
    df["Site"] = pd.to_numeric(df["Site"], errors="coerce")
    #Y finalmente quito la fila que contenga NaN
    df = df.dropna(subset=["Site"])
    #y ahora ya mi df me queda del mismo tamaño
    
    sites_plot = df["Site"] 
    rms_sites = df["RMS"] 
    
    plot.figure()
    plot.plot(sites_plot,rms_sites-1, 'o-')
    plot.xlabel("Site")
    plot.ylabel("RMS")
    plot.title(f"RMS per Site for Iter {last_iter}")
    plot.grid(True,alpha=0.3)
    plot.axhline(1, color='r', linestyle='--', alpha=0.5)
    plot.xticks(range(int(sites_plot.min()),int(sites_plot.max())+1,2))
    plot.show()
    
    
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

