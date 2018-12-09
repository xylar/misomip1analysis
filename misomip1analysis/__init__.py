
# set the backend to Agg right away so that applies to all plots and PEP8
# doesn't complain about imports
import matplotlib
matplotlib.use('Agg')

__version_info__ = (1, 0, 0)
__version__ = '.'.join(str(vi) for vi in __version_info__)
