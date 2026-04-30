import akantu as aka

def solve(Force, mesh_file):   

    material_file = 'material.dat'
    aka.parseInput(material_file)

    spatial_dimension = 2    
   
    mesh = aka.Mesh(spatial_dimension)
    mesh.read(mesh_file)

    model = aka.SolidMechanicsModel(mesh)
    
    # initialize a static solver

    model.initFull(_analysis_method=aka._static)

    # set the displacement/Dirichlet boundary conditions
    model.applyBC(aka.FixedValue(0.0, aka._x), "XBlocked")
    model.applyBC(aka.FixedValue(0.0, aka._y), "YBlocked")


    # set the force/Neumann boundary conditions
    model.getExternalForce()[:] = 0

  
    model.applyBC(aka.FromTraction(Force), "Traction")
    # configure the linear algebra solver
    solver = model.getNonLinearSolver()
    solver.set("max_iterations", 2)
    solver.set("threshold", 1e-10)
    solver.set("convergence_type", aka.SolveConvergenceCriteria.residual)

    # compute the solution
    model.solveStep()
    
    model.setBaseName("beam")
    model.addDumpFieldVector("displacement")
    model.addDumpFieldVector("external_force")
    model.addDumpField("strain")
    model.addDumpField("stress")
    model.addDumpField("blocked_dofs")
    model.dump()
    
    return model,mesh