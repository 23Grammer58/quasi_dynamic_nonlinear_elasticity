import vtk

p = 1

def read_vtk(file_path) -> vtk.vtkUnstructuredGrid:
    """
       Читает VTK файл и возвращает его как vtkUnstructuredGrid.

       Args:
           file_path (str): Путь к VTK файлу.

       Returns:
           vtk.vtkUnstructuredGrid: Считанный VTK файл в виде объекта vtkUnstructuredGrid.
       """
    reader = vtk.vtkUnstructuredGridReader()
    reader.SetFileName(file_path)
    reader.Update()
    return reader.GetOutput()


def process_vtk(file_path, dx, dy) -> vtk.vtkUnstructuredGrid:
    """
        Обрабатывает VTK файл, изменяя координаты точек и добавляя дополнительные данные.

        Args:
            file_path (str): Путь к исходному VTK файлу.
            dy (float): Смещение по оси y для максимальных и минимальных y-координат.

        Returns:
            vtk.vtkUnstructuredGrid: Обработанный VTK файл в виде объекта vtkUnstructuredGrid.
        """
    grid = read_vtk(file_path)

    points = grid.GetPoints()
    num_points = points.GetNumberOfPoints()

    max_y = -float('inf')
    min_y = float('inf')
    max_y_points = []
    min_y_points = []


    def find_bc():
        da = 0.9
        db = 1.15
        a = b = 10
        n = 5
        r = 0.2
        circle2cirlce = (a - (db + da) * 2) / (n - 1)

        coords_x_down = [round(da + db + circle2cirlce * i, p) for i in range(n)]
        coords_y_down = n * [round(db - r, p)]
        coords_down = list(zip(coords_x_down, coords_y_down))

        coords_y_up = n * [round(b - db + r, p)]
        coords_up = list(zip(coords_x_down, coords_y_up))

        coords_x_left = n * [round(db - r, p)]
        coords_y_left = [round(da + db + circle2cirlce * i) for i in range(n)]
        coords_left = list(zip(coords_x_left, coords_y_left))

        coords_x_right = n * [round(a - db + r, p)]
        coords_right = list(zip(coords_x_right, coords_y_left))


        # print(coords)
        return coords_down, coords_up, coords_left, coords_right


    bc_coords_down, bc_coords_up, bc_coords_left, bc_coords_right = find_bc()
    #эту процедуру можно и нужно адаптировать для точек сетки rake.vtk
    # for i in range(num_points):
    #     x, y, z = points.GetPoint(i)
    #     if y > max_y:
    #         max_y = y
    #         max_y_points = [i]
    #     elif y == max_y:
    #         max_y_points.append(i)
    #     if y < min_y:
    #         min_y = y
    #         min_y_points = [i]
    #     elif y == min_y:
    #         min_y_points.append(i)

    down_points = []
    up_points = []
    left_points = []
    right_points = []
    for i in range(num_points):
        x, y, z = points.GetPoint(i)
        x_r = round(x, p)
        y_r = round(y, p)
        if (x_r, y_r) in bc_coords_down:
            down_points.append(i)
        elif (x_r, y_r) in bc_coords_up:
            up_points.append(i)
        elif (x_r, y_r) in bc_coords_left:
            left_points.append(i)
        elif (x_r, y_r) in bc_coords_right:
            right_points.append(i)

    new_points = vtk.vtkPoints()
    boundary_tags = vtk.vtkIntArray()
    boundary_tags.SetName("v:bnd")

    updated_coords = vtk.vtkDoubleArray()
    updated_coords.SetName("v:x")
    updated_coords.SetNumberOfComponents(3)
    updated_coords.SetNumberOfTuples(num_points)

    # for i in range(num_points):
    #     x, y, z = points.GetPoint(i)
    #     new_points.InsertNextPoint(x, y, 0.0)  # Zeroing the z-coordinate
    #     if i in max_y_points:
    #         updated_coords.SetTuple3(i, x, y + dy, 0.0)  # Zeroing the z-coordinate
    #         boundary_tags.InsertNextValue(15)
    #     elif i in min_y_points:
    #         updated_coords.SetTuple3(i, x, y - dy, 0.0)  # Zeroing the z-coordinate
    #         boundary_tags.InsertNextValue(15)
    #     else:
    #         updated_coords.SetTuple3(i, x, y, 0.0)  # Zeroing the z-coordinate
    #         boundary_tags.InsertNextValue(4)

    for i in range(num_points):
        x, y, z = points.GetPoint(i)
        new_points.InsertNextPoint(x, y, 0.0)  # Zeroing the z-coordinate
        if i in up_points:
            updated_coords.SetTuple3(i, x, y + dy, 0.0)  # Zeroing the z-coordinate
            boundary_tags.InsertNextValue(15)
        elif i in down_points:
            updated_coords.SetTuple3(i, x, y - dy, 0.0)  # Zeroing the z-coordinate
            boundary_tags.InsertNextValue(15)
        elif i in right_points:
            updated_coords.SetTuple3(i, x + dx, y, 0.0)  # Zeroing the z-coordinate
            boundary_tags.InsertNextValue(15)
        elif i in left_points:
            updated_coords.SetTuple3(i, x - dx, y, 0.0)  # Zeroing the z-coordinate
            boundary_tags.InsertNextValue(15)
        else:
            updated_coords.SetTuple3(i, x, y, 0.0)  # Zeroing the z-coordinate
            boundary_tags.InsertNextValue(4)


    grid.SetPoints(new_points)
    grid.GetPointData().AddArray(boundary_tags)
    grid.GetPointData().AddArray(updated_coords)

    # Filter out non-triangle cells
    triangle_cells = vtk.vtkCellArray()
    cell_types = vtk.vtkUnsignedCharArray()
    cell_types.SetNumberOfComponents(1)

    for i in range(grid.GetNumberOfCells()):
        cell = grid.GetCell(i)
        if cell.GetCellType() == vtk.VTK_TRIANGLE:
            triangle_cells.InsertNextCell(cell)
            cell_types.InsertNextValue(vtk.VTK_TRIANGLE)

    grid.SetCells(cell_types, triangle_cells)

    # Create a new cell data array for f:thickness
    thickness_data = vtk.vtkFloatArray()
    thickness_data.SetName("f:thickness")
    thickness_data.SetNumberOfComponents(1)
    thickness_data.SetNumberOfTuples(grid.GetNumberOfCells())

    for i in range(grid.GetNumberOfCells()):
        thickness_data.SetValue(i, 1.0)

    grid.GetCellData().AddArray(thickness_data)

    return grid


