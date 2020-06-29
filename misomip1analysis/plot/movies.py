import os
import numpy
from progressbar import ProgressBar, Percentage, Bar, ETA
import subprocess

import matplotlib.pyplot as plt
import matplotlib.colors as colors

from misomip1analysis.models import load_datasets
from misomip1analysis.util import string_to_list
from misomip1analysis.plot.colormaps import register_custom_colormaps


def plot_movies(config):
    """
    Plot the all requested movies

    Parameters
    ----------
    config : ConfigParser
        config options
    """

    register_custom_colormaps()

    fieldNames = string_to_list(config['movies']['fields'])

    if fieldNames[0] == '':
        # nothing to plot
        return

    for fieldName in fieldNames:
        plot_movie(config, fieldName)


def plot_movie(config, fieldName):
    """
    Plot the frames of a movie from a time-dependent, spatially 2D field and
    then create a movie using ffmpeg

    Parameters
    ----------
    config : ConfigParser
        config options

    fieldName : str
        A field in the model output that can be plotted as a movie
    """

    daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    secondsPerDay = 24.*60.*60.
    secondsPerYear = 365.*secondsPerDay

    datasets, maxTime = load_datasets(config, variableList=[fieldName])

    movies = config['movies']
    startYear = movies.getfloat('startYear')
    startTime = startYear*secondsPerYear
    startYear = int(startYear)
    endTime = min(maxTime, (movies.getfloat('endYear')+1)*secondsPerYear)

    maxYear = int(numpy.ceil(maxTime/secondsPerYear))
    refTime = []
    for year in range(startYear, maxYear+1):
        refTime.append(year*secondsPerYear)
        for month in range(1, 12):
            refTime.append(refTime[-1]+daysPerMonth[month-1]*secondsPerDay)

    refTime = numpy.array(refTime)
    timeIndices = numpy.arange(len(refTime))
    mask = numpy.logical_and(refTime >= startTime, refTime < endTime)
    refTime = refTime[mask]
    timeIndices = timeIndices[mask]

    widgets = [fieldName, Percentage(), ' ', Bar(), ' ', ETA()]
    time_bar = ProgressBar(widgets=widgets,
                           maxval=len(refTime)).start()

    for index in range(len(refTime)):
        _plot_time_slice(config, fieldName, datasets, refTime[index],
                         timeIndices[index])
        time_bar.update(index+1)

    time_bar.finish()

    _frames_to_movie(config, fieldName)


