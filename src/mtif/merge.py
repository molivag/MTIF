
import sys
import os

def merge_impedance(results_path, iters, procs):
    print("→ Ejecutando mergeResult para impedance tensor option...")
    for ii in range(iters):
        os.system(f"cd {results_path} && mergeResult {ii} {procs} -csv && sleep 0.5")
        print('Continua iteracion: ',ii)
        os.system(f"cd {results_path} && mv result_MT.csv result_impedance_iter{ii}.csv ")
        os.system(f"cd {results_path} && mv RMS.out RMS_iter{ii}.out ")


def merge_rhoph(results_path, iters, procs):
    print("")
    print("→ Ejecutando mergeResult para Rhooa and phase option...")
    # ╰─❯ mergeResult 0 2 -appphs ; sleep 1 ; mv result_MT.csv result_rho_phase_iter0.csv

    for ii in range(iters):

        print("iteracion",ii)
        os.system(f"cd {results_path} && mergeResult {ii} {procs} -appphs && sleep 0.5")
        os.system(f"cd {results_path} && mv result_MT.txt result_rho_phase_iter{ii}.txt ")
        os.system(f"cd {results_path} && mv RMS.out RMS_iter{ii}.out ")
        print(f'esto es la iteracion {ii}')


# def run_merge(results_path, iterproc_arg, mode):
def run_merge(args):#results_path, iterproc_arg, mode):
    
    results_path = f"postprocessing/{args.job}"
    iters = args.iter 
    procs = args.proc


    #Ahora iters y procs representan los argumentos para mergeResulst
    # if mode == "impz":
    merge_impedance(results_path, iters, procs)
    
    # elif mode == "rhoph":
    merge_rhoph(results_path, iters, procs)

    # elif mode == "None":
    # elif mode == "none":
        # print(f"Preprocessing option '{mode}' selected.") 
        # print("Results already merged")
    
    # else:
        # print(f"❌ ❌ ❌ ❌ ❌  Preprocessing option '{mode}' not defined.") 
        # print("Opciones válidas: Z, rhoph or none")
        # sys.exit(1)
    print("\n✅ Successfully merged results.")
