import matplotlib.pyplot as plt 

def plot_energy(Energy_kinetic, Energy_potential, Energy_total, time, title_plot):
    
    fig1 = plt.figure()
    plt.subplot(1, 1, 1)
    ax1 = plt.gca()

    ax1.plot(time, Energy_kinetic, color = 'blue', linewidth=2, label = r'$E_{c}$')
    ax1.plot(time, Energy_potential, color = 'magenta', linewidth=2, label = r'$E_{p}$')
    ax1.plot(time, Energy_total, color = 'red', linewidth=2, label = r'$E_{tot}$')
 
    plt.title(title_plot)
    ax1.set_xlabel(r'Time (s)', fontsize = 14)
    ax1.set_ylabel(r'Energy (J)', fontsize = 14)
    ax1.legend()

    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)

    plt.show() 
    fig1.savefig("Energy.png")