def _plot_time_slice(config, fieldName, datasets, time, timeIndex):
    """
    Plot the frames of a movie from a time-dependent, spatially 2D field and
    then create a movie using ffmpeg

    Parameters
    ----------
    config : ConfigParser
        config options

    fieldName : str
        A field in the model output that can be plotted as a movie

    datasets : dict of xarray.Dataset
        The data sets to plot

    time : float
        The time to plot (by finding the nearest index in the time coordinate)
    """
    framesFolder = config['movies']['framesFolder']
    framesFolder = '{}/{}'.format(framesFolder, fieldName)
    try:
        os.makedirs(framesFolder)
    except OSError:
        pass

    # the file name is the variable followed by the zero-padded time index
    imageFileName = '{}/{}_{:04d}.png'.format(framesFolder, fieldName,
                                              timeIndex)
    if os.path.exists(imageFileName):
        # the image exists so we're going to save time and not replot it
        return

    modelNames = list(datasets.keys())
    modelCount = len(modelNames)
    section = config[fieldName]
    axes = section['axes']
    title = section['title']
    scale = section.getfloat('scale')
    if 'cmap' in section:
        cmap = section['cmap']
    else:
        cmap = 'ferret'

    if 'norm' in section:
        normType = section['norm']
        assert normType in ['linear', 'symlog', 'log']
    else:
        normType = 'linear'

    lower, upper = [float(limit) for limit in
                    string_to_list(section['limits'])]

    timeCoords = [float(coord) for coord in string_to_list(
        config['movies']['{}TimeCoords'.format(axes)])]

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
    row = 0
    for panelIndex in range(len(modelIndices)):
        modelIndex = modelIndices[panelIndex]
        row = rowCount-1 - panelIndex//columnCount
        col = numpy.mod(panelIndex, columnCount)

        if modelIndex >= modelCount:
            plt.delaxes(axarray[row, col])
            continue

        modelName = modelNames[modelIndex]
        ds = datasets[modelName]

        validTimes = numpy.nonzero(numpy.isfinite(ds.time.values))[0]
        ds = ds.isel(nTime=validTimes)

        times = ds.time.values
        localTimeIndex = numpy.interp(time, times,
                                      numpy.arange(ds.sizes['nTime']))
        localTimeIndex = int(localTimeIndex + 0.5)
        ds = ds.isel(nTime=localTimeIndex)
        year = times[localTimeIndex]/config['constants'].getfloat('sPerYr')

        ax = axarray[row, col]

        x = ds[axes[0]].values
        if axes[0] in ['x', 'y']:
            # convert to km
            x = 1e-3*x
        y = ds[axes[1]].values
        if axes[1] in ['x', 'y']:
            # convert to km
            y = 1e-3*y

        im = _plot_panel(ax, x, y, ds[fieldName].values, scale, lower, upper,
                         axes, cmap, normType)

        ax.text(timeCoords[0], timeCoords[1], '{:.2f} a'.format(year),
                fontsize=12)

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


def _plot_panel(ax, x, y, field, scale, lower, upper, axes, cmap, normType):
    """
    Plot a single panel for a given model in a movie frame
    """

    X, Y = _interp_extrap_corners(x, y)

    # convert from float32 to float64 to avoid overflow/underflow problems
    field = numpy.ma.masked_array(field, mask=numpy.isnan(field),
                                  dtype=float)

    field = field*scale

    if normType == 'symlog':
        norm = colors.SymLogNorm(linthresh=lower, linscale=0.5, vmin=-upper,
                                 vmax=upper, base=10.)
    elif normType == 'log':
        norm = colors.LogNorm(vmin=lower, vmax=upper)
    elif normType == 'linear':
        norm = colors.Normalize(vmin=lower, vmax=upper)
    else:
        raise ValueError('Unsupported norm type {}'.format(normType))

    # plot the data as an image
    im = ax.pcolormesh(X, Y, field, cmap=cmap, norm=norm,
                       shading='flat')

    if axes == 'xy':
        ax.set_aspect('equal', adjustable='box')
    else:
        ax.set_aspect('auto', adjustable='box')

    return im


def _interp_extrap_corners(x, y):
    x_corner = numpy.zeros(len(x)+1)
    y_corner = numpy.zeros(len(y)+1)
    x_corner[1:-1] = 0.5*(x[0:-1] + x[1:])
    x_corner[0] = 1.5*x[0] - 0.5*x[1]
    x_corner[-1] = 1.5*x[-1] - 0.5*x[-2]

    y_corner[1:-1] = 0.5*(y[0:-1] + y[1:])
    y_corner[0] = 1.5*y[0] - 0.5*y[1]
    y_corner[-1] = 1.5*y[-1] - 0.5*y[-2]

    X, Y = numpy.meshgrid(x, y)
    return X, Y


def _frames_to_movie(config, fieldName):
    """
    create a movie from frames using ffmpeg

    Parameters
    ----------
    config : ConfigParser
        config options

    fieldName : str
        A field in the model output that can be plotted as a movie
    """
    section = config['ffmpeg']

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
        args = ['ffmpeg', '-y'] + inputArgs + ['-i', framesTemplate] + \
            outputArgs + ['{}/{}_{}.{}'.format(movieFolder, experiment,
                                               fieldName, extension)]
        subprocess.check_call(args)
