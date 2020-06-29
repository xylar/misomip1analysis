#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'misomip1analysis', '__init__.py')) as f:
    init_file = f.read()
version = re.search(r'{}\s*=\s*[(]([^)]*)[)]'.format('__version_info__'),
                    init_file).group(1).replace(', ', '.')

setup(name='misomip1analysis',
      version=version,
      description='A python package for analyzing MISOMIP1 and ISOMIP+ '
                  'simulation results.',
      url='https://github.com/xylar/misomip1analysis',
      author='Xylar Asay-Davis',
      author_email='xylarstorm@gmail.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering',
      ],
      packages=find_packages(),
      package_data={'misomip1analysis': ['config.default']},
      install_requires=['numpy', 'scipy', 'matplotlib', 'netCDF4', 'xarray',
                        'dask', 'progressbar2', 'cmocean'],
      entry_points={'console_scripts':
                    ['misomip1analysis = misomip1analysis.__main__:main']})
