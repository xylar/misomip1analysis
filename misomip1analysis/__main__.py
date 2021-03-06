"""
Script for starting MISOMIP1 analysis
"""

import os
import argparse
import pkg_resources
from configparser import ConfigParser, ExtendedInterpolation

import misomip1analysis
from misomip1analysis.plot.metrics import plot_metric_timeseries
from misomip1analysis.plot.movies import plot_movies
from misomip1analysis.plot.gl_movies import plot_movies as plot_gl_movies


def main():

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configFiles', metavar='CONFIG',
                        type=str, nargs='*', help='config file')
    parser.add_argument('-v', '--version',
                        action='version',
                        version='misomip1analysis {}'.format(
                                misomip1analysis.__version__),
                        help="Show version number and exit")
    args = parser.parse_args()

    for configFile in args.configFiles:
        if not os.path.exists(configFile):
            raise OSError('Config file {} not found.'.format(configFile))

    # add config.default to cover default not included in the config files
    # provided on the command line
    if pkg_resources.resource_exists('misomip1analysis', 'config.default'):
        defaultConfig = pkg_resources.resource_filename('misomip1analysis',
                                                        'config.default')
        configFiles = [defaultConfig] + args.configFiles
    else:
        print('WARNING: Did not find config.default.  Assuming other config '
              'file(s) contain a\n'
              'full set of configuration options.')
        configFiles = args.configFiles

    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(configFiles)

    plot_metric_timeseries(config)
    plot_movies(config)
    plot_gl_movies(config)


if __name__ == "__main__":
    main()
