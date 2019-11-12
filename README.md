# adl2pydm

**NOTE**:  This project is in initial development.  *Be amazed when something works right at this time.  If you find something that does not work right or could be better, please file an [issue](https://github.com/BCDA-APS/adl2pydm/issues/new/choose) since that will be an important matter to be resolved.*

Convert [MEDM](https://epics.anl.gov/extensions/medm/index.php)'s .adl files to [PyDM](https://github.com/slaclab/pydm)'s .ui format

[![Python version](https://img.shields.io/pypi/pyversions/adl2pydm.svg)](https://pypi.python.org/pypi/adl2pydm)
[![unit test](https://travis-ci.org/BCDA-APS/adl2pydm.svg?branch=master)](https://travis-ci.org/BCDA-APS/adl2pydm)
[![Coverage Status](https://coveralls.io/repos/github/BCDA-APS/adl2pydm/badge.svg?branch=master)](https://coveralls.io/github/BCDA-APS/adl2pydm?branch=master)


[![Total alerts](https://img.shields.io/lgtm/alerts/g/BCDA-APS/adl2pydm.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/BCDA-APS/adl2pydm/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/BCDA-APS/adl2pydm.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/BCDA-APS/adl2pydm/context:python)

## Usage

```
user@localhost ~ $ adl2pydm
usage: adl2pydm [-h] [-d DIR] [-v] adlfile
adl2pydm: error: the following arguments are required: adlfile
```

## Help

```
user@localhost ~ $ adl2pydm -h
usage: adl2pydm [-h] [-d DIR] [-v] adlfile

convert MEDM .adl screen file(s) to PyDM .ui format (https://github.com/BCDA-
APS/adl2pydm) v0.0.1+10.gb491da1

positional arguments:
  adlfile            MEDM '.adl' file to convert

optional arguments:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  output directory, default: same directory as input file
  -v, --version      show program's version number and exit
```

## Install

Either:

* `pip install adl2pydm`
* `conda install adl2pydm -c aps-anl-tag`

Note:  Only the standard Python packages are needed to run *adl2pydm*. No additional packages are required.
