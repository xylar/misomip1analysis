import xarray
import numpy
from collections import OrderedDict

from misomip1analysis.util import string_to_list


def load_datasets(config, variableList=None):
    """
    Load model data

    Parameters
    ----------
    config : ConfigParser
        config options

    variableList : list of str, optional
        a list of variables to keep from each model.  By default, all variables
        are kept.

    Returns
    -------
    datasets : OrderedDict of xarray.Dataset
        A dictionary with one data set for each model

    maxTime : int
        The value of nTime from the longest model data set
    """

    modelNames = string_to_list(config['models']['names'])

    experimentName = config['experiment']['name']

    if 'setup' in config['experiment']:
        setupPrefix = '{}_'.format(config['experiment']['setup'])
    else:
        setupPrefix = ''

    datasets = OrderedDict()
    maxTime = None
    for modelName in modelNames:
        fileName = '{}/{}_{}{}.nc'.format(modelName, experimentName,
                                          setupPrefix, modelName)
        print('Reading data for {}'.format(modelName))

        ds = xarray.open_dataset(fileName, mask_and_scale=True, decode_cf=True,
                                 decode_times=False, engine='netcdf4')
        ds = ds.set_coords([coord for coord in ['time', 'x', 'y', 'z']
                            if coord in ds])

        if variableList is not None:
            ds = ds[variableList]
        datasets[modelName] = ds

        # many MISOMIP output files don't have the _FillValue flag set properly
        missingValue = 9.9692099683868690e36
        for variableName in ds.data_vars:
            var = ds[variableName]
            ds[variableName] = var.where(var != missingValue)

        # fix time if the middle of the month was used instead of the beginning
        time = ds.time.values
        secondsInJanuary = 31*24*60*60
        if numpy.abs(time[0]/secondsInJanuary - 0.5) < 1e-3:
            # very close to 1/2 month beyond where it should be, so let's
            # assume a consistant half-month offset
            daysPerMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            for tIndex in range(len(time)):
                month = numpy.mod(tIndex, 12)
                time[tIndex] -= 0.5*daysPerMonth[month]*24*60*60

            ds['time'] = ('time', time)

        if maxTime is None:
            maxTime = numpy.amax(time)
        else:
            maxTime = max(maxTime, numpy.amax(time))

    return datasets, maxTime
