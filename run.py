import subprocess
import sys
from bc_vtk_meshio import read_msh_write_vtk, next_quasi_static, add_dir_to_path
import shutil

def run_model(config_file, mesh_file, result_file):
    command = f"../model --mesh {mesh_file} --name {result_file} --config {config_file}"
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=False)
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        # print("Output:", result.stdout)
        print("Error:", e.stderr)
        sys.exit(1)


def zaglushka(config_file, mesh_file, result_file):
    result_path = add_dir_to_path("res", result_file, "_txt.vtk")
    shutil.copy2(mesh_file, result_path)


def iterative_solve(
        du, 
        dv, 
        maxit, 
        start_vtk_file: str = None, 
        msh_file: str = "rake_8", 
        experiment_name: str = "test",
        th = 0.4
        ):

    if not start_vtk_file:
        vtk_initial_path = read_msh_write_vtk(
            mesh_filename = msh_file,
            output_mesh_filename = experiment_name,
            print_bnd_data = False,
            du = du, 
            dv = dv,
            th=th
            )
        
        # print(vtk_initial_path)

        it = 0
        first_result_file = add_dir_to_path("", experiment_name, "_00")
        # print("first", first_result_file)

        run_model("rake_iterative.config", vtk_initial_path, first_result_file)
        # zaglushka("rake_iterative.config", vtk_initial_path, first_result_file)

        start_vtk_file = next_quasi_static(experiment_name + "_00", du, dv, th)  
        print("start", start_vtk_file)
    else:
        it = int(start_vtk_file[-10:-8])
        print(it)
    while it < maxit:
        it += 1
        # mesh_filename = start_vtk_file[:-2] + str(it).zfill(2)
        
        end_vtk_file = add_dir_to_path("", experiment_name + "_", str(it).zfill(2))

        print(start_vtk_file)
        print(end_vtk_file)
        run_model("rake_iterative.config", start_vtk_file, end_vtk_file)
        # zaglushka("rake_iterative.config", start_vtk_file, end_vtk_file)
        start_vtk_file = next_quasi_static(experiment_name + "_" + str(it).zfill(2), du, dv, th)  
    # next_vtk = next_quasi_static("test_00")
    # reformat_vtk(next_vtk, None)


if __name__ == "__main__":
    # if len(sys.argv) != 3 or sys.argv[1] != "--config":
    #     print("Usage: python script.py --config <config_file>")
    #     sys.exit(1)

    # config_file = sys.argv[2]
    # run_model(config_file)

    du = 0.0525  
    n = 123
    # start_configuration = r"/home/proj/membranemodel/build/benchmarks/general/iterative/res/test_119_txt.vtk"
    iterative_solve(du / n, du / n, n, experiment_name="t", th=0.05)
    