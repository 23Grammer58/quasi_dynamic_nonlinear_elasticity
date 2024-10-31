import meshio
import numpy as np
import os
import subprocess
from pathlib import Path
from bc_vtk import write_vtk, read_vtk


def add_dir_to_path(directory_name, filename, post_fix):
    return os.path.join(directory_name, filename + post_fix)


def check(number):
    """
    Проверяет тип граничного условия элемента.
    Args:
        number: число для проверки

    Returns:

    """
    print(number)
    if number & 0x8 != 0:
        print("условие закрепления")
    if number & 0x1 != 0:
        print("x - координата неподвижна")
    if number & 0x2 != 0:
        print("y - координата неподвижна")
    if number & 0x4 != 0:
        print("z - координата неподвижна")


def replace_vtktypeint(file_path, postfix=".vtk"):
    # file_path = add_dir_to_path("./res", mesh_file, postfix)
    with open(file_path, "r") as file:
        lines = file.readlines()

    with open(file_path, "w") as file:
        for line in lines:
            modified_line = line.replace("vtktypeint32", "int")
            # modified_line = line.replace("vtktypeint64", "int")
            file.write(modified_line)


def add_u_bc(ic, bc, point_type):

    v_x = ic
    v_bnd = bc

    v_bnd_14 = v_bnd == point_type
    # v_bnd_13 = v_bnd == 13

    v_x_bc_14_idx = np.unique(np.nonzero(v_bnd_14 * v_x)[0])
    print(v_x_bc_14_idx)
    print(v_x)

    for index in v_x_bc_14_idx:
        v_x[index][1] += dx
    return ic


