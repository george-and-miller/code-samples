from collections import namedtuple

import pandas as pd
import numpy as np
import pylab as pl
import scipy as sp
import scipy.integrate as si

class NotInDomain(Exception):
    pass


def area_integral(f, lower_x, upper_x, lower_y, upper_y):
    area, _ = si.dblquad(f, lower_y, upper_y, lambda x: lower_x, lambda x: upper_x)
    return area


def line_integral(f, lower_x, upper_x):
    area, _ = si.quad(f, lower_x, upper_x)
    return area


def inside_element(spaces, point):
    for space in spaces:
        if point in space:
            return space
    else:
        raise NotInDomain


class ElementSpace(object):
    def __init__(self, element, nodes):
        self.element = element
        self._alpha, self._beta = nodes[element[0]]
        self._gamma, self._delta = nodes[element[2]]
        self._denominator = ((self._gamma - self._alpha) * (self._delta - self._beta))
        self.centroid = ((self._gamma + self._alpha) / 2, (self._delta + self._beta) / 2)
        self.corners = self._alpha, self._beta, self._gamma, self._delta

        def _n_1(x, y):
            return ((self._gamma - x) * (self._delta - y)) / self._denominator

        def _n_2(x, y):
            return ((x - self._alpha) * (self._delta - y)) / self._denominator

        def _n_3(x, y):
            return ((x - self._alpha) * (y - self._beta)) / self._denominator

        def _n_4(x, y):
            return ((self._gamma - x) * (y - self._beta)) / self._denominator

        def _grad_n_1(x, y):
            return np.array([-(self._delta - y) / self._denominator, -(self._gamma - x) / self._denominator])

        def _grad_n_2(x, y):
            return np.array([(self._delta - y) / self._denominator, (self._alpha - x) / self._denominator])

        def _grad_n_3(x, y):
            return np.array([(-self._beta + y) / self._denominator, (-self._alpha + x) / self._denominator])

        def _grad_n_4(x, y):
            return np.array([(self._beta - y) / self._denominator, (self._gamma - x) / self._denominator])

        self.basis = [_n_1, _n_2, _n_3, _n_4]
        self.gradient = [_grad_n_1, _grad_n_2, _grad_n_3, _grad_n_4]

    def __contains__(self, item):
        return self._alpha <= item[0] <= self._gamma and self._beta <= item[1] <= self._delta

    def solution_gradient(self, alpha):
        return lambda x, y: sum(alpha[i] * space.gradient[i](x, y) for i in range(4))

    def solution(self, alpha):
        return lambda x, y: sum(alpha[i] * space.basis[i](x, y) for i in range(4))

    def region(self):
        return np.linspace(self._alpha, self._gamma, 100), np.linspace(self._beta, self._delta, 100)

    @property
    def mesh(self):
        _x, _y = self.region()
        return np.meshgrid(_x, _y)

    def gradient_basis_inner_product(self, i, j):
        return lambda x, y: self.gradient[i](x, y).dot(self.gradient[j](x, y))


files = namedtuple('Files', 'elements, nodes')
files.elements = './data/channel_elements.dat'
files.nodes = './data/channel_nodes.dat'

elements = pd.read_csv(files.elements, sep='\t', header=None).as_matrix()[:, 1:]
elements = elements - np.ones(np.shape(elements), dtype='int')
nodes = pd.read_csv(files.nodes, sep='\t', header=None).as_matrix()[:, 1:]

number = namedtuple('Number', 'elements, nodes')
number.elements = len(elements)
number.nodes = len(nodes)

boundary = namedtuple('Boundary', 'inflow, outflow')
boundary.inflow = range(0, 9)
boundary.outflow = range(146, 155)

pl.scatter(*nodes.T, marker='.')

spaces = np.empty(number.elements, dtype=ElementSpace)

for index, element in enumerate(elements):
    spaces[index] = ElementSpace(element, nodes)
    pl.text(spaces[index].centroid[0], spaces[index].centroid[1], "{idx}".format(idx=index),
            horizontalalignment='center', verticalalignment='center')

pl.savefig('./output/geometry.pdf', dpi=1200)
pl.clf()

R = np.zeros(number.nodes)
K = np.zeros((number.nodes, number.nodes))

for index, space in enumerate(spaces):
    alpha, beta, gamma, delta = space.corners
    element = space.element
    for i in range(4):
        for j in range(4):
            K[element[i], element[j]] += area_integral(space.gradient_basis_inner_product(i, j),
                                                       alpha, gamma, beta, delta)
    if index in boundary.inflow:
        R[element[0]] += -1 * line_integral(lambda x: space.basis[0](alpha, x), beta, delta)
        R[element[3]] += -1 * line_integral(lambda x: space.basis[3](alpha, x), beta, delta)
    elif index in boundary.outflow:
        R[element[2]] += line_integral(lambda x: space.basis[2](gamma, x), beta, delta)
        R[element[1]] += line_integral(lambda x: space.basis[1](gamma, x), beta, delta)

basis60 = np.zeros(188)
basis60[60] = 1

K[60] = basis60
R[60] = 0

alphas = sp.linalg.solve(K, R)

X, Y, U, V = np.zeros((4, number.elements))

for index, space in enumerate(spaces):
    alpha = alphas[space.element]
    X[index], Y[index] = space.centroid
    U[index], V[index] = space.solution_gradient(alpha)(X[index], Y[index])
    a, b, c, d = space.corners
    pl.plot([a, c], [b, b], color='k', alpha=.3)
    pl.plot([c, c], [b, d], color='k', alpha=.3)
    pl.plot([a, c], [d, d], color='k', alpha=.3)
    pl.plot([a, a], [b, d], color='k', alpha=.3)

pl.quiver(X, Y, U, V)
pl.savefig('./output/vectorfield.pdf', dpi=1200)
pl.clf()

for index, space in enumerate(spaces):
    alpha = alphas[space.element]
    a, b, c, d = space.corners
    pl.plot([a, c], [b, b], color='k', alpha=.3)
    pl.plot([c, c], [b, d], color='k', alpha=.3)
    pl.plot([a, c], [d, d], color='k', alpha=.3)
    pl.plot([a, a], [b, d], color='k', alpha=.3)
    X, Y = space.mesh
    U, V = space.solution_gradient(alpha)(X, Y)
    pl.streamplot(X, Y, U, V, density=.1, color='b')

pl.savefig('./output/streamlines.pdf', dpi=1200)
pl.clf()

#for index, space in enumerate(spaces):
#    alpha = alphas[space.element]
#    a, b, c, d = space.corners
#    pl.plot([a, c], [b, b], color='k', alpha=.3)
#    pl.plot([c, c], [b, d], color='k', alpha=.3)
#    pl.plot([a, c], [d, d], color='k', alpha=.3)
#    pl.plot([a, a], [b, d], color='k', alpha=.3)
#    X, Y = space.mesh()
#    F = space.solution(alpha)(X, Y)
#    pl.pcolormesh(X, Y, F)
#
#pl.savefig('./output/heatmap.pdf', dpi=1200)
#pl.clf()