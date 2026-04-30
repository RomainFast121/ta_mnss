#!/usr/bin/env python3

##########

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import collections as mc


positions = [
    [0, -1],
    [0, 0],
    np.array([1, 1])/np.sqrt(2),
    np.array([-1, 1])/np.sqrt(2)
]

conn = [
    [0, 1],
    [1, 2],
    [1, 3]
]


def compute_minmax(positions):
    return positions.min(axis=0), positions.max(axis=0)


def compute_range(positions):
    _min, _max = compute_minmax(positions)
    return _max - _min


def compute_node_size(positions):
    _range = compute_range(positions)
    _range = _range.max()
    return _range*.08


def packed_eqn(node_idx, dof_per_node, number_of_nodes):
    return np.arange(dof_per_node)+np.ones(dof_per_node)*node_idx*dof_per_node


def eqn_number_node(f_node_eqn, number_of_nodes):
    eqn_number = []
    for n in range(0, number_of_nodes):
        eqn = f_node_eqn(n, 2, number_of_nodes)
        eqn_number.append(np.array(eqn).flatten())
    return np.array(eqn_number, dtype=int)


def eqn_number_elem(eqn_number_node, conn):
    eqn_number = []
    for e in conn:
        eqn = []
        eqn.append(eqn_number_node[e[0], :])
        eqn.append(eqn_number_node[e[1], :])
        eqn_number.append(np.array(eqn).flatten())

    return np.array(eqn_number, dtype=int)


def plot_truss_structure(positions, conn, plot_eqn=None, **kwargs):

    positions = np.array(positions)
    conn = np.array(conn)
    eqn_num_node = None

    if type(plot_eqn) == str:
        if plot_eqn == "packed":
            plot_eqn = packed_eqn
        else:
            raise RuntimeError("not known eqn packing strategy")
        eqn_num_node = eqn_number_node(plot_eqn, positions.shape[0])

    elif type(plot_eqn) == np.ndarray:
        eqn_num_node = plot_eqn
    else:
        if plot_eqn is not None:
            raise RuntimeError("could not get eqn " + str(type(plot_eqn)))

    if plot_eqn is not None:
        eqn_num_elem = eqn_number_elem(eqn_num_node, conn)

    _min, _max = compute_minmax(positions)
    _range = compute_range(positions)
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim((_min[0]-_range.max()*0.2, _max[0]+_range.max()*0.2))
    ax.set_ylim((_min[1]-_range[1].max()*0.2, _max[1]+_range.max()*0.2))

    lines = []

    for i, e in enumerate(conn):
        p1 = positions[e[0]]
        p2 = positions[e[1]]
        lines.append((p1, p2))

    lc = mc.LineCollection(lines, linewidths=2)
    ax.add_collection(lc)
    disp_positions = ax.transData.transform(positions)
    node_size_px = compute_node_size(disp_positions)
    # print(node_size_px)
    ax.scatter(positions[:, 0], positions[:, 1], s=node_size_px**2)

    node_size = compute_node_size(positions)
    # print(node_size)

    # center_gravity = np.average(positions, axis=0)
    center_gravity = (_max+_min)/2
    # print(center_gravity)

    for i, p in enumerate(positions):
        _n = p - center_gravity
        norm = np.linalg.norm(_n)
        if norm < 1e-5:
            _n = np.array([1, 1])
        # print(norm, p, center_gravity,  _n)
        norm = _range.max()*.08/np.linalg.norm(_n)
        _n *= norm
        # print(p, _n)
        pos = p  # + _n
        # print('aaa', _range, p, pos, np.linalg.norm(_n))
        ax.text(pos[0], pos[1], str(i), horizontalalignment='center',
                verticalalignment='center')

        if plot_eqn is not None:
            eqns = eqn_num_node[i, :]
            ax.text(pos[0]+_n[0]*1.5, pos[1]+_n[1]*1.5,
                    "[" + ",".join([str(int(e)) for e in eqns]) + "]",
                    horizontalalignment='center',
                    verticalalignment='center')

    for i, e in enumerate(conn):
        p1 = positions[e[0]]
        p2 = positions[e[1]]
        center = (p1 + p2)/2
        _l = np.zeros(3)
        _l[:2] = p2 - p1
        _l /= np.linalg.norm(_l)
        _n = np.cross(_l, [0, 0, 1])
        # print(_n, node_size)
        center += _n[:2]*node_size*1.5
        ax.text(center[0], center[1], f"({str(i)})",
                horizontalalignment='center',
                verticalalignment='center')

    ret = {}
    if plot_eqn is not None:
        ret['eqn_node'] = np.array(eqn_num_node, dtype=int)
        ret['eqn_elem'] = np.array(eqn_num_elem, dtype=int)
    return ret


################################################################

if __name__ == "__main__":
    # ret = plot_truss_structure(positions, conn, plot_eqn='packed')
    # ret = plot_truss_structure(positions, conn)
    eqn_node = np.array(
        [[2, 3],
         [0, 1],
         [4, 5],
         [6, 7]]
    )
    ret = plot_truss_structure(positions, conn, plot_eqn=eqn_node)
    print(ret)
    plt.show()
