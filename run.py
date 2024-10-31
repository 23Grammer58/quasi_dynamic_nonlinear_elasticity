import os
import sys
import subprocess
import shutil
from pathlib import Path
from bc_vtk_meshio import read_msh_write_vtk, next_quasi_static

def run_model(
        config_file: Path, 
        mesh_file: Path, 
        result_filename: str, 
        output_dir: Path = Path("./res"),
        **kwargs
):
    """
    Запускает вызвываемую извне membrane solver с заданными конфигурационными и сеточными файлами.

    Args:
        config_file (Path): Путь к конфигурационному файлу модели.
        mesh_file (Path): Путь к файлу сетки.
        result_filename (str): Имя файла для результатов.
        output_dir (Path, optional): Директория для сохранения результатов. По умолчанию "./res".
    """
    # Обработка дополнительных параметров
    verbose = kwargs.get("verbose", False)
    if verbose:
        print("Запуск модели в режиме отладки.")

    # Формирование команды
    command = [
        "../model",
        "--target", str(output_dir),
        "--mesh", str(mesh_file),
        "--name", result_filename,
        "--config", str(config_file)
    ]

    # Добавление остальных параметров
    for key, value in kwargs.items():
        if key != "verbose":  # Исключение уже обработанных параметров
            command.extend([f"--{key}", str(value)])

    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        if verbose:
            print("Output:", result.stdout)
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
    start_vtk_file: Path | None = None,
    msh_file: str = "rake_8",
    experiment_name: str = "test",
    th: float = 0.4
):
    """
    Выполняет итеративное решение с заданными параметрами.
    
    Args:
        du (float): Смещение за одну итерацию по оси X.
        dv (float): Смещение за одну итерацию по оси Y.
        maxit (int): Максимальное количество итераций.
        start_vtk_file (Path, optional): Путь к стартовому .vtk файлу. По умолчанию None.
        msh_file (str, optional): Имя файла сетки с геометрией. По умолчанию "rake_8".
        experiment_name (str, optional): Имя эксперимента. По умолчанию "test".
        th (float, optional): Толщина. По умолчанию 0.4.
    """

    path_to_results = Path("res") / experiment_name
    path_to_meshes = path_to_results / "meshes"

     # Создание необходимых директорий
    path_to_results.mkdir(parents=True, exist_ok=True)
    path_to_meshes.mkdir(parents=True, exist_ok=True)

    if not start_vtk_file:
        # Создание начального .vtk файла с граничными условиями
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
        print(f"Начальный путь VTK с граничными условиями: {mesh_path}")
        
        computed_configuration_path = path_to_results / f"{experiment_name}_0000"
        
        run_model(
            config_file=Path("rake_iterative.config"),
            mesh_file=mesh_path, 
            result_filename=computed_configuration_path.name, 
            output_dir=path_to_results
            )

        it = 0
        # Генерация следующего файла сетки с наложенными граничными условиями .vtk файла
        mesh_path = next_quasi_static(it, Path(f"{computed_configuration_path}_txt.vtk"), du, dv, th)  

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
        
        # Генерация следующего файла сетки с наложенными граничными условиями .vtk файла
        mesh_path = next_quasi_static(it, Path(f"{computed_configuration_path}_txt.vtk"), du, dv, th)  
        print("Итеративное решение завершено.")


if __name__ == "__main__":
  
    it = 190
    it_0 = 38
    start_conf = r"/home/proj/membranemodel/build/benchmarks/general/iterative/res/Gore_Offx_" + str(it_0).zfill(4) + "_txt.vtk"

    du = 0.525 / 2 
    n = 50

    iterative_solve(
        du / n, 
        du / n, 
        n, 
        experiment_name="test",
        th=0.85, 
        # s tart_vtk_file=start_conf
        )
    