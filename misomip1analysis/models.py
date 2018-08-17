import xarray

from misomip1analysis.util import string_to_list

from collections import OrderedDict


def load_datasets(config, variableList=None):
    '''
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
    '''

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

        ds = xarray.open_dataset(fileName, mask_and_scale=True, decode_cf=True,
                                 decode_times=False, engine='netcdf4')
        ds = ds.set_coords(['time', 'x', 'y', 'z'])

        if variableList is not None:
            dropList = [var for var in ds.data_vars if var not in variableList]
            ds = ds.drop(dropList)
        datasets[modelName] = ds

        # many MISOMIP output files don't have the _FillValue flag set properly
        missingValue = 9.9692099683868690e36
        for variableName in ds.data_vars:
            var = ds[variableName]
            ds[variableName] = var.where(var != missingValue)

        nTime = ds.sizes['nTime']
        if maxTime is None:
            maxTime = nTime
        else:
            maxTime = max(maxTime, nTime)

    return datasets, maxTime
