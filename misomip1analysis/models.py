import xarray

from misomip1analysis.util import get_config_list

def load_datasets(config, variableList=None):
    '''
    Load model data for a given set of variables (or all variables if
    ``variableList=None``).
    '''

    modelNames = get_config_list(config, 'models', 'names')

    experimentName = config.get('experiment', 'name')

    if config.has_option('experiment', 'setup'):
        setupName = config.get('experiment', 'setup')
    else:
        setupName = None

    datasets = {}
    for modelName in modelNames:
        if setupName is None:
            fileName = '{}/{}_{}.nc'.format(modelName, experimentName,
                                            modelName)
        else:
            fileName = '{}/{}_{}_{}.nc'.format(modelName, experimentName,
                                               setupName, modelName)

        ds = xarray.open_dataset(fileName)
        ds = ds.set_coords(['time', 'x', 'y', 'z'])

        if variableList is not None:
            dropList = [var for var in ds.data_vars if var not in variableList]
            ds = ds.drop(dropList)
        datasets[modelName] = ds

    return datasets
