from datetime import datetime
import sys
from time import sleep

from .daemon import Daemon


class TestDaemon(Daemon):

    def __init__(self, data_dir, pidfile, logfile):
        super(TestDaemon, self).__init__(pidfile=pidfile,
                                         stdin=data_dir/".stdin",
                                         stdout=data_dir/".stdout",
                                         stderr=data_dir/".stderr")
        print(f"logging to {logfile}")
        self.logfile = logfile
        self._logfile = None
        self._cycle = 0

    def run(self):
        self._logfile = open(self.logfile, 'w+')
        self._logfile.write("opened logfile\n")
        self._logfile.flush()
        mtime = self.stdin.stat().st_mtime
        while mtime == self.stdin.stat().st_mtime:
            now = datetime.now()
            time = now.strftime("%S")
            if (self._cycle % 2) == 0:
                self._logfile.write(f"{self._cycle} -> {time}: even\n")
                self._logfile.flush()
            sleep(4)
            self._cycle += 1
        self._logfile.close()
        self._logfile = None