def next_quasi_static(it, path2current_configuration="solution_HOG_01", du=0.1, dv=0.1, th = 0.4):
    """
        quasi_i:{P_i, v_e_i} -> {P_(i+1), v_(i+1)}, где P_(i+1) = v_e_i, v_(i+1) = P_(i+1) + dx,
        создает новый .vtk.
    """

    # it = float(mesh_filename[-4:])
    # directory = r"res"

    # path_to_current_file = os.path.join(directory, mesh_filename + "_txt.vtk")
    # path_to_current_file = add_dir_to_path(directory_name=directory, filename=mesh_filename, post_fix="_txt.vtk")

    # print(path_to_current_file)

    mesh_old = meshio.read(path2current_configuration)

    print("old mesh", mesh_old)
    mesh = mesh_old.copy()
    # mesh.points = mesh.point_data['v:x_e']
    v_bnd = mesh.point_data['v:bnd']
    v_x = mesh.point_data['v:x_e'].copy()

    # du = 0.1
    # dv = 0.1
    dx = np.array([du, 0, 0])
    dy = np.array([0, dv, 0])

    # keys_bc = {"dy": [131, 132], "dx": [141, 142]}

    # mesh.points = mesh.point_data['v:x_e']

    # mesh.points = v_x
    # v_x = mesh.points

    v_bnd_142 = np.array(v_bnd == 142)
    v_bnd_141 = np.array(v_bnd == 141)

    v_bnd_132 = np.array(v_bnd == 132)
    v_bnd_131 = np.array(v_bnd == 131)

    if len(np.shape(v_bnd_131)) < 2:
        v_bnd_131 = v_bnd_131[:, np.newaxis]
        v_bnd_141 = v_bnd_141[:, np.newaxis]
        v_bnd_132 = v_bnd_132[:, np.newaxis]
        v_bnd_142 = v_bnd_142[:, np.newaxis]

    v_x_bc_142_idx = np.unique(np.nonzero(v_bnd_142 * v_x)[0])
    v_x_bc_141_idx = np.unique(np.nonzero(v_bnd_141 * v_x)[0])
    v_x_bc_132_idx = np.unique(np.nonzero(v_bnd_132 * v_x)[0])
    v_x_bc_131_idx = np.unique(np.nonzero(v_bnd_131 * v_x)[0])

    for index in v_x_bc_142_idx:
        v_x[index] += dy

    for index in v_x_bc_132_idx:
        v_x[index] += dx

    for index in v_x_bc_141_idx:
        v_x[index] -= dy

    for index in v_x_bc_131_idx:
        v_x[index] -= dx
        # print(mesh.points)
    # print(mesh.point_data['v:x'])

    # print("new data")
    # print(mesh.points)
    # print(mesh.point_data['v:x'])

    v_bnd_sim = np.array([int(x // 10) if x in [141, 142, 131, 132] else int(x) for x in v_bnd], dtype=int)[:, np.newaxis]
    mesh.point_data['v:bnd_sim'] = v_bnd_sim
    mesh.point_data['v:x'] = v_x
    
    cells_num = np.shape(mesh_old.cells[-1].data)
    f_fiber = np.ones(cells_num) * [1, 0, 0]
    s_fiber = np.ones(cells_num) * [0, 1, 0]
    thickness = np.ones(cells_num[0]) * th

    cell_data_vtk = {
        "f:fiber_s": [s_fiber],
        "f:fiber_f": [f_fiber],
        "f:thickness": [thickness[:, np.newaxis]],
    }

    # mesh.point_data['v:bc_type'] = v_bnd
    mesh_vtk = meshio.Mesh(
        mesh.points,
        mesh.cells,
        point_data=mesh.point_data,
        cell_data=cell_data_vtk
    )

    it += 1
    # next_mesh_filename = os.path.basename(path2current_configuration)[:-8]
    # path2next_file = os.path.join(os.path.dirname(path2current_configuration), next_mesh_filename + ".vtk")
    # meshio.write(path2next_file, mesh_vtk, binary=False)
    # print(f"Results writed to {path2next_file}")

    # print("curren conf type",type(path2current_configuration))

    current_filename = path2current_configuration.stem  # Без расширения
    it = int(current_filename.split('_')[-2])
    current_filename = current_filename.split('_')[0]
    
    next_mesh_filename = f"{current_filename}_{(it + 1):04d}.vtk"
    path2next_file = path2current_configuration.parent / Path("meshes") / next_mesh_filename
    
    # Запись новой сетки в файл
    meshio.write(path2next_file, mesh_vtk, binary=False)
    print(f"Результаты записаны в {path2next_file}")

    # print(mesh)
    replace_vtktypeint(path2next_file)
    reformat_vtk(path2next_file, path2next_file)

    return path2next_file


def read_msh_write_vtk(mesh_filename: str, path2vtk: str, print_bnd_data: bool = False, du=0.1, dv=0.1, th=0.4) -> str:
    

    # path_to_current_file = add_dir_to_path("./msh", mesh_filename, ".msh")
    # print(os.listdir("./res"))
    mesh = meshio.read(add_dir_to_path("./msh", mesh_filename, ".msh"))

    # print(mesh.point_data)
    vertex_bnd_msh = mesh.cells_dict['vertex'][:, 0]
    bnd_idx_msh = mesh.cell_data_dict['gmsh:physical']['vertex']

    if print_bnd_data:
        print('vertex_bnd from msh')
        print(vertex_bnd_msh)
        print('bnd_idx msh')
        print(bnd_idx_msh)
        print('mesh cells')
        print(mesh.cells_dict['triangle'])

    v_bnd = []
    n1 = 0
    n2 = 0
    end = False
    try:
        while not end:
            if n2 == vertex_bnd_msh[n1]:
                v_bnd.append([bnd_idx_msh[n1]])
                n2 += 1
                n1 += 1
            else:
                v_bnd.append([4])
                n2 += 1
    except IndexError:
        end = True

        others_vertex_bnd_edx = np.ones(len(mesh.points) - len(v_bnd))[:, np.newaxis] * 4
        v_bnd = np.array(v_bnd)

        # print(v_bnd)
        # print(others_vertex_bnd_edx)
        # print(f"shape v_bnd = {np.shape(v_bnd)}, shape other = {np.shape(others_vertex_bnd_edx)}")

        v_bnd = np.concatenate((v_bnd, others_vertex_bnd_edx))

    assert len(v_bnd) == len(mesh.points)
    mesh.point_data['v:bnd'] = v_bnd

    # du = 0.03
    # dv = 0.03
    dx = np.array([du, 0, 0])
    dy = np.array([0, dv, 0])

    keys_bc = {"dy": [131, 132], "dx": [141, 142]}

    v_x = mesh.points.copy()

    v_bnd_142 = np.array(v_bnd == 142)
    v_bnd_141 = np.array(v_bnd == 141)

    v_bnd_132 = np.array(v_bnd == 132)
    v_bnd_131 = np.array(v_bnd == 131)

    # if len(np.shape(v_bnd_13)) < 2:
    #     v_bnd_13 = v_bnd_13[:, np.newaxis]
    #     v_bnd_14 = v_bnd_14[:, np.newaxis]

    v_x_bc_142_idx = np.unique(np.nonzero(v_bnd_142 * v_x)[0])
    v_x_bc_141_idx = np.unique(np.nonzero(v_bnd_141 * v_x)[0])
    v_x_bc_132_idx = np.unique(np.nonzero(v_bnd_132 * v_x)[0])
    v_x_bc_131_idx = np.unique(np.nonzero(v_bnd_131 * v_x)[0])

    for index in v_x_bc_142_idx:
        v_x[index] += dy

    for index in v_x_bc_132_idx:
        v_x[index] += dx

    for index in v_x_bc_141_idx:
        v_x[index] -= dy

    for index in v_x_bc_131_idx:
        v_x[index] -= dx

    mesh.point_data['v:x'] = v_x

    # v_bnd
    v_bnd = v_bnd.flatten()
    v_bnd = np.array([int(x) if x in [141, 142, 131, 132] else int(x) for x in v_bnd], dtype=int)[:, np.newaxis]
    mesh.point_data['v:bnd'] = v_bnd

    cells_vtk = [("triangle", mesh.cells[-1].data)]
    cells_num = np.shape(mesh.cells[-1].data)
    print(cells_num)

    f_fiber = np.ones(cells_num) * [1, 0, 0]
    s_fiber = np.ones(cells_num) * [0, 1, 0]
    thickness = np.ones(cells_num[0]) * th

    cell_data_vtk = {
        "f:fiber_s": [s_fiber],
        "f:fiber_f": [f_fiber],
        "f:thickness": [thickness[:, np.newaxis]],
    }

    # cell_data_vtk = {key: np.array([np.array([elem]) for elem in value]) for key, value in cell_data_vtk.items()}
    # print(cell_data_vtk)
    # print(mesh.point_data)
    mesh_vtk = meshio.Mesh(
        mesh.points,
        cells_vtk,
        point_data=mesh.point_data,
        cell_data=cell_data_vtk
    )



    assert "vertex" not in mesh_vtk.cells_dict.keys()

    # path_to_reformatted_file = add_dir_to_path(path_to_save_mesh, output_mesh_filename, ".vtk")
    meshio.write(path2vtk, mesh_vtk, binary=False)
    reformat_vtk(path2vtk, path2vtk)
    # mesh_check = meshio.read(path_to_reformatted_file)
    # print(np.unique(np.linalg.norm(mesh_check.cell_data["f:fiber_f"])))

    return path2vtk


def inspect_vtk(file_path):
    import vtk
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(file_path)
    reader.Update()

    grid = reader.GetOutput()
    point_data = grid.GetPointData()

    # Check if 'v:bnd' array exists
    v_bnd = point_data.GetArray('v:bnd')

    if v_bnd is None:
        print("'v:bnd' array not found.")
    else:
        print("'v:bnd' array found.")
        print(f"Number of tuples in 'v:bnd': {v_bnd.GetNumberOfTuples()}")

    # List all arrays in the point data
    print("\nAvailable point data arrays:")
    for i in range(point_data.GetNumberOfArrays()):
        array_name = point_data.GetArrayName(i)
        print(f"- {array_name}")


def reformat_vtk(path: str, filename_output: str | None):

    if not filename_output:
        filename_output = path[:-4] + "_proc.vtk"
    replace_vtktypeint(path)

    write_vtk(read_vtk(path), filename_output)
    # return filename_output


def main():
    from run import run_model
    vtk_initial_path = read_msh_write_vtk(
        "square_with_holes_tags",
        "test",
        True)
    
    it = 0
    # start_vtk_path = add_dir_to_path("res", "test" + str(it.2f), ".vtk")
    run_model("rake_iterative.config")
    # reformat_vtk(vtk_initial_path, start_vtk_path)
    # next_vtk_path = add_dir_to_path("..\meshes", "test_01", ".vtk")
    next_vtk = next_quasi_static("test_00")
    # reformat_vtk(next_vtk, None)


if __name__ == "__main__":

    du = 3.5 / 400
    read_msh_write_vtk("rake_16", "rake_test", True, du, du)
    # m = meshio.read(r"res/test_00_txt.vtk")
    # print(m)
    # inspect_vtk("res/rake_test.vtk")
    # main()
    # it = 1
    #  
    # print(next_quasi_static("test_00"))

    # print(f"{it}")
    # rewrite()

    # check(132)
    # check(14)
    # check(13)

    # it = 1
    # filename_prev = "solution_HOG_01"
    # while it < 3:
    #     filename_new = next_quasi_static(filename_prev)
    #     filename_prev = filename_new
    #
    #     it += 1