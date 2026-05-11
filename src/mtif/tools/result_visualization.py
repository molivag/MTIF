import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
import matplotlib.gridspec as gridspec
from pyarrow import string
from scipy.interpolate import griddata
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker

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

def plot_visualization(
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
        last_it):

    # - - - - -  Begin of figures - - - - - - #
    #   Primer plot
    plot_mt_response(sites, components, freq, plot_x_axis, rhoph_iter, last_it)
    #   Segundo plot
    plot_global_RMSvsIter(archivos_MT,rms_iter, iters)
    #   Tercer  plot
    plot_RMS_per_site(rms_iter, last_it)
    #   Cuarto  plot
    plot_RMS_heatMap(domain, coast, rms_iter, sitesRMS, last_it)
    #   Quinto  plot
    plot_RMS_vs_Roughness(run_statistics, iters)

    plot.show()
