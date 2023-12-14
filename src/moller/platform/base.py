from .utils import *

import logging
logger = logging.getLogger(__name__)

class Platform:
    def __init__(self, info):
        pass

    def batch_queue_setup(self, info):
        if 'queue' not in info:
            msg = 'queue not specified'
            logger.error(msg)
            raise ValueError(msg)
        self.queue = info.get('queue', None)

        if 'node' not in info:
            msg = 'node not specified'
            logger.warning(msg)
        node = info.get('node', 1)

        if type(node) is list:
            if len(node) == 1:
                nnode, ncore = node[0], None
            elif len(node) == 2:
                nnode, ncore = node
            else:
                msg = 'invalid node parameter'
                logger.error(msg)
                raise ValueError(msg)
        else:
            nnode, ncore = int(node), None

        if 'core' in info:
            ncore = info.get('core')

        self.node = node
        self.nnode = nnode
        self.ncore = ncore

        if 'elapsed' not in info:
            msg = 'elapsed time not specified'
            logger.warning(msg)
        self.elapsed = convert_hhmmss_to_seconds(info.get('elapsed', '0'))

        if 'job_name' in info:
            self.job_name = info['job_name']
        else:
            self.job_name = None
        
    def generate(self, fp):
        pass

# platform factory
__platform_table = {}

def register_platform(platform_name: str, platform_class) -> None:
    if Platform not in platform_class.mro():
        raise TypeError("platform_class must be a subclass of Platform")
    __platform_table[platform_name.lower()] = platform_class

def create_platform(platform_name, info) -> Platform:
    if platform_name is None:
        raise ValueError(f"platform not specified")
    else:
        pn = platform_name.lower()
    if pn not in __platform_table:
        raise ValueError(f"Unknown platform: {platform_name}")
    platform_class = __platform_table[pn]
    return platform_class.create(info)
