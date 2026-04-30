%% Série 3
% Correction
%% ---------------------------------------------------
function fem_code
% Nettoyage
clear;
clc;

%L'utilisation de variables globales permet de limiter les paramètres de
%fonction
global K coordonnees connectivites materiau nb_elem nb_noeuds nb_ddl_p_noeuds nb_noeuds_p_elem ddl_libres;

% Chargement des fichiers d'entrée
% --------------------------------
coordonnees = load('./bridge_coord.txt');
connectivites = load('./bridge_connect.txt');


plotSystem(coordonnees,'-ok');

% Paramètres du problème
% --------------------------------
nb_ddl_p_noeuds=2;

E = 210*1e9;
A = 10000*1e-6;
f = 100*1e3;

% Initialisation
% --------------------------------
[nb_noeuds, ~] = size(coordonnees);
[nb_elem, nb_noeuds_p_elem] = size(connectivites);

materiau = ones(nb_elem,1);
u = zeros(nb_noeuds*nb_ddl_p_noeuds, 1);
F = zeros(nb_noeuds*nb_ddl_p_noeuds, 1);

precalculerNumerosEquations();

% Définition des propriétés de materiau
% --------------------------------

%Création d'une matrice contenant les propriétés de matériau par élément 
materiau = materiau*E*A;
%Les onzes premières barres ont une plus grande section
materiau(1:11) = materiau(1:11)*2;

% Assemblage de la matrice globale
% --------------------------------

assemblerMatriceRigidite();

% Application des conditions limites
% ----------------------------------

% En force

F(1*nb_ddl_p_noeuds+2) = -f;
F(2*nb_ddl_p_noeuds+2) = -f;
F(3*nb_ddl_p_noeuds+2) = -f;
F(4*nb_ddl_p_noeuds+2) = -f;
F(5*nb_ddl_p_noeuds+2) = -f;

% En déplacement (liste des ddls bloqués)
appliquerConditionLimite([1 2 6*nb_ddl_p_noeuds+2]);

% Résolution du système
% ---------------------

K_libre = K(ddl_libres, ddl_libres);
F_libre = F(ddl_libres);
u_libre = K_libre \ F_libre;
u(ddl_libres) = u_libre;
F = K*u;

% Affichage de la solution 
% ---------------------
disp(u);
disp(F);

% Réorganisation du vecteur déplacmement au format [num_du_noeud,num_du_ddl]
deplacement=zeros(nb_noeuds,nb_ddl_p_noeuds);
for n=1:nb_noeuds
    for d=1:nb_ddl_p_noeuds
        deplacement(n,d) = u((n-1)*nb_ddl_p_noeuds+d);
    end
end

disp(min(deplacement(:,2))*1000); %en mm
plotSystem(coordonnees+500*deplacement,'-or');

end
%% ---------------------------------------------------
function Kl = calculerMatriceRigiditeLocale(k)
    
    Kl = k*[1 0 -1 0; 0 0 0 0; -1 0 1 0; 0 0 0 0];
end
%% ---------------------------------------------------
function assemblerMatriceRigidite()

    global K equations_num nb_noeuds nb_elem nb_ddl_p_noeuds nb_noeuds_p_elem materiau

    K = zeros(nb_noeuds*nb_ddl_p_noeuds, nb_noeuds*nb_ddl_p_noeuds);
    
    for e=1:nb_elem
        
       [R,l] = calculerMatriceRotation(e);
       T = zeros(nb_noeuds_p_elem*nb_ddl_p_noeuds, nb_noeuds_p_elem*nb_ddl_p_noeuds);
       T(1:2,1:2) = R;
       T(3:4,3:4) = R;
       % Construction de la matrice de rigidité locale
       Kl = calculerMatriceRigiditeLocale(materiau(e)/l);
       % Rotation de la matrice dans le système global de coordonnée
       Kg = T*Kl*T';
       % Assemblage dans la matrice de rigidité du système à l'aide des
       % masques Matlab
       K(equations_num(e,:),equations_num(e,:)) = K(equations_num(e,:),equations_num(e,:))+Kg;
    end
end
%% ---------------------------------------------------
function appliquerConditionLimite(blocage)
   
    global ddl_libres nb_noeuds nb_ddl_p_noeuds
    % Construit du vecteur ddl_libres
    ddl_libres = 1:nb_noeuds*nb_ddl_p_noeuds;  
    
    %Tri du vecteur blocage dans l'ordre décroissant
    blocage = sort(blocage,'descend');
    %Retrait des ddl bloqués listés dans le vecteur blocage
    for n=1:length(blocage)
        ddl_libres(blocage(n)) = [];
    end
end
%% ---------------------------------------------------
function [R,l] = calculerMatriceRotation(e) 
    %Calcul de la matrice de rotation du repère local vers le repère global 
    %La fonction retourne également l pour le calcul de la rigidité de l'élément e
    global coordonnees connectivites
    
    n_1 = coordonnees(connectivites(e,1),:);
    n_2 = coordonnees(connectivites(e,2),:);  
    barre = n_1-n_2;    
    l = norm(barre);
    
    R = 1/l * [barre(1) -barre(2); barre(2) barre(1)];
end
%% ---------------------------------------------------
function precalculerNumerosEquations()
    %Calcul la matrice des numéros d'équations à partir des connectivités
    global connectivites nb_ddl_p_noeuds nb_noeuds_p_elem equations_num nb_elem
    
    equations_num = zeros(nb_elem,nb_noeuds_p_elem*nb_ddl_p_noeuds);
    
    for e=1:nb_elem
        for n=1:nb_noeuds_p_elem
            for d=1:nb_ddl_p_noeuds
                equations_num(e,(n-1)*nb_ddl_p_noeuds+d)=(connectivites(e,n)-1)*nb_ddl_p_noeuds+d;
            end
        end
    end
end
%% ---------------------------------------------------
function plotSystem(vect,kwargs)
    %Affichage du maillage ou des déplacements
    global connectivites nb_elem
    figure(1)
    hold on;
    for e=1:nb_elem
       x = [vect(connectivites(e,1),1) vect(connectivites(e,2),1)]; 
       y = [vect(connectivites(e,1),2) vect(connectivites(e,2),2)];
       plot(x,y,kwargs,'LineWidth',2.5,'MarkerSize',12);
    end
end