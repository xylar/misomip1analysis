from misomip1analysis.models import load_datasets
from misomip1analysis.util import get_config_list
from misomip1analysis import constants

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_metric_timeseries(config):
    '''
    Plot a time series of a given metric for all models.

    Parameters
    ----------
    config : ConfigParser
        config options
    '''

    experiment = config.get('experiment', 'name')
    modelNames = get_config_list(config, 'models', 'names')

    metricNames = get_config_list(config, 'metrics', 'names')
    plotFolder = config.get('metrics', 'folder')

    try:
        os.makedirs(plotFolder)
    except OSError:
        pass

    colors = get_config_list(config, 'metrics', 'colors')
    dpi = config.getint('metrics', 'dpi')
    lineWidth = config.getint('metrics', 'lineWidth')
    figsize = get_config_list(config, 'metrics', 'figsize')
    figsize = [float(dim) for dim in figsize]

    datasets = load_datasets(config, variableList=metricNames)

    maxTime = None
    for modelName in modelNames:
        nTime = datasets[modelName].sizes['nTime']
        if maxTime is None:
            maxTime = nTime
        else:
            maxTime = max(maxTime, nTime)

    for metricName in metricNames:
        semilog = config.getboolean(metricName, 'semilog')
        scale = config.getfloat(metricName, 'scale')
        title = config.get(metricName, 'title')

        plt.figure(figsize=figsize)
        for modelIndex, modelName in enumerate(modelNames):
            ds = datasets[modelName]
            if metricName not in ds.data_vars:
                continue

            years = ds.time.values/constants.sPerYr
            field = scale*ds[metricName].values
            if semilog:
                plt.semilogy(years, field, label=modelName,
                             color=colors[modelIndex], linewidth=lineWidth)
            else:
                plt.plot(years, field, label=modelName,
                         color=colors[modelIndex], linewidth=lineWidth)

        plt.ylabel(title)
        plt.xlabel('time (a)')
        plt.legend(loc='best')
        plt.tight_layout()
        plt.draw()
        plt.savefig('{}/{}_{}.png'.format(plotFolder, experiment, metricName),
                    dpi=dpi)
        plt.close()
