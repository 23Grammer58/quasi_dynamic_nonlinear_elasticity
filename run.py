import os
import sys
import subprocess
import shutil
from pathlib import Path
from bc_vtk_meshio import read_msh_write_vtk, next_quasi_static, add_dir_to_path


def add_dir_to_path(directory_name, filename, post_fix):
    return os.path.join(directory_name, filename + post_fix)

def run_model(config_file, mesh_file, result_filename, output_dir="./res"):
    """
    Запускает внешнюю модель с заданными конфигурационными и сеточными файлами.
    """
    command = [
        "../model",
        "--target", output_dir,
        "--mesh", mesh_file,
        "--name", result_filename,
        "--config", config_file
    ]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        # Для отладки можно раскомментировать следующую строку
        # print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
        sys.exit(1)


def zaglushka(config_file, mesh_file, result_file):
    result_path = add_dir_to_path("res", result_file, "_txt.vtk")
    shutil.copy2(mesh_file, result_path)


def iterative_solve(
    du: float,
    dv: float,
    maxit: int,
    start_vtk_file: str = None,
    msh_file: str = "rake_8",
    experiment_name: str = "test",
    th: float = 0.4
):
    """
    Выполняет итеративное решение с заданными параметрами.
    """

    # path2results = os.path.join("res", experiment_name)
    # if not os.path.exists(path2results):
    #     os.makedirs(path2results)

    path_to_results = Path("res") / experiment_name
    path_to_meshes = path_to_results / "meshes"

    path_to_results.mkdir(parents=True, exist_ok=True)
    path_to_meshes.mkdir(parents=True, exist_ok=True)

    if not start_vtk_file:
        # path2vtk_0 = add_dir_to_path(path2results, experiment_name, ".vtk")
        mesh_path = path_to_meshes / f"{experiment_name}.vtk"

        # считывает сетку .msh добавляет граничные условия и записывает .vtk со всеми необходимыми полями для membrane_solver
        read_msh_write_vtk(
            mesh_filename = msh_file,
            path2vtk = mesh_path,
            print_bnd_data = False,
            du = du, 
            dv = dv,
            th=th
            )
        
        global_it = 0
        print(f"Initial VTK path with boundary conditions: {mesh_path}")
        # maxit = du / n
        # print(vtk_initial_path)

        # path2computed_configuration = add_dir_to_path(path2results, experiment_name, "_0000")
        computed_configuration_path = path_to_results / f"{experiment_name}_0000"
        
        # print("first", first_result_filename)

        run_model(
            config_file=Path("rake_iterative.config"),
            mesh_file=mesh_path, 
            result_filename=computed_configuration_path.name, 
            output_dir=path_to_results
            )
        # zaglushka("rake_iterative.config", vtk_initial_path, first_result_filename)

        it = 0
        # path_to_current_file = add_dir_to_path(directory_name=directory, filename=mesh_filename, post_fix="_txt.vtk")
        
        mesh_path = next_quasi_static(it, Path(f"{computed_configuration_path}_txt.vtk"), du, dv, th)  

        # start_vtk_file = next_quasi_static(experiment_name + "_0000", du, dv, th)  
        print("start", start_vtk_file)
    else:
        basename = mesh_path.name

        try:
            global_it = int(basename.split('_')[-2])
            print("global iteration from filename", global_it)
        except (IndexError, ValueError) as e:
            print(f"Не удалось извлечь номер итерации из файла {mesh_path}: {e}")
            sys.exit(1)
        print(f"Продолжаем итеративное решение с итерации {global_it}")

        # global_it = int(start_vtk_file[-12:-8])
        # print(f"Continue iterative solving from {global_it} iteration")
    
    it = 0

    while it < (maxit):
        it += 1

        computed_configuration_path = path_to_results / f"{experiment_name}_{it:04d}"

        run_model(
            config_file=Path("rake_iterative.config"),
            mesh_file=mesh_path, 
            result_filename=computed_configuration_path.name, 
            output_dir=path_to_results
            )
        
        mesh_path = next_quasi_static(it, Path(f"{computed_configuration_path}_txt.vtk"), du, dv, th)  

        # mesh_filename = start_vtk_file[:-2] + str(it).zfill(2)
        
        # end_vtk_file = add_dir_to_path("", experiment_name + "_", str(global_it + it).zfill(4))
        # print("prev conf:", path2computed_configuration)

        # current_configuration = experiment_name + "_" + str(global_it + it).zfill(4)
        # path2computed_configuration = add_dir_to_path(path2results, experiment_name, "_" + str(it).zfill(4))

        # print("mesh file with bc: ",start_vtk_file)
        # print("current conf:", path2computed_configuration)

        # run_model("rake_iterative.config", start_vtk_file, current_configuration, path2results)
        # zaglushka("rake_iterative.config", start_vtk_file, end_vtk_file)
        # start_vtk_file = next_quasi_static(experiment_name + "_" + str(global_it + it).zfill(4), du, dv, th)  
        # start_vtk_file = next_quasi_static(it, path2computed_configuration, du, dv, th)  
    # next_vtk = next_quasi_static("test_00")
    # reformat_vtk(next_vtk, None)


if __name__ == "__main__":
    # if len(sys.argv) != 3 or sys.argv[1] != "--config":
    #     print("Usage: python script.py --config <config_file>")
    #     sys.exit(1)

    # config_file = sys.argv[2]
    # run_model(config_file)

    # n = 20000 / 5 / 2
    # 2780 + 18 + 0.5 
    # start_configuration = r"/home/proj/membranemodel/build/benchmarks/general/iterative/res/DIC_goretex_complex_94_txt.vtk"
    it = 190
    it_0 = 38
    start_conf = r"/home/proj/membranemodel/build/benchmarks/general/iterative/res/Gore_Offx_" + str(it_0).zfill(4) + "_txt.vtk"

    du = 0.525 / 2 
    n = 50

    # du_0 = du / n * (n - it) 
    # n_0 = 100

    # du_1 = du_0 / n_0 * (n_0 - it_0) 
    # n_1 = 100

    iterative_solve(
        du / n, 
        du / n, 
        n, 
        experiment_name="test",
        th=0.85, 
        # s tart_vtk_file=start_conf
        )
    