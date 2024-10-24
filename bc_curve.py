import meshio
from bc_vtk_meshio import add_dir_to_path
from bc_vtk import write_vtk, read_vtk
import numpy as np


def read_msh_write_vtk(mesh_filename: str, output_mesh_filename: str, print_bnd_data: bool = False, du=0.1,
                       dv=0.1) -> str:
    path_to_current_file = add_dir_to_path("./res", mesh_filename, ".msh")
    # print(os.listdir("./res"))
    mesh = meshio.read(path_to_current_file)

    print(mesh.cells_dict)
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

    f_fiber = np.ones(cells_num) * [1, 0, 0]
    s_fiber = np.ones(cells_num) * [0, 1, 0]
    thickness = np.ones(cells_num[0]) * 0.4

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

    path_to_reformatted_file = add_dir_to_path("./res", output_mesh_filename, ".vtk")
    meshio.write(path_to_reformatted_file, mesh_vtk, binary=False)
    reformat_vtk(path_to_reformatted_file, path_to_reformatted_file)
    return path_to_reformatted_file


def reformat_vtk(path: str, filename_output: str | None):
    if not filename_output:
        filename_output = path[:-4] + "_proc.vtk"

    write_vtk(read_vtk(path), filename_output)
    # return filename_output


def main():

    read_msh_write_vtk("rake_curves", "test", True, 0.01, 0.01)

if __name__ == "__main__":
    main()