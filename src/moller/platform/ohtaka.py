from .base import register_platform
from .base_slurm import BaseSlurm
from .utils import *

import logging
logger = logging.getLogger(__name__)

class Ohtaka(BaseSlurm):
    def __init__(self, info):
        super().__init__(info)

    def parallel_command(self, info):
        #--- system dependent
        exec_command=r'srun --exclusive --mem-per-cpu=1840 -N $_nn -n $_np -c $_nc'
        return exec_command

    @classmethod
    def create(cls, info):
        return cls(info)

# for platform factory
register_platform("ohtaka", Ohtaka)
