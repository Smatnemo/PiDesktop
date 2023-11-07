
import os
import os.path as osp
import itertools
from datetime import datetime
import pibooth
from LDS.utils import LOGGER, PoolingTimer
# from LDS.pictures import get_picture_factory
from LDS.pictures.pool import PicturesFactoryPool

class PicturePlugin(object):
    """Plugin to build the final picture.
    """

    name = 'pibooth-core:picture'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.factory_pool = PicturesFactoryPool()
        self.picture_destroy_timer = PoolingTimer(0)
        self.second_previous_picture = None
        self.texts_vars = {}

    def _reset_vars(self, app):
        """Destroy final picture (can not be used anymore).
        """
        self.factory_pool.clear()
        app.previous_picture = None
        app.previous_animated = None
        app.previous_picture_file = None