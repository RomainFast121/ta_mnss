import akantu as aka
import matplotlib.tri as tri
import matplotlib.pyplot as plt
import numpy as np
    
def solid_mechanics(timestep, F, max_steps, dump_every, show_plot):
    
    # creating the model

    spatial_dimension = 2
    time_factor = 0.8
 
    aka.parseInput('../Files/material.dat')
    mesh = aka.Mesh(spatial_dimension)
    mesh.read('beam.msh')


    # model Initialization
    model = aka.SolidMechanicsModel(mesh)
    model.initFull(_analysis_method = aka._explicit_lumped_mass)
    timestep_stable = model.getStableTimeStep()
    timestep_stable *= time_factor;
    model.setTimeStep(timestep);

    mesh = model.getMesh()
    print("The timestep is : " + str(timestep))
    print("The stable timestep is : " + str(timestep_stable))
    
    # show mesh
    
    mesh = model.getMesh()
    conn = mesh.getConnectivity(aka._triangle_3)
    nodes = mesh.getNodes()
    triangles = tri.Triangulation(nodes[:, 0], nodes[:, 1], conn)

    plt.axes().set_aspect('equal')
    t = plt.triplot(triangles, '--', lw=.8)
    
    plt.show()
    displacement = model.getDisplacement()
    nodes = mesh.getNodes()

    # set the displacement/Dirichlet boundary conditions
    model.applyBC(aka.FixedValue(0.0, aka._x), "left")
    model.applyBC(aka.FixedValue(0.0, aka._y), "left")

    # Neumann Traction

    traction = np.zeros(spatial_dimension)
    traction[int(aka._y)] = -F
    model.getExternalForce()[:] = 0
    model.applyBC(aka.FromSameDim(traction), 'right')

    model.setBaseName("explicit_dynamic");
    model.addDumpField("displacement");
    model.addDumpField("velocity");
    model.addDumpField("acceleration");
    model.addDumpField("stress");
    model.dump()

    Energy_kinetic = []
    Energy_potential = []
    Energy_total = []
    time = []

    for t in range(max_steps):
     
        if t == 0:
            traction = np.zeros(spatial_dimension)
            traction[int(aka._y)] = -F
            model.getExternalForce()[:] = 0
            model.applyBC(aka.FromSameDim(traction), 'right')

        if t != 0 :
            traction = np.zeros(spatial_dimension)
            traction[int(aka._y)] = 0
            model.getExternalForce()[:] = 0
            model.applyBC(aka.FromSameDim(traction), 'right')
        
        displacement = model.getDisplacement()
  
        # Solve model
        model.solveStep();
    
        # Plot energy
        time.append(t*timestep)
        epot = model.getEnergy("potential");
        Energy_potential.append(epot)
        ekin = model.getEnergy("kinetic");
        Energy_kinetic.append(ekin)
        Energy_total.append(ekin + epot)
        #print("passing step " + str(t) + " " + str(max_steps))
        model.dump()

        # plot displacement field
        if show_plot == "show_plot_yes":
            if t%dump_every == 0: 
                plt.axes().set_aspect('equal')
                u_disp = plt.tricontourf(triangles, np.linalg.norm(displacement, axis=1))
                t = plt.triplot(triangles, '--', lw=.8)
                #plt.clim(vmin=0, vmax=7e-09)
                cbar = plt.colorbar(u_disp)
                cbar.set_label('displacement magnitude [m]')
                plt.show()
    
    return Energy_kinetic, Energy_potential, Energy_total, time
