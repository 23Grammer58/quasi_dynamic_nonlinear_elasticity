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
        energy_file: Path = Path("../potentials/MooneyRivlin.energy"),
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
        "--config", str(config_file),
        "--energy", str(energy_file)
    ]

    # Добавление остальных параметров
    for key, value in kwargs.items():
        if key != "verbose":  # Исключение уже обработанных параметров
            command.extend([f"--{key}", str(value)])

    try:
        if verbose:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
        else:
            result = subprocess.run(command, check=True, text=True, capture_output=False)


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
    energy_file: Path | str,
    start_vtk_file: Path | None = None,
    msh_file: str = "rake_8",
    experiment_name: str | None = "test",
    th: float = 0.4,
    # **kwargs

):
    """
    Выполняет итеративное решение с заданными параметрами.
    
    Args:
        du (float): Смещение за одну итерацию по оси X.
        dv (float): Смещение за одну итерацию по оси Y.
        maxit (int): Максимальное количество итераций.
        start_vtk_file (Path, optional): Путь к функции свободной энергии деформации ("потенциал") в формате .energy. 
        start_vtk_file (Path, optional): Путь к стартовому .vtk файлу. По умолчанию None.
        msh_file (str, optional): Имя файла сетки с геометрией. По умолчанию "rake_8".
        experiment_name (str, optional): Имя эксперимента. По умолчанию "test".
        th (float, optional): Толщина. По умолчанию 0.4.
    """

    if not Path("../model").exists():
        raise FileNotFoundError("Файл 'model' не найден в текущей директории.")
    
    if energy_file.suffix != ".energy":
        raise ValueError("Неверное расширение файла. Ожидалось '.energy', получено '{}'.".format(energy_file.suffix))

    if not experiment_name:
        experiment_name = msh_file + "_" + str(energy_file.stem)

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
            output_dir=path_to_results, 
            energy_file=energy_file
            )

        it = 0
        # Генерация следующего файла сетки с наложенными граничными условиями .vtk файла
        # необходимо добавить _txt.vtk, т.к. в файле с результатами расчетов будет обязательно такой суффикс
        mesh_path = next_quasi_static(it, Path(f"{computed_configuration_path}_txt.vtk"), du, dv, th)  

    else:
        start_vtk_file = Path(start_vtk_file)
        basename = start_vtk_file.name
        print(start_vtk_file)
        # mesh_path = start_vtk_file.parent / "meshes" /  (start_vtk_file.stem[:-4] + ".vtk")
        mesh_path = next_quasi_static(0, start_vtk_file, du, dv, th)  
        # mesh_path.suffix = ".vtk"
        print(f"mesh in {mesh_path}")

        try:
            global_it = int(basename.split('_')[-2])
            # print("Стартуем итеративное решение с итерации", global_it)
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
            output_dir=path_to_results,
            energy_file=energy_file
            )
        
        # Генерация следующего файла сетки с наложенными граничными условиями .vtk файла
        mesh_path = next_quasi_static(it, Path(f"{computed_configuration_path}_txt.vtk"), du, dv, th)  
        print("Итеративное решение завершено.")


if __name__ == "__main__":
  
    it = 190
    it_0 = 24
    # start_conf = r"/home/proj/membranemodel/build/benchmarks/general/iterative/res/exponential_big_mesh/exponential_big_mesh_" + str(it_0).zfill(4) + "_txt.vtk"
    # start_conf = r"/home/proj/membranemodel/build/benchmarks/general/iterative/res/test_20_20/test_20_20_0000_txt.vtk"
    start_conf = r"/home/proj/membranemodel/build/benchmarks/general/iterative/res/cross/stretch_cross_0000_txt.vtk"
    du = 3.0 
    n = 10

    iterative_solve(
        du / n, 
        du / n, 
        n, 
        experiment_name="cross",
        th=0.85,
        msh_file="rake_8",
        energy_file=Path("/home/proj/membranemodel/build/benchmarks/general/potentials/GOH1.energy"),
        start_vtk_file=start_conf
        )
    