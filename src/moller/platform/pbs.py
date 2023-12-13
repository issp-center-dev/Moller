from .base import register_platform
from .base_pbs import BasePBS
from .utils import *

import logging
logger = logging.getLogger(__name__)

class Pbs(BasePBS):
    def __init__(self, info):
        super().__init__(info)

    @classmethod
    def create(cls, info):
        return cls(info)

# for platform factory
register_platform("pbs", Pbs)

