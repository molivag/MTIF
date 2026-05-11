import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.gridspec as gridspec
from pyarrow import string
from scipy.interpolate import griddata
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
import glob
import sys
import os


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
    #     # Si tus archivos merged se llaman distinto, ajusta esto:
    # PATTERN_MT = os.path.join(results_path, "result_impedance_iter*.csv")  # ejemplo: result_MT_iter05.csv
    # PATTERN_RMS = os.path.join(results_path, "RMS_iter*.out")  # ejemplo: result_MT_iter05.csv
    # PATTERN_RHOPH = os.path.join(results_path, "result_rho_phase_iter*.txt")  # ejemplo: result_MT_iter05.csv
    # PATTERN_STATS = os.path.join(results_path, "femtic.cnv")  # ejemplo: result_MT_iter05.csv
    # coord_path = os.path.join(BASE_DIR,"preprocessing","geometry","sites_coord_elev.dat")
    # coast_path = os.path.join(BASE_DIR,"preprocessing","geometry","coast_line.dat")
    # domain_path = os.path.join(BASE_DIR,"preprocessing","geometry","analysis_domain.dat")
    # # dominio del modelo

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

# def plot_mt_response(sites, components, freq, plot_x_axis, rhoph_iter, z_iter, last_it, iters):
def plot_mt_response(sites, components, freq, plot_x_axis, rhoph_iter, last_it):

    n_sites = len(sites)

    if components is None:
        component_names = ["xy", "yx"]  # default
    else:
        component_names = components
    

    #Las figuras Rho and Ph vs freq Obs y Cal en 4 componentes
    fig = plot.figure(figsize=(4*n_sites, 12))
    fig.suptitle(rf"Respuesta calculada vs observada", fontsize=16, y=0.95)
    
    n_comp = len(component_names)
    # Grid exterior: 4 componentes × n_sites
    outer = gridspec.GridSpec(
        # 4, n_sites,
        n_comp, n_sites,
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
            
            
    
    # component_names = ["xx", "xy", "yx", "yy"]

    # component_names = ["xy", "yx",]
    
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
            rho_err = rhoph_iter[last_it][mask][f"AppR{comp}Err"]
            phs_err = rhoph_iter[last_it][mask][f"Phs{comp}Err"]

            #- - - 
            rho_cal = rhoph_iter[last_it][mask][f"AppR{comp}Cal"]
            phase_cal = rhoph_iter[last_it][mask][f"Phs{comp}Cal"]
    
            match plot_x_axis:
                case "freq":
                    # ---- Rho ----
                    ax_rho.errorbar(axis_x, rho_obs, 
                                    yerr=rho_err,
                                    fmt='og',
                                    markersize=4,
                                    capsize=4,
                                    elinewidth=1.0,
                                    markeredgewidth=1.0,
                                    alpha=0.7)

                    ax_rho.plot(axis_x, rho_cal, '--', color='darkcyan', linewidth=1.5)
                    ax_rho.tick_params(labelbottom=False)
                    # ax_rho.set_xscale('log')
                    ax_rho.set_yscale('log')
                    ax_rho.set_ylim(1, 1000)
                    # ax_rho.set_xlim(0.5e-3, 1.5e3)
                    ax_rho.set_xlim(1.5e4, 0.5e-4) #de altas a bajas frecuencias
                    ax_rho.grid(axis='x', linestyle='--', alpha=0.5)
                    ax_rho.grid(axis='y', linestyle='--', alpha=0.5)
    
                    # ---- Phase ----
                    ax_phi.errorbar(axis_x, phase_obs,
                                    yerr=phs_err,
                                    fmt='xr', 
                                    markersize=4, 
                                    capsize=4, 
                                    elinewidth=1.0, 
                                    markeredgewidth=1.0,
                                    alpha=0.7)

                    # ax_phi.plot(axis_x, phase_cal, '--', color='crimson' , linewidth=1.25)
                    # ax_phi.semilogx(axis_x, phase_obs, 'xk', markersize=3)
                    ax_phi.semilogx(axis_x, phase_cal, '--', color='crimson', linewidth=1.5)
                    ax_phi.set_ylim(-180, 180)
                    ax_phi.grid(axis='x', linestyle='--', alpha=0.5)
                    ax_phi.grid(axis='y', linestyle='--', alpha=0.5)

                    # if comp in ["xy"]:
                    #     # ← Añade esto:
                    #     ax_phi.axhline(-45,  color='plum', linewidth=0.9, linestyle='-', alpha=0.8)
                    #
                    # if comp in ["yx"]:
                    #     ax_phi.axhline(135,  color='maroon', linewidth=0.9, linestyle='-', alpha=0.8)



                    # fig, (ax1, ax2) = plot.subplots(2)
                    # fig.suptitle('Axes values are scaled individually by default')
                    # ax_rho.plot(axis_x, rho_cal,)
                    # ax_rho.set_xlabel("Frequency (Hz)",fontsize=9)
                    # ax_phi.semilogx(axis_x, phase_cal)
                    # ax_rho.set_xlabel("Frequency (Hz)",fontsize=9)








                case "period":
                    # Si el error es más de 10 veces el dato, podrías opacar la barra
                    # alpha_val = 1.0 if (rho_err.mean() < rho_obs.mean() * 2) else 0.4
                    # ax_rho.errorbar(axis_x, rho_obs, yerr=rho_err, fmt='ok', alpha=alpha_val)
                    # ---- Rho ----
                    ax_rho.errorbar(axis_x, rho_obs,
                                    yerr=rho_err,
                                    fmt='ok',
                                    markersize=3,
                                    capsize=3,
                                    elinewidth=0.8,
                                    markeredgewidth=0.8,
                                    alpha=0.7)
                    ax_rho.plot(axis_x, rho_cal, '--', color='darkcyan', linewidth=1.25)
                    ax_rho.tick_params(labelbottom=False)
                    ax_rho.set_yscale('log')
                    # ax_rho.set_ylim(1, 1000)
    
                    # ---- Phase ----
                    ax_phi.errorbar(axis_x, phase_obs,
                                    yerr=phs_err,
                                    fmt='xk', 
                                    markersize=3, 
                                    capsize=3, 
                                    elinewidth=0.8, 
                                    markeredgewidth=0.8,
                                    alpha=0.7)
                    ax_phi.plot(axis_x, phase_cal, '--', color='crimson' , linewidth=1.25)
                    # ax_phi.set_ylim(-180, 180)
    
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
                    ax_phi.set_xlabel(r"$\log_{10}$ $\left[Period \right] (sec)$ ",fontsize=9)
    
    
            # Etiqueta del componente en la esquina
            # if j == n_sites - 1:
            ax_phi.text(
               0.95, 0.15, comp,
               transform=ax_phi.transAxes,
               ha='right',
               fontsize=12,
               fontweight='bold',
               color='blue')
    
    legend_elements = [
        Line2D([0], [0], marker='o', color='k', linestyle='None',
               label=r'Obs $\rho_a$'),
        Line2D([0], [0], marker='*', color='k', linestyle='None',
               label=r'Obs $\phi$'),
        Line2D([0], [0], color='crimson', linestyle='--',
               label=rf'$\rho_a$ Calc. Iteration {last_it}'),
        Line2D([0], [0], color='darkcyan', linestyle='--',
               label=rf'$\phi$ Calc. Iteration {last_it}')
    ]
    
    fig.legend(
        handles=legend_elements,
        handletextpad=0.1,  # <--- ESTO reduce el espacio entre el símbolo y el texto
        handlelength=1.5,   # Reduce el largo del área del símbolo
        loc='upper center',
        ncol=4,
        frameon=False,
        bbox_to_anchor=(0.76, 0.05)
    )


def plot_global_RMSvsIter(archivos_MT, rms_iter, iters):
    tot = range(iters)
    inicio = tot[0]
    fin = tot[-1]

    rms_global=np.zeros(len(archivos_MT))
    for j in range(len(archivos_MT)):
        rms_global[j] = np.sqrt(np.mean(rms_iter[j]["RMS"])**2)

    plot.figure()
    plot.plot(range(len(archivos_MT)),rms_global, '-x', markersize=9)
    plot.xlabel("Iterations")
    plot.ylabel("Global RMS")
    plot.grid(True,which="both")
    plot.xticks(range(inicio, fin, 1))


def plot_RMS_per_site(rms_iter, last_iter):
    #keys devuelve una vista iterable y entonces se le puede apicar max()
    # last_iter=max(rms_iter.keys())

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
    plot.xticks(range(int(sites_plot.min()),int(sites_plot.max())+1,3))


def plot_RMS_heatMap(domain, coast, rms_iter, sitesRMS, last_iter):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # plot the coordinate map with RMS error in each station
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # =====================================================
    # 1) LEER COORDENADAS DE ESTACIONES
    # =====================================================


    # Ahora 'sites' contiene:
    # Site | X | Y


    # =====================================================
    # 2) LEER RMS DE LA ITERACION
    # =====================================================
    # rms_table ya lo tienes en memoria o leído desde FEMTIC
    # debe tener columnas:
    # Site | #Data | RMS

    # rms_selected = rms_iter[last_it]
    # rms_df = rms_selected[["Site","RMS"]]


    # last_iter=max(rms_iter.keys())
    rms_selected = rms_iter[last_iter]
    rms_df = rms_selected[["Site", "RMS"]].copy()  # .copy() para no modificar el diccionario original
    rms_df["Site"] = pd.to_numeric(rms_df["Site"], errors="coerce")  # convierte texto a número, y "Total" → NaN
    rms_df = rms_df.dropna(subset=["Site"])  # elimina la fila donde Site es NaN (la fila "Total")

    # =====================================================
    # 3) UNIR RMS CON COORDENADAS
    # =====================================================
    data = pd.merge(sitesRMS, rms_df, on="Site")
    # Ahora data tiene:
    # Site | SiteName | X | Y | RMS


    # =====================================================
    # 4) CREAR GRID REGULAR DE INTERPOLACION
    # =====================================================
    x = data["Y"].to_numpy()
    y = data["X"].to_numpy()
    z = data["RMS"].to_numpy()


    xmin, xmax = domain[1]
    ymin, ymax = domain[0]

    nx, ny = 300, 300

    xi = np.linspace(xmin, xmax, nx)
    yi = np.linspace(ymin, ymax, ny)

    Xi, Yi = np.meshgrid(xi, yi)


    # =====================================================
    # 5) INTERPOLAR RMS EN EL GRID
    # =====================================================
    Zi = griddata(
        points=(x, y),
        values=z,
        xi=(Xi, Yi),
        method="cubic"      # opciones: 'linear', 'nearest'
    )


    # =====================================================
    # 6) PLOT DEL HEATMAP
    # =====================================================
    plot.figure(figsize=(8,10))

    plot.contourf(Xi,Yi, Zi, levels=20, cmap="afmhot_r")

    # Dibujar estaciones encima
    cont = plot.scatter(x,y,c=z, edgecolor="k",
                        cmap="afmhot_r"
                        )
    cbar = plot.colorbar(cont)
    cbar.set_label("RMS", fontsize=14)

    # Etiquetar algunas estaciones
    for _, row in data.iloc[::7].iterrows():

        plot.text(
            float(row["Y"]),
            float(row["X"]),
            fr"$\mathbf{{{row['Site']}}}$",
            # row["SiteName"],
            fontsize=10,
            ha="center",
            va="top",
            color="#15b01A"
        )


        plot.xlabel("East [km]")
        plot.ylabel("North [km]")
        plot.title(f"RMS Map - Iter {last_iter}")


        plot.tight_layout()
        # Coastline
        plot.plot(coast[:,1], coast[:,0], 'r')

        plot.xlim(xmin, xmax)
        plot.ylim(ymin, ymax)


def plot_RMS_vs_Roughness(run_statistics, iters):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #
    # plot the RMS vs Roughness in each iteration 
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    tot = range(iters)
    inicio = tot[0]
    fin = tot[-1]

    roughness = run_statistics["Roughness"]
    iterations = run_statistics["Iter#"]
    globRMS = run_statistics["RMS"]

    # fig ,ax1 = plot.subplots()
    # el área del plot termina al 82 % del ancho de la figura,
    # fig.subplots_adjust(right=0.82)
    fig, ax1 = plot.subplots(constrained_layout=True)



    ax2 = ax1.twinx()
    ax1.plot(iterations,globRMS, '-o', color='#15b01A')  
    ax2.plot(iterations,roughness, 'r-o')  

    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('RMS', color='g')
    ax1.tick_params(axis='y', labelcolor='#15b01A')

    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylabel('Roughness', color='r')

    ax1.grid(axis='x', linestyle='--', alpha=0.5)

    plot.xticks(range(inicio, fin, 1))




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
    

    
    # =======================
    # 2) ARGUMENTO DE STES
    # =========================
    #
    # if not sites_arg.startswith("st"):
    #      print("Formato de sites incorrecto. Usa por ejemplo: st1-4")
    #      sys.exit(1)
    # try:
    #     rango = sites_arg[2:]           # quita "st"
    #     inicio, fin = rango.split("-")  # separa 1 y 4
    #     inicio = int(inicio)
    #     fin = int(fin)
    # except:
    #     print("Formato inválido. Usa: stX-Y  (ejemplo: st1-4)")
    #     sys.exit(1)
    #
    # if inicio > fin:
    #     print("El rango está invertido.")
    #     sys.exit(1)
    #
    # sites = list(range(inicio, fin + 1))

    sites = parse_sites(sites_arg)
    
    
    # =======================
    # 2) ARGUMENTO DE ITER and PROCESSES
    # =========================
    # if iterproc_arg is None:
    #     print("Falta argumento ipX-M")
    #     sys.exit(1)
    # if not iterproc_arg.startswith("ip"):
    #     print("Formato incorrecto en iter-proc. Ejemplo: ip11-4")
    #     sys.exit(1)
    #
    # try:
    #     rango = iterproc_arg[2:]        # quita "ip"
    #     iters, procs = rango.split("-")  # separa X y M
    #     iters = int(iters)
    #     procs = int(procs)
    # except:
    #     print("Formato inválido. Usa: stX-Y  (ejemplo: st1-4)")
    #     sys.exit(1)
    # iters = iters+1
    iters, procs = parse_iterproc(iterproc_arg)
    
    
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
    
    
    
    # =========================
    # 1) CONFIGURACIÓN BÁSICA
    # =========================
    # Componente a evaluar: "Zxy", "Zyx", "Zxx", "Zyy"
    print(f"  \n     📂Leyendo resultados de: {results_path}")
    print(f"     📌Sites seleccionados: {sites}")
    
    
    paths = build_postprocessing_paths(results_path)
    
    # archivos_MT = sorted(glob.glob(PATTERN_MT))
    # archivos_RMS = sorted(glob.glob(PATTERN_RMS))
    # archivos_RHOPHASE = sorted(glob.glob(PATTERN_RHOPH))

    archivos_MT = sorted(glob.glob(paths["mt_pattern"]))
    archivos_RMS = sorted(glob.glob(paths["rms_pattern"]))
    archivos_RHOPHASE = sorted(glob.glob(paths["rhoph_pattern"]))
    
    
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

    # sitesRMS = pd.read_csv(coord_path,sep=r'\s+', header=None)
    sitesRMS = pd.read_csv(paths["coord_path"],sep=r'\s+', header=None)
    sitesRMS = sitesRMS.iloc[:,0:3]
    sitesRMS.columns = ["SiteName","X","Y"]
    #adding an extra column to be able the merge with RMS file data
    sitesRMS["Site"] = np.arange(1,len(sitesRMS)+1)

    coast      = np.loadtxt(paths["coast_path"], skiprows=1)
    domain = np.loadtxt(paths["domain_path"])

    run_statistics = pd.read_csv(paths["stats_path"] , sep=r'\s+',usecols=[0,4,6])

    
    
    #Site,Frequency,
    # ReZxxCal,ImZxxCal,ReZxyCal,ImZxyCal,ReZyxCal,ImZyxCal,ReZyyCal,ImZyyCal
    # ReZxxObs,ImZxxObs,ReZxyObs,ImZxyObs,ReZyxObs,ImZyxObs,ReZyyObs,ImZyyObs
    # ReZxxErr,ImZxxErr,ReZxyErr,ImZxyErr,ReZyxErr,ImZyxErr,ReZyyErr,ImZyyErr
    
    #Site Frequency      AppRxxCal PhsxxCal AppRxyCal PhsxyCal AppRyxCal PhsyxCal AppRyyCal PhsyyCal
    #AppRxxObs  PhsxxObs  AppRxyObs PhsxyObs AppRyxObs PhsyxObs AppRyyObs  PhsyyObs AppRxxErr  PhsxxErr AppRxyErr  PhsxyErr      AppRyxErr       PhsyxErr      AppRyyErr       PhsyyErr
    
    #       Site     #Data            RMS
    
    n_sites = len(sites)
    last_it = iters-1    #       ---> aqui le quitamos el + 1 del range agregado al inicio
    print(f"DEBUG: iters={iters}, last_it={last_it}")  # ← añade esta línea
    
    

    #Definimos la frecuencia
    freq = z_iter[last_it][z_iter[last_it]["Site"] == 1]["Frequency"]
    # freq = rhoph_iter[last_it][rhoph_iter[last_it]["Site"] == 1]["Frequency"]


    # if post_options == "impz":
    #     freq = z_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
    #
    # elif post_options == "rhoph":
    #     freq = rhoph_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
    #
    # else: 
    #     freq = rhoph_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
    #     freq = z_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
    #
        

    plot_mt_response(sites, components, freq, plot_x_axis, rhoph_iter, last_it)

    #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  # #
    #   Segundo plot
    plot_global_RMSvsIter(archivos_MT,rms_iter, iters)
    # plot.show()
    
    
    #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  #  # #
    #   Tercer  plot
    plot_RMS_per_site(rms_iter, last_it)
    

    plot_RMS_heatMap(domain, coast, rms_iter, sitesRMS, last_it)

    plot_RMS_vs_Roughness(run_statistics, iters)
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

