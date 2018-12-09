from misomip1analysis.models import load_datasets
from misomip1analysis.util import string_to_list

import os
import numpy
from progressbar import ProgressBar, Percentage, Bar, ETA
import subprocess
from distutils.spawn import find_executable

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors


def plot_movies(config):
    '''
    Plot the all requested movies

    Parameters
    ----------
    config : ConfigParser
        config options
    '''

    _register_ferret_colormap()

    fieldNames = string_to_list(config['movies']['fields'])
    for fieldName in fieldNames:
        plot_movie(config, fieldName)


def plot_movie(config, fieldName):
    '''
    Plot the frames of a movie from a time-dependent, spatially 2D field and
    then create a movie using ffmpeg (if available)

    Parameters
    ----------
    config : ConfigParser
        config options

    fieldName : str
        A field in the model output that can be plotted as a movie
    '''

    datasets, maxTime = load_datasets(config, variableList=[fieldName])

    movies = config['movies']
    tIndexStart = int(12*movies.getfloat('startYear')+0.5)
    tIndexEnd = min(maxTime, int(12*(movies.getfloat('endYear')+1)+0.5))

    widgets = [fieldName, Percentage(), ' ', Bar(), ' ', ETA()]
    time_bar = ProgressBar(widgets=widgets,
                           maxval=(tIndexEnd-tIndexStart)).start()

    for timeIndex in range(tIndexStart, tIndexEnd):
        _plot_time_slice(config, fieldName, datasets, timeIndex)
        time_bar.update(timeIndex-tIndexStart+1)

    time_bar.finish()

    _frames_to_movie(config, fieldName)


def _plot_time_slice(config, fieldName, datasets, timeIndex):
    '''
    Plot the frames of a movie from a time-dependent, spatially 2D field and
    then create a movie using ffmpeg (if available)

    Parameters
    ----------
    config : ConfigParser
        config options

    fieldName : str
        A field in the model output that can be plotted as a movie

    datasets : dict of xarray.Dataset
        The data sets to plot

    timeIndex : int
        The index into the time series to plot
    '''
    framesFolder = config['movies']['framesFolder']
    framesFolder = '{}/{}'.format(framesFolder, fieldName)
    try:
        os.makedirs(framesFolder)
    except OSError:
        pass

    # the file name is the variable followed by the zero-padded time index
    imageFileName = '{}/{}_{:04d}.png'.format(framesFolder, fieldName,
                                              timeIndex)
    if(os.path.exists(imageFileName)):
        # the image exists so we're going to save time and not replot it
        return

    modelNames = list(datasets.keys())
    modelCount = len(modelNames)
    section = config[fieldName]
    axes = section['axes']
    title = section['title']
    scale = section.getfloat('scale')
    lower, upper = [float(limit) for limit in
                    string_to_list(section['limits'])]

    if axes == 'xy':
        columnCount = min(3, modelCount)
        xLabel = 'x (km)'
        yLabel = 'y (km)'
        rowScale = 1.2
    elif axes == 'xz':
        columnCount = min(4, modelCount)
        rowScale = 2.0
        xLabel = 'x (km)'
        yLabel = 'z (m)'
    elif axes == 'yz':
        columnCount = min(4, modelCount)
        rowScale = 2.0
        xLabel = 'y (km)'
        yLabel = 'z (m)'
    else:
        raise ValueError('Unknow axes value {}'.format(axes))

    rowCount = (modelCount+columnCount-1)//columnCount

    modelIndices = numpy.reshape(numpy.arange(rowCount*columnCount),
                                 (rowCount, columnCount))[::-1, :].ravel()

    figsize = [16, 0.5+rowScale*(rowCount+0.5)]
    fig, axarray = plt.subplots(rowCount, columnCount, sharex='col',
                                sharey='row', figsize=figsize, dpi=100,
                                facecolor='w')

    if modelCount == 1:
        axarray = numpy.array(axarray)

    if rowCount == 1:
        axarray = axarray.reshape((rowCount, columnCount))

    lastImage = []
    for panelIndex in range(len(modelIndices)):
        modelIndex = modelIndices[panelIndex]
        row = rowCount-1 - panelIndex//columnCount
        col = numpy.mod(panelIndex, columnCount)

        if modelIndex >= modelCount:
            plt.delaxes(axarray[row, col])
            continue

        modelName = modelNames[modelIndex]
        ds = datasets[modelName]

        localTimeIndex = min(timeIndex, ds.sizes['nTime']-1)
        ds = ds.isel(nTime=localTimeIndex)
        year = ds.time.values/config['constants'].getfloat('sPerYr')

        # convert x and y to km
        ranges = {}
        for varName in ['x', 'y']:
            ranges[varName] = [1e-3*ds[varName].min(), 1e-3*ds[varName].max()]
        ranges['z'] = [ds.z.min(), ds.z.max()]

        extent = []
        for axis in axes:
            extent += ranges[axis]

        if axes == 'xy':
            # the y extent is max then min because the y axis then gets flipped
            # (imshow is weird that way)
            extent = [extent[0], extent[1], extent[3], extent[2]]

        ax = axarray[row, col]

        im = _plot_panel(ax, ds[fieldName].values, '{:.2f} a'.format(year),
                         scale, lower, upper, extent, axes)

        if row == rowCount-1:
            ax.set_xlabel(xLabel)

        if col == columnCount-1:
            lastImage.append(im)

        if col == 0:
            ax.set_ylabel(yLabel)
            for label in ax.yaxis.get_ticklabels()[0::2]:
                label.set_visible(False)

        ax.set_title(modelNames[modelIndex])
        plt.tight_layout()

    fig.subplots_adjust(right=0.91)
    if rowCount == 1:
        fig.subplots_adjust(top=0.85)
    else:
        fig.subplots_adjust(top=0.9)
    pos0 = axarray[0, -1].get_position()
    pos1 = axarray[-1, -1].get_position()
    top = pos0.y0 + pos0.height
    height = top - pos1.y0
    cbar_ax = fig.add_axes([0.92, pos1.y0, 0.02, height])
    cbar = fig.colorbar(lastImage[row], cax=cbar_ax)
    if rowCount == 1:
        for label in cbar.ax.yaxis.get_ticklabels()[1::2]:
            label.set_visible(False)

    plt.suptitle(title)

    plt.draw()
    plt.savefig(imageFileName)

    plt.close()


