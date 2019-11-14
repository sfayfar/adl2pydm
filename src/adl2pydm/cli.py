#!/usr/bin/env python

"""
convert MEDM .adl screen file(s) to PyDM .ui format

Only rely on packages in this project or from the standard Python distribution. 
"""

import argparse
# from collections import namedtuple
import logging
import os

from . import adl_parser
from . import output_handler


logging.basicConfig(level=logging.DEBUG)        # development
# logging.basicConfig(level=logging.WARNING)      # production
logger = logging.getLogger(__name__)


def processFile(adl_filename, output_path=None):
    output_path = output_path or os.path.dirname(adl_filename)

    screen = adl_parser.MedmMainWidget(adl_filename)
    buf = screen.getAdlLines(adl_filename)
    screen.parseAdlBuffer(buf)
    
    writer = output_handler.Widget2Pydm()
    writer.write_ui(screen, output_path)


def get_user_parameters():
    import adl2pydm
    doc = __doc__.strip().splitlines()[0]
    doc += ' (%s)' % adl2pydm.__url__
    doc += ' v' + adl2pydm.__version__
    parser = argparse.ArgumentParser(
        prog=adl2pydm.__package__, description=doc)

    msg = "MEDM '.adl' file to convert"
    parser.add_argument('adlfile', action='store', help=msg)

    msg =  "output directory"
    msg += ", default: same directory as input file"
    parser.add_argument(
        '-d', 
        '--dir',
        action='store', 
        dest='dir', 
        help=msg, 
        default=None)

    parser.add_argument(
        '-v', 
        '--version', 
        action='version', 
        version=adl2pydm.__version__)

    # TODO: control logging level
    # see: https://www.fun4jimmy.com/2015/09/15/configuring-pythons-logging-module-with-argparse.html

    return parser.parse_args()

def main():
    options = get_user_parameters()
    processFile(options.adlfile, options.dir)


if __name__ == "__main__":
    main()
