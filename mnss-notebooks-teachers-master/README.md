# See it on noto

[Trusses - Lecture](https://noto.epfl.ch/hub/user-redirect/git-pull?repo=https://gitlab.epfl.ch/anciaux/mnss-notebooks&urlpath=lab%2Ftree%2Fmnss-notebooks%2F01_BarresTreillis%2F01_Cours.ipynb)

[Trusses - Exercise](https://noto.epfl.ch/hub/user-redirect/git-pull?repo=https://gitlab.epfl.ch/anciaux/mnss-notebooks&urlpath=lab%2Ftree%2Fmnss-notebooks%2F01_BarresTreillis%2F01_Exercice.ipynb)

# Installation on noto.epfl.ch

There is a need for installation of dependencies. This can be done
installing a virtual environment as follows:

```bash
kbuilder_create mnss git+https://gitlab.com/ganciaux/slides.git
```

# Installation of dependencies with pip on personal machine

```bash
pip install -r requirements.txt
```

# (Re-)generate svg for figures

```
pdflatex fig.tex
inkscape -o fig.svg fig.pdf
```
