# pydm installed with bluesky

Noticing that *designer* is not working with (at least one of) my 
*bluesky* installations, I want to identify why.

## Environment variables

Per the revised [installation notes](install-pydm.md), designer
works (*works* means: finds the PyDM widget plugins) 
when *pydm* is installed in a custom conda environment.

In my typical *bluesky* environment, designer does not find the plugins.
A comparison of the environment variables for each is obtained
with the command `env | sort > ${CONDA_DEFAULT_ENV}.txt`
The [differences](diffs.txt) between the two environments are minor.
Both `EPICS_BASE` and `EPICS_HOST_ARCH` are not relevant.
`PYQTDESIGNERPATH` is defined properly (and populated properly) in both.
For the *bluesky* environment, `PATH` has an extra (and unnecessary)
`/home/mintadmin/Apps/anaconda/bin` as the second item, but removing this
from `PATH` has no effect.

It's not obvious why, when using the *bluesky* environment, the designer 
does not find the PyDM widget plugins.  However, examination of the environment
variables does not reveal the reason.

## Installed packages
