#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This sample script will get deployed in the bin directory of the
users' virtualenv when the parent module is installed using pip.
"""

from pathlib import Path

from aicsdaemon import TestDaemon


def main():
    ddir = Path("~/Sandbox/Python/aicsdaemon/aicsdaemon/tests/data").expanduser().resolve()
    td = TestDaemon(data_dir=ddir, pidfile=ddir/".pidfile", logfile=ddir/".logfile")
    print("got daemon instance")
    td.start()
    print("started daemon")


###############################################################################
# Allow caller to directly run this module (usually in development scenarios)

if __name__ == '__main__':
    main()
