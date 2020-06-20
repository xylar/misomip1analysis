# misomip1analysis
A python package for analyzing MISOMIP1 and ISOMIP+ simulation results

## Instructions for ISOMIP+

### 1. One-time setup
#### 1.1 install miniconda 

If you don't already have an anaconda python environment:
``` bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
/bin/bash Miniconda3-latest-Linux-x86_64.sh
```
At the end of the install procedure, it will ask you if it should add a line to
your `.bashrc`.  Either do that or manually source the file it says to add to 
your `.bashrc`.

#### 1.2 get the code

Clone from GitHub:
``` bash
git clone git@github.com:xylar/misomip1analysis.git
cd misomip1analysis
git reset --hard origin/add_analysis
```

#### 1.3 create a conda environment
 
Create an env. for running the code:
``` bash
conda create -n misomip python=3.8 xarray dask netcdf4 numpy scipy \
    matplotlib progressbar2 ffmpeg
```

### 1.4. download or link to results

Either download the results from [OSF](https://osf.io/3p8e7/) or make local
symlinks to your own ocean results.  First, make a directory somewhere for the
simulation results and the analysis
``` bash
mkdir isomip+
cd isomip+
```
Then, make one or more subdirectories for the model results:
``` bash
mkdir POP2x
mkdir MPAS-Ocean
...
```
These directories need to have the same model name that appears in the
NetCDF file name:
```
COCO, FVCOM, MITgcm_BAS, MITgcm_BAS_Coupled, MITgcm_JPL, MOM6, MOM6_SIGMA_ZSTAR,
MPAS-Ocean, NEMO-CNRS, NEMO-UKESM1is, POP2x, ROMSUTAS
```
If your files don't have the expected name, you can always make symlinks.

#### 1.5 Make a config file

``` bash
vim config.Ocean0_COM
```
Put the following in the file:
``` ini
[experiment]
## Options related to the experiment being analyzed

# The name of the experiment (one of Ocean0-4 or IceOcean1-2)
name = Ocean0

# The "setup" of the experiment (if any), either COM or TYP
setup = COM

[models]
## Options related to the models to analyze

# A comma-separated list of models whose results should be analyzed
names = POP2x, MPAS-Ocean
```

There are many other [config options](https://github.com/xylar/misomip1analysis/blob/master/misomip1analysis/config.default) 
that you can copy and modify.

### 2. Each time you run the analysis
#### 2.1 activate the environment
``` bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate misomip
```

#### 2.2 Modify the config file (if you need to)

See [misomip1analysis/config.default](https://github.com/xylar/misomip1analysis/blob/master/misomip1analysis/config.default)
for all of the possible config options you can change.

``` bash
vim config.Ocean0_COM
```

Examples can be found in the [configs](https://github.com/xylar/misomip1analysis/blob/master/configs/)
directory in the GitHub repo.

#### 2.3 Run the analysis

``` bash
python -m misomip1analysis config.Ocean0_COM
```

The results will appear in the `analysis` folder
