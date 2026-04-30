#!/usr/bin/env python

import os
import sys
repo_name = 'mnss-notebooks/'


################################################################
def printlink(d, f):
    base = os.path.splitext(f)[0]
    print('- [' + d + ':' + base + '](https://noto.epfl.ch/hub/user-redirect/git-pull?repo=https://gitlab.epfl.ch/anciaux/mnss-notebooks&urlpath=lab/tree/' +
          repo_name + '/' + d + '/' + f + ')')


#  https://noto.epfl.ch/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgitlab.epfl.ch%2Fanciaux%2Fmnss-notebooks&urlpath=lab%2Ftree%2Fmnss-notebooks%2F01_Ressorts%2FExercice_02.ipynb&branch=master

################################################################


def createlinks(d):
    ls = os.listdir(d)
    for f in ls:
        _file = os.path.join(d, f)
        if not os.path.isfile(_file):
            continue
        base, ext = os.path.splitext(_file)
        if ext != '.ipynb':
            continue
        printlink(d, f)


################################################################


ls = os.listdir()

for d in sorted(ls):
    if not os.path.isdir(d):
        continue

    if d in ['.git', 'Garbage', '.ipynb_checkpoints',
             'publish', 'publish-final', 'outils_projets']:
        continue

    # print(d)
    createlinks(d)
    print('')
