
    lc = 20;
    r = 50.0;
    xc = 0.0;
    yc = 0.0;
    
    Point(1) = {xc + r, yc, 0, lc};
    Point(2) = {xc, yc + r, 0, lc};
    Point(3) = {xc - r, yc, 0, lc};
    Point(4) = {xc, yc - r, 0, lc};
    Point(5) = {xc, yc, 0, lc};
    
    Circle(1) = {1, 5, 2};
    Circle(2) = {2, 5, 3};
    Circle(3) = {3, 5, 4};
    Circle(4) = {4, 5, 1};
    
    Line Loop(5) = {1, 2, 3, 4};
    Plane Surface(6) = {5};
    Physical Surface(7) = {6};
    Physical Line(8) = {2}; // demi-cercle supérieur
    Physical Line(9) = {4}; // demi-cercle inférieur
    