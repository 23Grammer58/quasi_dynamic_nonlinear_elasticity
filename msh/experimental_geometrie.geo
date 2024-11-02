
// Gmsh script to create points and lines with simplified coordinates (new data)
Point(1) = {9.163394495412845, -0.05354740061162033, 0, 1.0};
Point(2) = {0.9111009174311944, -0.02996941896024463, 0, 1.0};
Point(3) = {0.274495412844038, 0.4180122324159026, 0, 1.0};
Point(4) = {0.06229357798165314, 1.0310397553516824, 0, 1.0};
Point(5) = {0.03871559633027655, 1.9034250764525993, 0, 1.0};
Point(6) = {0.2509174311926623, 2.657920489296636, 0, 1.0};
Point(7) = {0.08587155963302884, 3.2945259938837923, 0, 1.0};
Point(8) = {0.18018348623853342, 5.982415902140673, 0, 1.0};
Point(9) = {-0.055596330275228034, 6.218195718654434, 0, 1.0};
Point(10) = {-0.055596330275228034, 6.571865443425076, 0, 1.0};
Point(11) = {0.13302752293578113, 7.444250764525994, 0, 1.0};
Point(12) = {0.13302752293578113, 9.1182874617737, 0, 1.0};
Point(13) = {0.3688073394495426, 9.73131498470948, 0, 1.0};
Point(14) = {0.7696330275229375, 9.943516819571865, 0, 1.0};
Point(15) = {1.5477064220183498, 10.03782874617737, 0, 1.0};
Point(16) = {8.880458715596331, 10.132140672782874, 0, 1.0};
Point(17) = {9.399174311926606, 9.943516819571865, 0, 1.0};
Point(18) = {9.8, 9.283333333333333, 0, 1.0};
Point(19) = {9.8, 1.1489296636085626, 0, 1.0};
Point(20) = {9.587798165137615, 0.2765443425076457, 0, 1.0};
Point(21) = {9.163394495412845, -0.05354740061162033, 0, 1.0};
Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 5};
Line(5) = {5, 6};
Line(6) = {6, 7};
Line(7) = {7, 8};
Line(8) = {8, 9};
Line(9) = {9, 10};
Line(10) = {10, 11};
Line(11) = {11, 12};
Line(12) = {12, 13};
Line(13) = {13, 14};
Line(14) = {14, 15};
Line(15) = {15, 16};
Line(16) = {16, 17};
Line(17) = {17, 18};
Line(18) = {18, 19};
Line(19) = {19, 20};
Line(20) = {20, 21};
Line(21) = {21, 1};
Line Loop(1) = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21};

// Количество точек на внутренней окружности
num_points = 8;
// Количество точек на внешней окружности
num_points_out = 16;
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
        px = X + 4 * r * Cos(angle);
        py = Y + 4 * r * Sin(angle);
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
Save "rake_experimental.msh";
