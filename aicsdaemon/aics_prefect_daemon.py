from dask_jobqueue import SLURMCluster
import dask, dask.distributed
from time import sleep

from .daemon import Daemon


class AicsPrefectDaemon(Daemon):

    def __init__(self, data_dir, pidfile, logfile):
        super(AicsPrefectDaemon, self).__init__(pidfile=data_dir/pidfile,
                                                stdout=data_dir/".stdout",
                                                stdin=data_dir/".stdin",
                                                stderr=data_dir/".stderr")

        print(f"logging to {data_dir/logfile}")
        self.logfile = data_dir/logfile
        self._logfile = None
        self._cycle = 0

    def run(self):
        self._logfile = open(self.logfile, 'w+')
        self._logfile.write("opened logfile\n")
        self._logfile.flush()

        cluster = SLURMCluster(cores=2, memory="8GB", walltime="01:00:00", queue="aics_cpu_general")
        cluster.adapt(minimum_jobs=2, maximum_jobs=40)
        client = dask.distributed.Client(cluster)

        self._logfile.write(f"{cluster.scheduler_info['address']}\n")
        self._logfile.write(f"{cluster.scheduler_info['services']['dashboard']}\n")
        self._logfile.flush()

        # this enables us to put something in stdin and if so this loop will
        # exit. Thus using the stdin="filepath" argument gives us a clean way to
        # shutdown the process
        mtime = self.stdin.stat().st_mtime
        while mtime == self.stdin.stat().st_mtime:
            sleep(10)

        self._logfile.close()
        self._logfile = None

