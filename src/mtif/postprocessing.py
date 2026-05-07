from mtif.config import read_config
from mtif.tools.MTpostprocess import run

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
#
# Comando para lanzar el postprocesado
#
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
def run_post(args):
    print("== Running Postprocessing ==")
    config = read_config()
    post_cfg = config["post"]

    job = args.job if args.job else post_cfg["last_job"]
    sites = args.sites if args.sites else post_cfg["default_sites"]
    iters = args.iter if args.iter else post_cfg["default_iter"]
    # iters = args.iter if args.iter is not None else post_cfg["default_iter"]
    procs = args.proc if args.proc else post_cfg["default_proc"]
    xaxis = args.axis if args.axis else post_cfg["default_axis"]
    comp = args.comp if args.comp else ["xy", "yx"]

    
    if args.mode is not None:
        mode = args.mode                        #Si usuario pasa --mode impz → usa impz
    elif config.get("default_mode") in ["impz", "rhoph"]:
        mode = config.get("default_mode")       #Si no pasa nada y el config tiene impz o rhoph → usa eso
    else:
        mode = "none"                           #Si no hay nada válido → usa "none"

    results_path = f"{post_cfg['post_path']}/{job}"
    st_arg = f"st{sites}"
    ip_arg = f"ip{iters}-{procs}"


    print("   Results folder: ",results_path)
    print("   Job:", job)
    print("   Sites:", sites)
    print("   Mode:", mode)

    # run(results_path,st_arg,ip_arg,xaxis, mode)
    run(results_path, st_arg, ip_arg, xaxis, mode, comp)


