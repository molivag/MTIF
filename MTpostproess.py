#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import glob
import sys
import os



coord="../PREprocessing/MeshTranFemtic/input_data/geometry/sites_coord_elev.dat"
df_coord = pd.read_csv (coord,sep=r'\s+')
# =========================
# 0) CONFIGURACIÓN DESDE TERMINAL
# =========================

if len(sys.argv) != 3:
    print("Uso: ./global_check.py <path_to_results> <sitex-y>")
    print("Ejemplo: ./global_check.py test_data_No_Topo/pureOpenMP site1-4")
    sys.exit(1)

results_path = sys.argv[1]


# =========================
# 2) ARGUMENTO DE SITES
# =========================

sites_arg = sys.argv[2]  # ejemplo: "st1-4"

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







# =========================
# 1) CONFIGURACIÓN BÁSICA
# =========================
# Componente a evaluar: "Zxy", "Zyx", "Zxx", "Zyy"
print(f"  \n     📂Leyendo resultados de: {results_path}")
print(f"     📌Sites seleccionados: {sites}")

# Si tus archivos merged se llaman distinto, ajusta esto:
PATTERN_MT = os.path.join(results_path, "result_MT_iter*.csv")  # ejemplo: result_MT_iter05.csv
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
    numero = int(nombre.replace("result_MT_iter","").replace(".csv",""))
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

#Site Frequency      AppRxxCal       PhsxxCal      AppRxyCal       PhsxyCal      AppRyxCal       PhsyxCal      AppRyyCal       PhsyyCal
#AppRxxObs       PhsxxObs      AppRxyObs       PhsxyObs      AppRyxObs       PhsyxObs      AppRyyObs       PhsyyObs      AppRxxErr       PhsxxErr      AppRxyErr       PhsxyErr      AppRyxErr       PhsyxErr      AppRyyErr       PhsyyErr
#       Site     #Data            RMS

n_sites = len(sites)
site=sites[0]
last_it = 5
site = rhoph_iter[0]["Site"]==1

#Definimos la frecuencia
freq = z_iter[last_it][z_iter[last_it]["Site"]==1]["Frequency"]
# freq_exp = freq.apply(lambda x: f"{x:.3e}")
# print(freq_exp)
rho_obs = rhoph_iter[last_it][site]["AppRxyObs"]
phase_obs = rhoph_iter[last_it][site]["PhsxyObs"]

rho_cal = rhoph_iter[last_it][site]["AppRxyCal"]
phase_cal = rhoph_iter[last_it][site]["PhsxyCal"]




# fig, axs = plot.subplots(8, n_sites, figsize=(4*n_sites, 10), sharex='col', 
#                           squeeze=False)


# for j, site in enumerate(sites):
#
#     # # Fila 1 → resistividad
#     # axs[0, j].loglog(freq, rho_obs, 'ok')
#     # axs[0, j].loglog(freq, rho_cal, '--r')
#     # axs[0, j].set_title(f"Site {site}")
#     # axs[0, j].set_ylabel(r"$\rho_{app}$")
#     #
#     # # Fila 2 → fase
#     # axs[1, j].semilogx(freq, phase_obs, 'ok')
#     # axs[1, j].semilogx(freq, phase_cal, '--r')
#     # axs[1, j].set_ylabel(r"$\phi$ (deg)")
#     # axs[1, j].set_xlabel("Frequency (Hz)")
#     # axs[1, j].set_ylim(-60,-20)
#     # axs[0, j].tick_params(labelbottom=False)
#     #
#     # # Fila 1 → resistividad
#     # axs[2, j].loglog(freq, rho_obs, 'ok')
#     # axs[2, j].loglog(freq, rho_cal, '--r')
#     # axs[2, j].set_title(f"Site {site}")
#     # axs[2, j].set_ylabel(r"$\rho_{app}$")
#     #
#     # # Fila 2 → fase
#     # axs[3, j].semilogx(freq, phase_obs, 'ok')
#     # axs[3, j].semilogx(freq, phase_cal, '--r')
#     # axs[3, j].set_ylabel(r"$\phi$ (deg)")
#     # axs[3, j].set_xlabel("Frequency (Hz)")
#     # axs[3, j].set_ylim(-60,-20)
#     # axs[0, j].tick_params(labelbottom=False)
#
#     # ---- XX ----
#     axs[0, j].loglog(freq, rho_obs, 'ok')
#     axs[0, j].loglog(freq, rho_cal, '--r')
#     axs[1, j].semilogx(freq, phase_obs, 'ok')
#     axs[1, j].semilogx(freq, phase_cal, '--r')
#
#     # ---- XY ----
#     axs[2, j].loglog(freq, rho_obs, 'ok')
#     axs[2, j].loglog(freq, rho_cal, '--r')
#     axs[3, j].semilogx(freq, phase_obs, 'ok')
#     axs[3, j].semilogx(freq, phase_cal, '--r')
#
#     # ---- YX ----
#     axs[4, j].loglog(freq, rho_obs, 'ok')
#     axs[4, j].loglog(freq, rho_cal, '--r')
#     axs[5, j].semilogx(freq, phase_obs, 'ok')
#     axs[5, j].semilogx(freq, phase_cal, '--r')
#
#     # ---- YY ----
#     axs[6, j].loglog(freq, rho_obs, 'ok')
#     axs[6, j].loglog(freq, rho_cal, '--r')
#     axs[7, j].semilogx(freq, phase_obs, 'ok')
#     axs[7, j].semilogx(freq, phase_cal, '--r')
#
#     # Quitar eje X en todos menos el último
#     for row in [0,1,2,3,4,5,6]:
#         axs[row, j].tick_params(labelbottom=False)
#
# plot.subplots_adjust(
#     wspace=0.35,   # espacio horizontal
#     hspace=0.05    # espacio vertical
# )
#
#



#
# plot.figure()
# plot.title(rf"$\rho_{{app}}$ Obs vs Calc ")
# plot.loglog(freq,rho_obs,'ok', label="Obs")
# plot.loglog(freq,rho_cal,'--r', label=f"Calc iter {last_it}")
# plot.xlabel("Frequency (Hz)")
# plot.ylabel("Apparent Resistivity (Ohm·m)")
# plot.legend()
plot.show()



#Las figuras Rho and Ph vs freq Obs y Cal en 4 componentes
fig = plot.figure(figsize=(4*n_sites, 12))
fig.suptitle(rf"Respuesta calculada vs observada", fontsize=16, y=0.95)

# Grid exterior: 4 componentes × n_sites
outer = gridspec.GridSpec(
    4, n_sites,
    hspace=0.35,   # espacio entre componentes
    wspace=0.3
)

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

        # ---- Rho ----
        ax_rho.loglog(freq, rho_obs, 'ok', markersize=3)
        ax_rho.loglog(freq, rho_cal, '--r', linewidth=1)
        ax_rho.tick_params(labelbottom=False)

        if j == 0:
            ax_rho.set_ylabel(r"$\rho_{_a}$",fontsize=12)

        if i == 0:
            ax_rho.set_title(f"Site {site}")

        # ---- Phase ----
        ax_phi.semilogx(freq, phase_obs, 'xk', markersize=3)
        ax_phi.semilogx(freq, phase_cal, '--r', linewidth=1)
        # ax_phi.set_ylim(-80, -20)

        if j == 0:
            ax_phi.set_ylabel(r"$\phi$ ($^\circ$)",fontsize=12)

        if i == 3:
            ax_phi.set_xlabel("Frequency (Hz)")

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
           label=rf'Cal Iter {last_it}')
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


