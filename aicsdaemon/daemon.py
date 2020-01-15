#!/usr/bin/env python

from abc import ABC, abstractmethod
import atexit
import os
import sys
import time
from signal import SIGTERM

from .types import Pathlike


class Daemon(ABC):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile: Pathlike, stdin: Pathlike = None,
                 stdout: Pathlike = None, stderr: Pathlike = None, foreground: bool = False):
        # STDIN, STDOUT, STDERR, will eventually need to be redirected to /dev/null, making that clear here
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.foreground = foreground
        # file to hold the pid so the process can later be killed by pid
        self.pidfile = pidfile
        if stdin:
            open(stdin, 'w').close()  # create stdin or empty it, it will be opened for reading

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        """
        if not self.foreground:
            try:
                pid = os.fork()
                if pid > 0:
                    # exit first parent
                    sys.exit(0)
            except OSError as err:
                sys.stderr.write("fork #1 failed: %d (%s)\n" % (err.errno, err.strerror))
                sys.exit(1)

            # decouple from parent environment
            os.chdir("/")
            os.setsid()
            os.umask(0)

            # do second fork
            try:
                pid = os.fork()
                if pid > 0:
                    # exit from second parent
                    sys.exit(0)
            except OSError as err:
                sys.stderr.write("fork #2 failed: %d (%s)\n" % (err.errno, err.strerror))
                sys.exit(1)

        print(f"pid is {str(os.getpid())}")

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        self.isolate_daemon()

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())

        with open(self.pidfile, 'w+') as fp:
            fp.write("%s\n" % pid)

    def isolate_daemon(self):
        self._isolate_stream(self.stdin, sys.stdin, mode='r')
        self._isolate_stream(self.stdout, sys.stdout, mode='a+')
        self._isolate_stream(self.stderr, sys.stderr, mode='a+')

    @staticmethod
    def _isolate_stream(fname, sys_stream, mode: str):
        sobj = open(fname, mode=mode) if fname else os.devnull
        if fname:
            # replace sys_stream with the file stream
            if mode == 'r':
                sys_stream = sobj
            else:
                os.dup2(sobj.fileno(), sys_stream.fileno())
        else:
            sys_stream.close()

        return sys_stream

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()  # run should enter an unending loop
        self.stop()  # if the loop exits for some reason clean up the pidfile

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    @abstractmethod
    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        pass

