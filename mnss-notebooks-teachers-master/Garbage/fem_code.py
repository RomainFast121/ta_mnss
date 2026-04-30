#!/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from plot_truss import plot_truss_structure

# Série 3
# Correction
# ---------------------------------------------------


def calculerMatriceRigiditeLocale(k):

    Kl = k*np.array([[1, 0, -1, 0],
                     [0, 0, 0, 0],
                     [- 1, 0, 1, 0],
                     [0, 0, 0, 0]])
    return Kl
# ---------------------------------------------------


def assemblerMatriceRigidite(coordonnees, connectivites, materiau,
                             elem_colors=None, **kwargs):

    equations_num = precalculerNumerosEquations(coordonnees, connectivites)
    nb_noeuds = coordonnees.shape[0]
    nb_elem = connectivites.shape[0]
    nb_noeuds_p_elem = connectivites.shape[1]
    nb_ddl_p_noeuds = 2

    K = np.zeros((nb_noeuds*nb_ddl_p_noeuds, nb_noeuds *
                  nb_ddl_p_noeuds), dtype=object)

    for e in range(0, nb_elem):
        n_1 = coordonnees[connectivites[e, 0], :]
        n_2 = coordonnees[connectivites[e, 1], :]
        R, L = calculerMatriceRotation(n_1, n_2, **kwargs)
        T = np.zeros((nb_noeuds_p_elem*nb_ddl_p_noeuds,
                      nb_noeuds_p_elem*nb_ddl_p_noeuds), dtype=object)
        T[: 2, :2] = R
        T[2:, 2:] = R
        # Construction de la matrice de rigidité locale
        Kl = calculerMatriceRigiditeLocale(materiau[e]/L)
        # Rotation de la matrice dans le système global de coordonnée
        Kg = T@Kl@T.T
        # Assemblage dans la matrice de rigidité du système à l'aide des
        idx = equations_num[e, :]
        for i, gi in enumerate(idx):
            for j, gj in enumerate(idx):
                K[gi, gj] += Kg[i, j]
    return K
# ---------------------------------------------------


def calculerMatriceRotation(p1, p2):
    # Calcul de la matrice de rotation du repère local vers le repère global
    # La fonction retourne également L pour le calcul de la rigidité de
    # l'élément e global coordonnees connectivites

    barre = p2 - p1
    L = np.linalg.norm(barre)

    R = 1/L * np.array([[barre[0], -barre[1]],
                        [barre[1], barre[0]]])

    return R, L


# ---------------------------------------------------
def precalculerNumerosEquations(coordonnees, connectivites):
    # Calcul la matrice des numéros d'équations à partir des connectivités

    nb_elem = connectivites.shape[0]
    nb_noeuds_p_elem = connectivites.shape[1]
    nb_ddl_p_noeuds = 2

    equations_num = np.zeros(
        (nb_elem, nb_noeuds_p_elem*nb_ddl_p_noeuds), dtype=int)

    for e in range(0, nb_elem):
        for n in range(0, nb_noeuds_p_elem):
            for d in range(0, nb_ddl_p_noeuds):
                equations_num[e, (n-1)*nb_ddl_p_noeuds +
                              d] = (connectivites[e, n]-1)*nb_ddl_p_noeuds+d
    return equations_num


def main():
    # Définition des coordonnées
    # --------------------------------
    coordonnees = np.array([
        [0, 0],
        [4, 0],
        [8, 0],
        [12, 0],
        [16, 0],
        [20, 0],
        [24, 0],
        [4, 6],
        [8, 6],
        [16, 6],
        [20, 6]]
    )

    connectivites = np.array([[0,  1],
                              [1, 2],
                              [2, 3],
                              [3, 4],
                              [4, 5],
                              [5, 6],
                              [0, 7],
                              [7, 8],
                              [8, 9],
                              [9, 10],
                              [10, 6],
                              [1, 7],
                              [2, 8],
                              [4, 9],
                              [5, 10],
                              [2, 7],
                              [3, 8],
                              [3, 9],
                              [4, 10]])

    print(connectivites - 1)

    plot_truss_structure(coordonnees, connectivites)

    # Paramètres du problème
    # --------------------------------
    E = 210*1e9
    A = 10000*1e-6
    f = 100*1e3

    # Initialisation
    # --------------------------------
    nb_noeuds = coordonnees.shape[0]
    nb_elem = connectivites.shape[0]

    materiau = np.ones(nb_elem)
    u = np.zeros(nb_noeuds * 2)
    F = np.zeros_like(u)

    # Définition des propriétés de materiau
    # --------------------------------

    # Création d'une matrice contenant les propriétés de matériau par élément
    materiau = materiau*E*A
    # Les onzes premières barres ont une plus grande section
    materiau[:11] *= 2

    # Assemblage de la matrice globale
    # --------------------------------

    K = assemblerMatriceRigidite(coordonnees, connectivites, materiau)

    # Application des conditions limites
    # ----------------------------------

    # En force
    nb_ddl_p_noeuds = 2

    Fview = F.reshape((nb_noeuds, 2))
    Fview[1, 1] = -f
    Fview[2, 1] = -f
    Fview[3, 1] = -f
    Fview[4, 1] = -f
    Fview[5, 1] = -f

    # En déplacement (liste des ddls bloqués)
    blocages = np.zeros_like(u, dtype=bool)
    blocages_view = blocages.reshape((nb_noeuds, 2))
    blocages_view[0, 0] = True
    blocages_view[0, 1] = True
    blocages_view[6, 0] = True
    ddl_libres = np.logical_not(blocages)
    print(ddl_libres.reshape(nb_noeuds, 2))
    # Résolution du système
    # ---------------------

    K_libre = K[ddl_libres, :][:, ddl_libres]
    F_libre = F[ddl_libres]
    u_libre = np.linalg.solve(K_libre, F_libre)
    u[ddl_libres] = u_libre
    F = K@u

    # Affichage de la solution
    # ---------------------
    print(u.reshape(nb_noeuds, 2))
    print(F.reshape(nb_noeuds, 2))
    print(F)

    # Réorganisation du vecteur déplacement au format [num_du_noeud,num_du_ddl]
    deplacement = np.zeros((nb_noeuds, nb_ddl_p_noeuds))
    for n in range(0, nb_noeuds):
        for d in range(0, nb_ddl_p_noeuds):
            deplacement[n, d] = u[(n-1)*nb_ddl_p_noeuds+d]

    print(min(deplacement[:, 1])*1000)  # en mm
    plot_truss_structure(coordonnees+500*deplacement, connectivites)
    plt.show()


if __name__ == "__main__":
    main()
