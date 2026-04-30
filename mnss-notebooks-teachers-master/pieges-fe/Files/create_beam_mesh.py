def create_beam_mesh(L, H, h):
   
    geo = f'''
    L = {L};
    H = {H};
    h = {h};
    
    Point(1) = {{0, 0, 0, h}};
    Point(2) = {{L, 0, 0, h}};
    Point(3) = {{L, H, 0, h}};
    Point(4) = {{0, H, 0, h}};

    Line(1) = {{1, 2}};
    Line(2) = {{2, 3}};
    Line(3) = {{3, 4}};
    Line(4) = {{4, 1}};

    Line Loop(1) = {{1, 2, 3, 4}};
    Plane Surface(1) = {{1}};

    Physical Surface(1) = {{1}};
    Physical Line("left") = {{4}};
    Physical Line("bottom") = {{1}};
    Physical Line("top") = {{3}};
    Physical Line("right") = {{2}};

    '''
    
    with open('beam.geo', 'w') as f:
        f.write(geo)
    
    import subprocess
    ret = subprocess.run("gmsh -2 -order 1 -o beam.msh beam.geo", shell=True)
    if ret.returncode:
        print("Beware, gmsh could not run: mesh is not regenerated")
    else:
        print("Mesh generated")