#!/usr/bin/env pyton
################################################################
import numpy as np
import sys
from sympy import latex
from IPython.display import display, Math
from IPython.core.interactiveshell import InteractiveShell
import IPython
import sympy
from io import BytesIO
# from . import presentation_helper as ph
################################################################


def print_latex(sstr, *argv, ret=False):
    args = []
    for a in argv:
        try:
            ff = a._repr_latex_()
            ff = ff[1:-1]
        except Exception as e:
            print(e)
            ff = latex(a)
        args.append(ff)
    sstr = sstr.format(*args)
    if sys.version_info.major < 3:
        raise Exception("Must be using Python 3")
    if sys.version_info.minor >= 9:
        sstr = '$' + sstr + '$'

    # print(sstr)
    res = Math(sstr)
    display(res)
    if ret is True:
        return res
    return None

################################################################


class ColoredMatrix:

    color_def = {
        'b': 'blue',
        'g': 'green',
        'r': 'red',
        'p': 'purple',
        'c': 'cyan',
        'm': 'magenta',
        'y': 'yellow',
        'k': 'black',
        'w': 'white',
        'bg': 'magenta',
        'gr': 'purple',
        'bk': 'blue'
    }

    def __init__(self, mat):

        if isinstance(mat, ColoredMatrix):
            self.mat = mat.mat
        else:
            self.mat = mat

        self.colors = np.zeros(self.mat.shape, dtype='S10')
        self.alternative = np.zeros(self.mat.shape, dtype='S10')
        self.sym = False

    def __len__(self):
        return self.mat.__len__()

    def dot(self, mat):
        return self.mat.dot(mat)

    def __mul__(self, n):
        return self.mat.__mul__(n)

    def __rmul__(self, n):
        return n*self.mat

    def __div__(self, n):
        temp = ColoredMatrix(self.mat.__div__(n))
        temp.colors[:] = self.colors[:]
        return temp

    def copy(self):
        _mat = ColoredMatrix(self.mat.copy())
        _mat.colors = self.colors.copy()
        return _mat

    def evalf(self, *args):
        mat_eval = self.mat.evalf(*args)
        new_mat = ColoredMatrix(mat_eval)
        new_mat.colors = self.colors.copy()
        return new_mat

    def __getitem__(self, index):
        sub_mat = self.mat.__getitem__(index)
        if not hasattr(sub_mat, 'shape'):
            return sub_mat

        new_mat = ColoredMatrix(sub_mat)
        new_mat.colors = self.colors[index].reshape(sub_mat.shape)
        return new_mat

    def __setitem__(self, index, value):
        return self.mat.__setitem__(index, value)

    def _get_coeff(self, i, j=0):
        if self.alternative[i, j].decode() != '':
            return self.alternative[i, j].decode()

        return latex(self.mat[i, j])

    def _colored_coeff(self, i, j=0):

        if self.sym is True:
            if i == self.mat.shape[0]-1 and j == 0:
                return 'Sym.'

            return ''

        color = self.colors[i, j].decode()
        if color in self.color_def:
            color = self.color_def[color]
        else:
            color = 'black'

        coeff = self._get_coeff(i, j)
        if coeff == '':
            return ''

        return (r'{\color{' + color + '}{' + coeff + '}}')

    def profile(self, symbol=r'\diamond', remove_zeros=False):
        _mat = self.mat.copy()
        new_mat = ColoredMatrix(_mat)
        new_mat.colors = self.colors.copy()
        new_mat.alternative[:] = symbol
        if remove_zeros:
            new_mat.colors[np.array(_mat) == 0] = 'w'
        return new_mat

    def _repr_latex_(self):
        m = self.mat.shape[0]

        if len(self.mat.shape) > 1 and self.mat.shape[1] > 1:
            n = self.mat.shape[1]

            result = ''
            for i in range(0, m):
                row = []
                for j in range(0, n):
                    row.append(self._colored_coeff(i, j))

                result += ' & '.join(row)
                if i < m-1:
                    result += r'\\'
            result = (r'\left[\begin{array}{' + 'c'*n + '}' +
                      result + r'\end{array}\right]')

        else:
            rows = []
            for i in range(0, m):
                rows.append(self._colored_coeff(i))
            result = r'\\'.join(rows)
            result = (r'\left\{\begin{matrix}' +
                      result + r'\end{matrix}\right\}')

        return '$' + result + '$'

################################################################
def _print_latex_png(o):
    o = o._repr_latex_()
    dvioptions = None
    exprbuffer = BytesIO()
    # from IPython.core.debugger import Tracer
    # Tracer()()
    sympy.preview(o, output='png', viewer='BytesIO',
                  outputbuffer=exprbuffer, packages=('xcolor',),
                  dvioptions=dvioptions)
    return exprbuffer.getvalue()

################################################################


def _print_latex_svg(o):
    o = o._repr_latex_()
    dvioptions = None
    exprbuffer = BytesIO()
    # from IPython.core.debugger import Tracer
    # Tracer()()
    sympy.preview(o, output='svg', viewer='BytesIO',
                  outputbuffer=exprbuffer, packages=('xcolor',),
                  dvioptions=dvioptions)
    return exprbuffer.getvalue().decode()

################################################################

def registerFormatter(_type, _format, formatter_functor):
    f = InteractiveShell.instance().display_formatter.formatters[_format]
    f.for_type(_type, func=formatter_functor)

################################################################


def init_printing():
    sympy.init_printing()
    registerFormatter(IPython.core.display.Math,
                      'image/svg+xml', _print_latex_svg)
    registerFormatter(IPython.core.display.Math, 'image/png', _print_latex_png)

################################################################


init_printing()
