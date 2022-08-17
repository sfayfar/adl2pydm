# adl2pydm

[![release](https://img.shields.io/github/release/BCDA-APS/adl2pydm.svg)](https://github.com/BCDA-APS/adl2pydm/releases)
[![Python version](https://img.shields.io/pypi/pyversions/adl2pydm.svg)](https://pypi.python.org/pypi/adl2pydm)
[![PyPi](https://img.shields.io/pypi/v/adl2pydm.svg)](https://pypi.python.org/pypi/adl2pydm)
[![aps-anl-tag](https://img.shields.io/conda/vn/aps-anl-tag/adl2pydm)](https://anaconda.org/aps-anl-tag/adl2pydm)

[![license: ANL](https://img.shields.io/badge/license-ANL-brightgreen)](LICENSE.txt)
![Unit Tests](https://github.com/BCDA-APS/adl2pydm/workflows/Unit%20Tests/badge.svg)

**NOTE**:  This project is in initial development.  *Be amazed when something works right at this time.  If you find something that does not work right or could be better, please file an [issue](https://github.com/BCDA-APS/adl2pydm/issues/new/choose) since that will be an important matter to be resolved.*

Convert [MEDM](https://epics.anl.gov/extensions/medm/index.php)'s .adl files to [PyDM](https://github.com/slaclab/pydm)'s .ui format

## Usage

```
user@localhost ~ $ adl2pydm
usage: adl2pydm [-h] [-d DIR] [-v] adlfile
adl2pydm: error: the following arguments are required: adlfile
```

## Help

```bash
user@localhost ~ $ adl2pydm -h
usage: adl2pydm [-h] [-d DIR] [-v] [-log LOG] [--use-scatterplot] adlfiles [adlfiles ...]

Convert MEDM's .adl screen file(s) to PyDM .ui format. (https://github.com/BCDA-APS/adl2pydm) v0.0.1+279.g5d2b329.dirty

positional arguments:
  adlfiles             MEDM '.adl' file(s) to convert

optional arguments:
  -h, --help           show this help message and exit
  -d DIR, --dir DIR    output directory, default: same directory as input file
  -v, --version        show program's version number and exit
  -log LOG, --log LOG  Provide logging level. Example --log debug', default='warning'
  --use-scatterplot    Translate MEDM 'cartesian plot' widget as `PyDMScatterPlot` instead of `PyDMWaveformPlot`, default=False
```

## Install

Only the `pip` install is working now ([PyPI package](https://pypi.org/project/punx/)):

* `pip install adl2pydm`

Once a `conda` package has been built and uploaded to the
[`aps-anl-tag` channel on conda-forge](https://anaconda.org/aps-anl-tag),
(see [related GitHub issue](https://github.com/BCDA-APS/adl2pydm/issues/85)) then:

* `conda install adl2pydm -c aps-anl-tag`

Note:  Only the standard Python (3.7 or higher) packages are needed to run
*adl2pydm*. No additional packages are required.
