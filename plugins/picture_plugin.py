
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

    @pibooth.hookimpl(hookwrapper=True)
    def pibooth_setup_picture_factory(self, cfg, opt_index, factory):

        outcome = yield  # all corresponding hookimpls are invoked here
        factory = outcome.get_result() or factory

        factory.set_margin(cfg.getint('PICTURE', 'margin_thick'))

        backgrounds = cfg.gettuple('PICTURE', 'backgrounds', ('color', 'path'), 2)
        factory.set_background(backgrounds[opt_index])

        overlays = cfg.gettuple('PICTURE', 'overlays', 'path', 2)
        if overlays[opt_index]:
            factory.set_overlay(overlays[opt_index])

        texts = [cfg.get('PICTURE', 'footer_text1').strip('"').format(**self.texts_vars),
                 cfg.get('PICTURE', 'footer_text2').strip('"').format(**self.texts_vars)]
        colors = cfg.gettuple('PICTURE', 'text_colors', 'color', len(texts))
        text_fonts = cfg.gettuple('PICTURE', 'text_fonts', str, len(texts))
        alignments = cfg.gettuple('PICTURE', 'text_alignments', str, len(texts))
        if any(elem != '' for elem in texts):
            for params in zip(texts, text_fonts, colors, alignments):
                factory.add_text(*params)

        if cfg.getboolean('PICTURE', 'captures_cropping'):
            factory.set_cropping()

        if cfg.getboolean('GENERAL', 'debug'):
            factory.set_outlines()

        outcome.force_result(factory)