def write_vtk(grid: vtk.vtkUnstructuredGrid, output_path: str):

    """
       Записывает объект vtkUnstructuredGrid в VTK файл, удовлетворяющий требованиям из img/grid_vtk_pattern.vtk.
       Также записываются дополнительные поля (ГУ, тип ГУ, толщина, стартовая конфигурация).

       Args:
           grid (vtk.vtkUnstructuredGrid): Обработанный VTK файл в виде объекта vtkUnstructuredGrid.
           output_path (str): Путь для сохранения выходного VTK файла.
    """
    num_points = grid.GetNumberOfPoints()
    num_cells = grid.GetNumberOfCells()

    with open(output_path, 'w') as file:
        file.write('# vtk DataFile Version 3.0\n')
        file.write('File written by membrane-model\n')
        file.write('ASCII\n')
        file.write('DATASET UNSTRUCTURED_GRID\n')

        points = grid.GetPoints()
        file.write(f'POINTS {num_points} float\n')
        for i in range(num_points):
            x, y, z = points.GetPoint(i)
            file.write(f'{x} {y} 0.0\n')  # Zeroing the z-coordinate

        cells = grid.GetCells()
        cell_array = cells.GetData()
        file.write(f'CELLS {num_cells} {cell_array.GetNumberOfTuples()}\n')
        cell_id_list = vtk.vtkIdList()
        for i in range(num_cells):
            grid.GetCellPoints(i, cell_id_list)
            num_cell_points = cell_id_list.GetNumberOfIds()
            file.write(f'{num_cell_points}')
            for j in range(num_cell_points):
                file.write(f' {cell_id_list.GetId(j)}')
            file.write('\n')

        cell_types = grid.GetCellTypesArray()
        file.write(f'CELL_TYPES {num_cells}\n')
        for i in range(num_cells):
            file.write(f'{cell_types.GetValue(i)}\n')

        point_data = grid.GetPointData()
        file.write(f'POINT_DATA {num_points}\n')

        v_bnd = point_data.GetArray('v:bnd')

        if v_bnd is None:
            print("Warning: 'v:bnd' array not found.")
            return

        file.write('SCALARS v:bnd int 1\n')
        file.write('LOOKUP_TABLE default\n')
        for i in range(num_points):
            file.write(f'{v_bnd.GetValue(i)}\n')

        if point_data.GetArray('v:bnd_sim') is not None:
            v_bnd = point_data.GetArray('v:bnd_sim')
            file.write('SCALARS v:bnd_sim int 1\n')
            file.write('LOOKUP_TABLE default\n')
            for i in range(num_points):
                file.write(f'{v_bnd.GetValue(i)}\n')
        else:
            v_bnd = point_data.GetArray('v:bnd')
            file.write('SCALARS v:bnd_sim int 1\n')
            file.write('LOOKUP_TABLE default\n')
            for i in range(num_points):
                file.write(f'{int(v_bnd.GetValue(i) // 10) if v_bnd.GetValue(i) in [131, 132, 141, 142] else int(v_bnd.GetValue(i))}\n')


        v_x = point_data.GetArray('v:x')
        file.write('SCALARS v:x double 3\n')
        file.write('LOOKUP_TABLE default\n')
        for i in range(num_points):
            file.write(f'{v_x.GetComponent(i, 0)} {v_x.GetComponent(i, 1)} 0.0\n')  # Zeroing the z-coordinate

        if point_data.GetArray('v:x_e') is not None:
            v_xe = point_data.GetArray('v:x_e')
            file.write('SCALARS v:x_e double 3\n')
            file.write('LOOKUP_TABLE default\n')
            for i in range(num_points):
                file.write(f'{v_xe.GetComponent(i, 0)} {v_xe.GetComponent(i, 1)} 0.0\n')  # Zeroing the z-coordinate

        cell_data = grid.GetCellData()
        file.write(f'CELL_DATA {num_cells}\n')

        f_thickness = cell_data.GetArray('f:thickness')
        file.write('SCALARS f:thickness float 1\n')
        file.write('LOOKUP_TABLE default\n')
        for i in range(num_cells):
            file.write(f'{f_thickness.GetValue(i)}\n')

        f_fiber_s = cell_data.GetArray('f:fiber_s')
        if f_fiber_s:
            file.write('SCALARS f:fiber_s double 3\n')
            file.write('LOOKUP_TABLE default\n')
            for i in range(num_cells):
                # file.write(f'{f_fiber_s.GetValue(i)} 0.0 0.0 \n')
                file.write(f'1.0 0.0 0.0 \n')

        f_fiber_f = cell_data.GetArray('f:fiber_f')
        if f_fiber_f:
            file.write('SCALARS f:fiber_f double 3\n')
            file.write('LOOKUP_TABLE default\n')
            for i in range(num_cells):
                file.write(f'0.0 1.0 0.0\n')



if __name__ == "__main__":
    input_vtk_file = r'..\meshes\rake.vtk'
    output_vtk_file = r'..\meshes\rake_proc.vtk'

    dx = 7.0
    dy = 7.0

    grid = process_vtk(input_vtk_file, dx, dy)
    write_vtk(grid, output_vtk_file)