def _plot_panel(ax, field, label, scale, lower, upper, extent, axes):
    '''
    Plot a single panel for a given model in a movie frame
    '''

    ax.set_adjustable('box')

    # aspect ratio
    if(axes == 'xy'):
        # pixels are 1:1
        aspectRatio = None
    else:
        # stretch the axes to fill the plot area
        aspectRatio = 'auto'

    # convert from float32 to float64 to avoid overflow/underflow problems
    field = numpy.ma.masked_array(field, mask=numpy.isnan(field),
                                  dtype=float)

    field = field*scale

    # plot the data as an image
    im = ax.imshow(field, extent=extent, cmap='ferret', vmin=lower, vmax=upper,
                   aspect=aspectRatio, interpolation='nearest')

    if(axes == 'xy'):
        # y axis will be upside down in imshow, which we don't want for xy
        ax.invert_yaxis()
        ax.text(350., 60., label, fontsize=12)
    else:
        # upside-down y axis is okay
        ax.text(350., -80., label, fontsize=12)

    return im


def _frames_to_movie(config, fieldName):
    '''
    create a movie from frames using ffmpeg (if available)

    Parameters
    ----------
    config : ConfigParser
        config options

    fieldName : str
        A field in the model output that can be plotted as a movie
    '''
    section = config['ffmpeg']
    ffmpeg = section['path']
    if find_executable(ffmpeg) is None:
        print('WARNING: {} not found. Frames will not be converted to '
              'movies.'.format(ffmpeg))
        return

    experiment = config['experiment']['name']
    movieFolder = config['movies']['folder']
    try:
        os.makedirs(movieFolder)
    except OSError:
        pass
    framesFolder = config['movies']['framesFolder']
    framesTemplate = '{}/{}/{}_%04d.png'.format(framesFolder, fieldName,
                                                fieldName)

    inputArgs = string_to_list(section['input'], separator=' ')
    outputArgs = string_to_list(section['output'], separator=' ')
    extensions = string_to_list(section['extensions'])

    for extension in extensions:
        args = [ffmpeg, '-y'] + inputArgs + ['-i', framesTemplate] + \
            outputArgs + ['{}/{}_{}.{}'.format(movieFolder, experiment,
                                               fieldName, extension)]
        subprocess.check_call(args)


def _register_ferret_colormap():
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
    matplotlib.cm.register_cmap(name='ferret', cmap=cmap)
