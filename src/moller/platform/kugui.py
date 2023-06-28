from .base import register_platform
from .base_pbs import BasePBS
from .utils import *

import logging
logger = logging.getLogger(__name__)

class Kugui(BasePBS):
    def __init__(self, info):
        super().__init__(info)

    def generate_header(self, fp):
        shebang = '#!/bin/bash\n'

        sched_key = '#PBS '

        sched_params = []
        sched_params.append('-q {}'.format(self.queue))
        sched_params.append('-l select={}:ncpus=128'.format(self.nnode))
        sched_params.append('-l walltime={}'.format(convert_seconds_to_hhmmss(self.elapsed)))
        if self.job_name is not None:
            sched_params.append('-N {}'.format(self.job_name))

        fp.write(shebang)
        fp.write('\n'.join([ sched_key + s for s in sched_params ]) + '\n')
        fp.write('\n')
        fp.write('export _debug=1')
        fp.write('\n')

    @classmethod
    def create(cls, info):
        return cls(info)

# for platform factory
register_platform("kugui", Kugui)

