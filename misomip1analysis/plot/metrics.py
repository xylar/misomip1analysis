import os
import matplotlib.pyplot as plt

from misomip1analysis.models import load_datasets
from misomip1analysis.util import string_to_list


def plot_metric_timeseries(config):
    """
    Plot a time series of a given metric for all models.

    Parameters
    ----------
    config : ConfigParser
        config options
    """

    experiment = config['experiment']['name']

    metrics = config['metrics']
    metricNames = string_to_list(metrics['names'])
    if metricNames[0] == '':
        # nothing to plot
        return

    plotFolder = metrics['folder']

    try:
        os.makedirs(plotFolder)
    except OSError:
        pass

    colors = string_to_list(metrics['colors'])
    dpi = metrics.getint('dpi')
    lineWidth = metrics.getint('lineWidth')
    figsize = string_to_list(metrics['figsize'])
    figsize = [float(dim) for dim in figsize]

    datasets, maxTime = load_datasets(config, variableList=metricNames)
    modelNames = list(datasets.keys())

    for metricName in metricNames:
        metricConfig = config[metricName]
        semilog = metricConfig.getboolean('semilog')
        scale = metricConfig.getfloat('scale')
        title = metricConfig['title']

        plt.figure(figsize=figsize)
        for modelIndex, modelName in enumerate(modelNames):
            ds = datasets[modelName]
            if metricName not in ds.data_vars:
                continue

            years = ds.time.values/config['constants'].getfloat('sPerYr')
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
