import numpy as np
import matplotlib.pyplot as plt

import ipywidgets as widgets
from IPython.display import display

K = np.zeros([2,2])
b = np.array([0,1])



def make_widget1():
    #L1 = widgets.IntSlider(description='L1',min=1)
    ratio = widgets.FloatLogSlider(
        value=0.5,
        base=10,
        min=-2, # max exponent of base
        max=-0.00001, # min exponent of base
        step=0.01, # exponent step
        description='L1')
    A1 = widgets.FloatLogSlider(
        value=10,
        base=10,
        min=0, # max exponent of base
        max=10, # min exponent of base
        step=0.2, # exponent step
        description='EA1')
    #L2 = widgets.IntSlider(description='L2',min=1)
    A2 = widgets.FloatLogSlider(
        value=10,
        base=10,
        min=0, # max exponent of base
        max=10, # min exponent of base
        step=0.2, # exponent step
        description='EA2')
    F = widgets.IntSlider(description='F',min=1)





    coords=np.array([[0,0],[1,0],[2,0]])
    conn = np.array([[0,1],[1,2]])

    

    def plotplot(ratio,A1,A2,F):
        L1 = ratio
        L2 = 1-ratio
        coords[1,0]=L1
        coords[2,0]=L1+L2

        Ks = [A1,A2]
        thickness = lambda K: 20*((np.log(K)+1)/10)
        thickness = lambda K: 10

        

        for i,bar in enumerate(conn):
            barc= coords[bar]
            plt.plot(barc[:,0],barc[:,1],'-', linewidth=thickness(Ks[i]), markersize=2*thickness(Ks[i]))


        plt.arrow(L1+L2,0,(L1+L2)/10,0, color='r', width = 0.03, head_width = 0.09)
        plt.ylim([-1,1])
        plt.xlim([-0.1*(L1+L2),1.25*(L1+L2)])

    def writeK(ratio,A1,A2):
        L1 = ratio
        L2 = 1-ratio
        K1 = A1/L1
        K2 = A2/L2

       # K = np.array([[K1+K2, -K2],[-K2, K2]])
        global K
        
        K[0,0]= K1+K2
        K[0,1] = -K2
        K[1,0] = -K2
        K[1,1] = K2


        K_list = ["{:.3g}".format(s) for s in [K[0,0],K[0,1],K[1,0],K[1,1]]]
        
        print("K : \n |  {:<9} {:<9} | \n | {:<9}   {:<9}|".format(*K_list))
        cond = np.linalg.cond(K)
        print('\n Condition number : {:.1g} '.format(cond))
        
        
    def writeKpert(ratio,A1,A2):
        L1 = ratio
        L2 = 1-ratio
        K1 = A1/L1
        K2 = A2/L2

       # K = np.array([[K1+K2, -K2],[-K2, K2]])
        Kb = np.zeros((2,2))
        
        Kb[0,0]= (K1+K2)*(1+1e-8)
        Kb[0,1] = -K2
        Kb[1,0] = -K2
        Kb[1,1] = K2

        #plot_matrix(K, "K")
        print("K perturbé: \n | ", Kb[0,0], ' ',Kb[0,1], ' | \n | ', Kb[1,0], ' ',Kb[1,1], ' | ')
        


    def writeX(ratio,A1,A2):
        
        L1 = ratio
        L2 = 1-ratio
        K1 = A1/L1
        K2 = A2/L2

       # K = np.array([[K1+K2, -K2],[-K2, K2]])
        global K
        
        K[0,0]= K1+K2
        K[0,1] = -K2
        K[1,0] = -K2
        K[1,1] = K2
        
        
        
        sol = np.linalg.inv(K).dot(b)
        
        sol_list = ["{:.3g}".format(s) for s in sol]


        print("d : \n | {:>9} | \n | {:>9} |".format(*sol_list))
        
        
    def writeXb(ratio,A1,A2):
        
        L1 = ratio
        L2 = 1-ratio
        K1 = A1/L1
        K2 = A2/L2

        Kb = np.zeros((2,2))
        
        Kb[0,0]= (K1+K2)*(1+1e-6)
        Kb[0,1] = -K2
        Kb[1,0] = -K2
        Kb[1,1] = K2
        
        
        sol = np.linalg.inv(Kb).dot(b)

        sol_list = ["{:.3g}".format(s) for s in sol]
        print("d* perturbé : \n | {:>9} | \n | {:>9} |".format(*sol_list))
        
        
    def normDiff(ratio,A1,A2):
        
        L1 = ratio
        L2 = 1-ratio
        K1 = A1/L1
        K2 = A2/L2

       # K = np.array([[K1+K2, -K2],[-K2, K2]])
        global K
        
        K[0,0]= K1+K2
        K[0,1] = -K2
        K[1,0] = -K2
        K[1,1] = K2
        
        
        
        sol1 = np.linalg.inv(K).dot(b)

        Kb = np.zeros((2,2))
        
        Kb[0,0]= (K1+K2)*(1+1e-6)
        Kb[0,1] = -K2
        Kb[1,0] = -K2
        Kb[1,1] = K2
        
        
        sol2 = np.linalg.inv(Kb).dot(b)

        #plot_matrix(K, "K")
        print("    ||d - d*||/||dA|| : {:.2g}".format(np.linalg.norm(sol2-sol1)/(1e-6)))
     




    #outLeft = widgets.VBox([L1,A1,L2,A2,F])
    sliders = widgets.VBox([ratio,A1,A2])
    beamplot = widgets.interactive_output(plotplot, {'ratio': ratio, 'A1': A1,'A2': A2,'F': F})
    Kplot = widgets.interactive_output(writeK, {'ratio': ratio, 'A1': A1,'A2': A2})
    Kpertplot = widgets.interactive_output(writeKpert, {'ratio': ratio, 'A1': A1,'A2': A2})
    Xplot = widgets.interactive_output(writeX, {'ratio': ratio, 'A1': A1,'A2': A2})
    Xbplot = widgets.interactive_output(writeXb, {'ratio': ratio, 'A1': A1,'A2': A2})
    normD = widgets.interactive_output(normDiff, {'ratio': ratio, 'A1': A1,'A2': A2})
    
    return [sliders,beamplot,Kplot,Kpertplot, Xplot,Xbplot,normD]
