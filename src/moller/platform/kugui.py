from .base import register_platform
from .base_pbs import BasePBS
from .utils import *

import logging
logger = logging.getLogger(__name__)

class Kugui(BasePBS):
    def __init__(self, info):
        super().__init__(info)
        if self.ncore is None:
            self.ncore = 128  # default

    @classmethod
    def create(cls, info):
        return cls(info)

# for platform factory
register_platform("kugui", Kugui)

