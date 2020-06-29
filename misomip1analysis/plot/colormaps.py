import numpy

import cmocean
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
from matplotlib.cm import register_cmap


def register_custom_colormaps():
    red = numpy.array([[0, 0.6],
                       [0.15, 1],
                       [0.35, 1],
                       [0.65, 0],
                       [0.8, 0],
                       [1, 0.75]])

    green = numpy.array([[0, 0],
                         [0.1, 0],
                         [0.35, 1],
                         [1, 0]])

    blue = numpy.array([[0, 0],
                        [0.5, 0],
                        [0.9, 0.9],
                        [1, 0.9]])

    # light gray for use as an "invalid" background value wherever
    # data has been masked out in the NetCDF file
    backgroundColor = (0.9, 0.9, 0.9)

    colorCount = 21
    ferretColorList = numpy.ones((colorCount, 4), float)
    ferretColorList[:, 0] = numpy.interp(numpy.linspace(0, 1, colorCount),
                                         red[:, 0], red[:, 1])
    ferretColorList[:, 1] = numpy.interp(numpy.linspace(0, 1, colorCount),
                                         green[:, 0], green[:, 1])
    ferretColorList[:, 2] = numpy.interp(numpy.linspace(0, 1, colorCount),
                                         blue[:, 0], blue[:, 1])
    ferretColorList = ferretColorList[::-1, :]

    cmap = colors.LinearSegmentedColormap.from_list('ferret', ferretColorList,
                                                    N=255)
    cmap = plt.get_cmap(cmap)
    cmap.set_bad(backgroundColor)
    register_cmap(name='ferret', cmap=cmap)

    colors1 = cm.get_cmap('cmo.ice_r')(numpy.linspace(0., 0.9, 64))
    colors2 = cm.get_cmap('cmo.solar')(numpy.linspace(0, 1, 192))
    colorlist = numpy.vstack((colors1, colors2))
    cmap = colors.LinearSegmentedColormap.from_list('thermal_driving',
                                                    colorlist)
    cmap.set_bad(backgroundColor)
    register_cmap(name='thermal_driving', cmap=cmap)

    colors1 = cm.get_cmap('cmo.curl')(numpy.linspace(0.5, 0.95, 64))
    colors2 = cm.get_cmap('cmo.haline')(numpy.linspace(0, 1, 192))
    colorlist = numpy.vstack((colors1, colors2))
    cmap = colors.LinearSegmentedColormap.from_list('haline_driving',
                                                    colorlist)
    cmap.set_bad(backgroundColor)
    register_cmap(name='haline_driving', cmap=cmap)

    colors1 = cm.get_cmap('cmo.ice_r')(numpy.linspace(0., 0.9, 128))
    colors2 = cm.get_cmap('cmo.solar')(numpy.linspace(0, 1, 128))
    colorlist = numpy.vstack((colors1, colors2))
    cmap = colors.LinearSegmentedColormap.from_list('thermal_driving_symlog',
                                                    colorlist)
    cmap.set_bad(backgroundColor)
    register_cmap(name='thermal_driving_symlog', cmap=cmap)

    colors1 = cm.get_cmap('cmo.curl')(numpy.linspace(0.5, 0.95, 128))
    colors2 = cm.get_cmap('cmo.haline')(numpy.linspace(0, 1, 128))
    colorlist = numpy.vstack((colors1, colors2))
    cmap = colors.LinearSegmentedColormap.from_list('haline_driving_symlog',
                                                    colorlist)
    cmap.set_bad(backgroundColor)
    register_cmap(name='haline_driving_symlog', cmap=cmap)
