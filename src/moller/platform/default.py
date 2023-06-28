from .base import Platform, register_platform
from .function import ScriptFunction
from .utils import *

import logging
logger = logging.getLogger(__name__)

class DefaultPlatform(Platform):
    def __init__(self, info):
        super().__init__(info)
        self.setup(info)

    def setup(self, info):
        self.queue = None
        self.node = info.get('node', 1)
        self.nnode = self.node[0] if type(self.node) is list else self.node
        self.job_name = info.get('job_name', '(noname)')

    def parallel_command(self, info):
        exec_command=r'mpiexec -np $_np -x OMP_NUM_THREADS=$_nc'
        return exec_command

    def generate_header(self, fp):
        shebang = '#!/bin/bash\n'
        fp.write(shebang)
        fp.write('\n')
        fp.write('export _debug=1\n')
        fp.write('\n')

    function_setup_taskenv = r"""
function _setup_taskenv () {
    :
}
export -f _setup_taskenv
    """

    def generate_function(self):
        flist = ScriptFunction.function_defs
        flist.append(self.function_setup_taskenv)
        flist.append(ScriptFunction.function_main)
        return ''.join(flist)
    
    @classmethod
    def create(cls, info):
        return cls(info)

# for platform factory
register_platform("default", DefaultPlatform)
