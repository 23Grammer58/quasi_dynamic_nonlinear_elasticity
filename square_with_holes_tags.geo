ls = 0.1;
//количество отверстий вдоль оси Ox
n = 5;
//количество отверстий вдоль оси Oy
m = 5;
// радиус окружностей
r = 0.2;
//размер патча вдоль оси Ox
a = 10;
//размер патча вдоль оси Oy
b = 10;
//толщина образца
th = 0.1;

Point(1) = {0, 0, 0, ls};
Point(2) = {a, 0, 0, ls};
Point(3) = {a, b, 0, ls};
Point(4) = {0, b, 0, ls};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};

Line Loop(1) = {1, 2, 3, 4};

X = 0;
Y = 0;

loops[] = {};
points[] = {};
curves[] = {};

curves_down_bc[] = {};
curves_bc[] = {};
curves_bc[] = {};
curves_bc[] = {};

points_down[] = {};
points_up[] = {};
points_left[] = {};
points_right[] = {};

//Physical Curve(131) = {};

Function CircleLoop_new
    pp = newp;
    Point(pp) = {X, Y, 0, ls};
    points[] = {};

    num_points = 72;  // Количество точек на окружности
    delta_angle = 2 * Pi / num_points;  // Угол между соседними точками

    // Создание точек на окружности
    For i In {0:num_points-1}
        angle = i * delta_angle;
        px = X + r * Cos(angle);
        py = Y + r * Sin(angle);
        points[] += newp;
        Point(pp + i) = {px, py, 0, ls};
    EndFor

    lp = newl;

    // Создание дуг для окружности
    For i In {1:num_points}
        next_i = i % num_points + 1; // Обеспечение замыкания окружности
        Circle(lp + i - 1) = {points[i], pp, points[next_i]};
    EndFor

    //Physical Curve(131) += {lp:lp+num_points-1};

    llp = newll;
    Line Loop(llp) = {lp:lp+num_points-1};
    loops[] += llp;
Return


Function CircleLoop
    pp = newp;
    Point(pp) = {X, Y, 0, ls};
    Point(pp+1) = {X+r, Y, 0, ls};
    Point(pp+2) = {X, Y+r, 0, ls};
    Point(pp+3) = {X-r, Y, 0, ls};
    Point(pp+4) = {X, Y-r, 0, ls};
    points[] = {};

    //points[] += pp;


    //points[] += pp + 2;
    //points[] += pp + 3;
    //points[] += pp + 4;
    //pp = new
    //Physical Point(pp) = {pp + 1};

    lp = newl;
    Circle(lp) = {pp+1, pp, pp + 2};
    Circle(lp+1) = {pp+2, pp, pp + 3};
    Circle(lp+2) = {pp+3, pp, pp + 4};
    Circle(lp+3) = {pp+4, pp, pp + 1};

    //Physical Curve(131) += {lp, lp+1, lp+2, lp+3};
    //right 132
    If (position == 4)
        //points[] += pp + 1;
        points[] += lp + 1;
        points[] += lp + 2;
        points[] += lp + 4;
        //curves[] += lp + 1;
    EndIf

    //up 142
    If (position == 2)
        //points[] += pp + 2;
        points[] += lp + 1;
        points[] += lp + 2;
        points[] += lp + 3;
    EndIf

    //left 131
    If (position == 3)
        //points[] += pp + 3;
        points[] += lp + 3;
        points[] += lp + 2;
        points[] += lp + 4;
    EndIf

    //down 141
    If (position == 1)
        //points[] += pp + 4;
        points[] += lp + 1;
        points[] += lp + 4;
        points[] += lp + 3;
    EndIf

    llp = newll;
    Line Loop(llp) = {lp, lp+1, lp+2, lp+3};
    loops[] += llp;

    //Physical Curve(lp) = {pp, pp +3};

Return

dist_to_border = 1.15;
//da = 2 * sqrt(2) * r + 0.4;
da = 0.9;
If (da < 2 * Sqrt(2) * r)
    da = 2 * Sqrt(2) * r + 0.00001;
EndIf
circle2cirlce = (a - (dist_to_border + da) * 2) / (n - 1);

//circle2cirlce = 1.6;
//circle_coords[] = {1.7, 3.4, 5.1, 6.8, 8.5};
//circle_coords[] = {1.7, 2.6, 3.5, 4.4, 5.3};

For i In {0:4}

    position = 1;
    X = dist_to_border + da + circle2cirlce * i;
    Y = dist_to_border;
    Call CircleLoop;
    points_up[] += points[];

    position = 2;
    X = dist_to_border + da + circle2cirlce * i;
    Y = b - dist_to_border;
    Call CircleLoop;
    points_down[] += points[];

    position = 3;
    X = dist_to_border;
    Y = da + dist_to_border + circle2cirlce * i;
    Call CircleLoop;
    points_left[] += points[];

    position = 4;
    X = a - dist_to_border;
    Y = da + dist_to_border + circle2cirlce * i;
    Call CircleLoop;
    points_right[] += points[];

EndFor

Physical Point(141) = {points_down[]};
Physical Point(142) = {points_up[]};
Physical Point(131) = {points_left[]};
Physical Point(132) = {points_right[]};

//Physical Curve(141) = {points_down[]};
//Physical Curve(142) = {points_up[]};w
//Physical Curve(131) = {points_left[]};
//Physical Curve(132) = {points_right[]};

//Physical Point(131) = {curves_bc[]};

Plane Surface(1) = {1, loops[]};
Physical Surface(2) = {1};
//Extrude{0,0,1}{Surface{1};}

//MeshSize{PointsOf{Volume{:};}} = 0.1;

//Mesh.CharacteristicLengthMin = 0.8;
//Mesh.CharacteristicLengthMax = 0.4;
Mesh 2;
//+
//Transfinite Surface {1};
//+
//Recombine Surface {1};
//Mesh.Format = 16;
//Save "rake_curves.msh";