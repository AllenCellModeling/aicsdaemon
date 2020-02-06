import os
from datetime import datetime
from signal import SIGTERM
from time import sleep
from multiprocessing import Process, Queue

import pytest

from ..daemon import Daemon


class TestFgDaemon(Daemon):

    def __init__(self, data_dir, pidfile, logfile, fg=True):
        super(TestFgDaemon, self).__init__(pidfile=data_dir/pidfile,
                                           stdin=data_dir / "stdin",
                                           stdout=data_dir / "stdout",
                                           stderr=data_dir / "stderr",
                                           foreground=fg)
        print(f"logging to {logfile}")
        self.logfile = data_dir/logfile
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


def launch_daemon(q, data_dir):
    dm = TestFgDaemon(data_dir=data_dir, pidfile="pidfile", logfile="logfile", fg=True)
    dm.start()


def test_daemon_abc():
    """
    Since the Daemon class is an ABC it should raise an error if instantiated
    """
    with pytest.raises(TypeError):
        Daemon()


@pytest.fixture()
def daemon_launcher(data_dir):
    dm = TestFgDaemon(data_dir=data_dir, pidfile="pidfile", logfile="logfile", fg=True)
    #import subprocess
    #return subprocess.run(['my_example'], capture_output=True)
    return dm


def test_daemon_child(data_dir, daemon_launcher):
    pth = data_dir / "pidfile"
    if pth.exists():
        with open(str(pth), 'r') as pf:
            pid = int(pf.read().strip())
        try:
            os.kill(pid, SIGTERM)
        except OSError:
            pass
        os.remove(pth)


    dm_out = daemon_launcher
    dm_out.start()
    lines = 0
    with open(dm_out.logfile, "r") as fp:
        for i, l in enumerate(fp):
            pass
        lines = i+1
    assert lines > 1
    dm_out.stop()

