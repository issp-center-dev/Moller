from .base import register_platform
from .base_pbs import BasePBS
from .utils import *

import logging
logger = logging.getLogger(__name__)

class Pbs(BasePBS):
    def __init__(self, info):
        super().__init__(info)
        self.pbs_use_old_format = True
        # check
        if self.ncore is None:
            logger.error("number of cores per node not specified.")
            raise ValueError("number of cores per node not specified")

    @classmethod
    def create(cls, info):
        return cls(info)

# for platform factory
register_platform("pbs", Pbs)

