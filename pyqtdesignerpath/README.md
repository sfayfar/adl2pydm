# Contents

* `pydm_designer_plugin.py` - describes PyDM widgets to Qt designer
* other files - describe how to build conda environment

## Summary

... for those who prefer concise summaries ...

### Install PyDM in custom environment

```
conda create -y -n pydm-environment python pydm -c conda-forge
conda activate pydm-environment
```

### Install PyDM & Bluesky in custom environment

NOTE: these instructions from 2019 are out-of-date

```
# name the custom environment
ENVO=bluesky-pydm

# build ${ENVO} environment
PACKAGES="pydm"
PACKAGES="${PACKAGES} bluesky ophyd databroker hklpy hkl"
PACKAGES="${PACKAGES} apstools stdlogpj pyRestTable spec2nexus pvview bcdamenu"
PACKAGES="${PACKAGES} ipython jupyter notebook jupyterlab flask"
PACKAGES="${PACKAGES} anaconda-client anaconda-project"
PACKAGES="${PACKAGES} sphinx sphinx_rtd_theme"
PACKAGES="${PACKAGES} pytest twine coverage coveralls versioneer"
PACKAGES="${PACKAGES} cfunits curl blosc"
CHANNELS="-c conda-forge -c nsls2forge -c aps-anl-tag"

conda create -y -n ${ENVO} python ${PACKAGES} ${CHANNELS}
conda activate ${ENVO}
```
