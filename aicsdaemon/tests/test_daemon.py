import os
from datetime import datetime
from signal import SIGTERM
from time import sleep

import pytest

from ..daemon import Daemon
from ..example_child import TestDaemon


def test_daemon_abc():
    """
    Since the Daemon class is an ABC it should raise an error if instantiated
    """
    with pytest.raises(TypeError):
        Daemon()


@pytest.fixture()
def daemon_launcher():
    import subprocess
    return subprocess.run(['my_example'], capture_output=True)


def test_daemon_child(data_dir, daemon_launcher):
    pth = data_dir/".pidfile"
    if pth.exists():
        with open(str(pth), 'r') as pf:
            pid = int(pf.read().strip())
        try:
            os.kill(pid, SIGTERM)
        except OSError:
            pass
        os.remove(pth)

    dm_out = daemon_launcher

    assert True

