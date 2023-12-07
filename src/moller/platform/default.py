from .base import Platform, register_platform
from .base_default import BaseDefault
from .function import ScriptFunction
from .utils import *

import logging
logger = logging.getLogger(__name__)

class DefaultPlatform(BaseDefault):
    def __init__(self, info):
        super().__init__(info)
        self.setup(info)

    def setup(self, info):
        self.queue = None
        node = info.get('node', 1)
        core = info.get('core', 0)

        self.nnode = node[0] if type(node) is list else node
        if core > 0:
            self.ncore = core
        elif type(node) is list and len(node)>1:
            self.ncore = node[1]
        else:
            self.ncore = 0

        self.node = node
        self.job_name = info.get('job_name', '(noname)')

    def parallel_command(self, info):
        exec_command=r'mpiexec -np $_np -x OMP_NUM_THREADS=$_nc'
        return exec_command

    def generate_header(self, fp):
        super().generate_header(fp)

    def generate_function(self):
        return super().generate_function()
    
    @classmethod
    def create(cls, info):
        return cls(info)

# for platform factory
register_platform("default", DefaultPlatform)
