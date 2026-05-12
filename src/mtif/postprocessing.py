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
    xaxis = args.axis if args.axis else post_cfg["default_axis"]
    comp = args.comp if args.comp else ["xy", "yx"]

    
    results_path = f"{post_cfg['post_path']}/{job}"
    st_arg = f"st{sites}"


    print("   Results folder: ",results_path)
    print("   Job:", job)
    print("   Sites:", sites)
    print("   Total Iterations:", iters)

    run(results_path, iters, st_arg, xaxis,  comp)


