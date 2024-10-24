// Количество точек на внутренней окружности
num_points = 8;
// Количество точек на внешней окружности
num_points_out = 4;
//If (num_points / 4 < 4)
//    num_points_out = 4;
//ElseIf
//    num_points_out = num_points / 4;
//EndIf
//шаг сетки
ls = 0.5;
// количество отверстий вдоль оси Ox
n = 5;
// количество отверстий вдоль оси Oy
m = 5;
// радиус окружностей
r = 0.2;
// размер патча вдоль оси Ox
a = 10;
// размер патча вдоль оси Oy
b = 10;

Point(1) = {0, 0, 0, ls};
Point(2) = {a, 0, 0, ls};
Point(3) = {a, b, 0, ls};
Point(4) = {0, b, 0, ls};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

Line Loop(1) = {1, 2, 3, 4};

loops[] = {};
out_loops[] = {};
out_points[] = {};

// Вызов функции создания окружностей и добавление их в loops[]
X = 0;
Y = 0;

Function CircleLoop_old
    pp = newp;

    Point(pp) = {X, Y, 0, ls};

    points[] = {};
    bc_points[] = {};

    delta_angle = 2 * Pi / num_points;  // Угол между соседними точками

    // Создание точек на окружности
    For j In {1:num_points}
        angle = (j - 1) * delta_angle;
        px = X + r * Cos(angle);
        py = Y + r * Sin(angle);
        points[j] = newp;
        Point(points[j]) = {px, py, 0, ls};
    EndFor

    delta_angle_out = 2 * Pi / num_points_out;  // Угол между соседними точками
    For j In {1:num_points}
        angle = (j - 1) * delta_angle;
        px = X + r * Cos(angle);
        py = Y + r * Sin(angle);
        points[j] = newp;
        Point(points[j]) = {px, py, 0, ls};
    EndFor


    out_circlce_points[] = {};
    For j In {1:num_points / 2}
        angle = (j - 1) * 2  * delta_angle;
        px = X + 2 * r * Cos(angle);
        py = Y + 2 * r * Sin(angle);
        out_circle_points[j] = newp;
        Point(out_circle_points[j]) = {px, py, 0, ls};
    EndFor

    lp = newl;

    // Создание дуг для окружности
    For j In {1:num_points}
        next_i = j % num_points + 1; // Обеспечение замыкания окружности
        Circle(lp + j - 1) = {points[j], pp, points[next_i]};
    EndFor


    llp = newll;
    Line Loop(llp) = {lp:lp+num_points-1};
    loops[] += llp;

    lp = newl;

    For j In {1:num_points / 2}
        next_i = j % (num_points / 2)+ 1; // Обеспечение замыкания окружности
        Circle(lp + j - 1) = {out_circle_points[j], pp, out_circle_points[next_i]};
    EndFor

    llp = newll;
    Line Loop(llp) = {lp:lp+num_points-1};
    out_loops[] += llp;
Return

Function CircleLoop
    pp = newp;
    Point(pp) = {X, Y, 0, ls};
    points[] = {};
    bc_points[] = {};  // Массив для хранения точек на половине окружности

    delta_angle = 2 * Pi / num_points;  // Угол между соседними точками

    // Создание точек на окружности
    For j In {1:num_points}
        angle = (j - 1) * delta_angle;
        px = X + r * Cos(angle);
        py = Y + r * Sin(angle);
        points[j] = newp;
        Point(points[j]) = {px, py, 0, ls};
    EndFor

    delta_angle_out = 2 * Pi / num_points_out;  // Угол между соседними точками
    out_circlce_points[] = {};
    For j In {1:num_points_out}
        angle = (j - 1) * delta_angle_out;
        px = X + 2 * r * Cos(angle);
        py = Y + 2 * r * Sin(angle);
        out_circle_points[j] = newp;
        Point(out_circle_points[j]) = {px, py, 0, ls};
    EndFor


    // Определение направления
    // Влево (граница x = 0)
    If (X == dist_to_border)
        For j In {1:num_points}
            angle = (j - 1) * delta_angle;
            If (Cos(angle) < 0)  // Выбор точек, которые находятся слева
                bc_points[] += points[j];
            EndIf
        EndFor
    // Вправо (граница x = a)
    ElseIf (X == a - dist_to_border)
        For j In {1:num_points}
            angle = (j - 1) * delta_angle;
            If (Cos(angle) > 0)  // Выбор точек, которые находятся справа
                bc_points[] += points[j];
            EndIf
        EndFor
    // Вверх (граница y = b)
    ElseIf (Y == b - dist_to_border)
        For j In {1:num_points}
            angle = (j - 1) * delta_angle;
            If (Sin(angle) > 0)  // Выбор точек, которые находятся сверху
                bc_points[] += points[j];
            EndIf
        EndFor
    // Вниз (граница y = 0)
    ElseIf (Y == dist_to_border)
        For j In {1:num_points}
            angle = (j - 1) * delta_angle;
            If (Sin(angle) < 0)  // Выбор точек, которые находятся снизу
                bc_points[] += points[j];
            EndIf
        EndFor
    EndIf

    lp = newl;

    // Создание дуг для окружности
    For j In {1:num_points}
        next_i = j % num_points + 1; // Обеспечение замыкания окружности
        Circle(lp + j - 1) = {points[j], pp, points[next_i]};
    EndFor

    llp = newll;
    Line Loop(llp) = {lp:lp+num_points-1};
    loops[] += llp;

    lp = newl;

    For j In {1:num_points_out}
        next_i = j % (num_points_out)+ 1; // Обеспечение замыкания окружности
        Circle(lp + j - 1) = {out_circle_points[j], pp, out_circle_points[next_i]};
    EndFor

    llp = newll;
    Line Loop(llp) = {lp:lp+num_points-1};
    out_loops[] += llp;
Return


dist_to_border = 1.15;
da = 0.9;
If (da < 2 * Sqrt(2) * r)
    da = 2 * Sqrt(2) * r + 0.00001;
EndIf

circle2cirlce = (a - 2 * (dist_to_border + da)) / (n - 1);

For i In {0:(n-1)}
    position = 1;
    X = dist_to_border + da + circle2cirlce * i;
    Y = dist_to_border;
    Call CircleLoop;
    points_down[] += bc_points[];
    out_points[] += out_circle_points[];

    position = 2;
    X = dist_to_border + da + circle2cirlce * i;
    Y = b - dist_to_border;
    Call CircleLoop;
    points_up[] += bc_points[];
    out_points[] += out_circle_points[];

    position = 3;
    X = dist_to_border;
    Y = dist_to_border + da + circle2cirlce * i;
    Call CircleLoop;
    points_left[] += bc_points[];
    out_points[] += out_circle_points[];

    position = 4;
    X = a - dist_to_border;
    Y = dist_to_border + da + circle2cirlce * i;
    Call CircleLoop;
    points_right[] += bc_points[];
    out_points[] += out_circle_points[];
EndFor


Physical Point(141) = {points_down[]};
Physical Point(142) = {points_up[]};
Physical Point(131) = {points_left[]};
Physical Point(132) = {points_right[]};

Plane Surface(1) = {1, loops[]};
Physical Surface(2) = {1};

// Увеличиваем размер элементов сетки за пределами окружностей
//Mesh.CharacteristicLengthMin = 0.9;
//Mesh.CharacteristicLengthMax = 0.6;

Point{out_points[]} In Surface {1};

Mesh 2;
Save "rake.msh";
