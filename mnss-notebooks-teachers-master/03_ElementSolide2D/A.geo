

lc = DefineNumber[ 0.7, Name "Parameters/lc" ];
Point(1) = {0, 0, 0, lc};
Point(2) = {2, 0, 0, lc};
Point(3) = {8, 0, 0, lc};
Point(4) = {10, 0, 0, lc};
Point(5) = {4, 6, 0, lc};
Point(6) = {6, 6, 0, lc};
Point(7) = {6, 7, 0, lc};
Point(8) = {4, 7, 0, lc};
Point(9) = {5, 10, 0, lc};
Point(10) = {4, 11, 0, lc};
Point(11) = {6, 11, 0, lc};
Line(1) = {1, 2};
Line(2) = {2, 5};
Line(3) = {5, 6};
Line(4) = {6, 3};
Line(5) = {3, 4};
Line(6) = {4, 11};
Line(7) = {11, 10};
Line(8) = {10, 1};
Line(9) = {8, 9};
Line(10) = {9, 7};
Line(11) = {7, 8};
Line Loop(12) = {11, 9, 10};
Line Loop(13) = {8, 1, 2, 3, 4, 5, 6, 7};
Plane Surface(14) = {12, 13};
Physical Surface(15) = {14};

