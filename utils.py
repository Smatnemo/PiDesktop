"""
LDS utilities
"""

import sys 
import os 
import time 
import os.path as osp 
import logging 
import psutil
import platform
from fnmatch import fnmatchcase
import contextlib 
import errno
import subprocess
import pygame 

LOGGER = logging.getLogger("LDS")

class BlockConsoleHandler(logging.StreamHandler):

    default_level = logging.INFO 
    pattern_indent = '+< '
    pattern_blocks = '| '
    pattern_dedent = '+> '
    current_indent = ''

    def emit(self, record):
        cls = self.__class__
        if cls.is_debug():
            record.msg = '{}{}'.format(cls.current_indent, record.msg)
            # print('This is emit')
        logging.StreamHandler.emit(self, record)
    
    @classmethod
    def is_debug(cls)->bool:
        """
        Return True if handler is set to DEBUG
        """
        for hdlr in logging.getLogger().handlers:
            if isinstance(hdlr, cls):
                return hdlr.level < logging.INFO
        return False
    
    @classmethod
    def indent(cls)->None:
        """
        Begin a new log block
        """
        if cls.is_debug():
            cls.current_indent += cls.pattern_indent

    @classmethod 
    def dedent(cls)->None:
        """
        End the current log block
        """
        if cls.is_debug():
            cls.current_indent = (cls.current_indent[:-len(cls.pattern_blocks)] + cls.pattern_dedent)


def load_module(path):
    """
    Load a python module dynamically
    """
    if not osp.isfile(path):
        raise ValueError("Invalid Python module path '{}'".format(path))
    
    dirname, filename = osp.split(path)
    modname = osp.splitext(filename)[0]

    if dirname not in sys.path:
        sys.path.append(dirname)
    
    for hook in sys.meta_path:
        if hasattr(hook, 'find_module'):
            loader = hook.find_module(modname, [dirname])
            if loader:
                return loader.load_module(modname)
        else: 
            spec = hook.find_spec(modname, [dirname])
            if spec:
                return spec.loader.load_module(modname)
    
    LOGGER.warning("Can not load Python module '%s' from '%s'", modname, path)

def get_event_pos(display_size, event)->tuple:
    """
    Return a tuple with the position along the width and height of the display
    :param display_size: the display dimensions of the screen 
    :param event: pygame event object
    """
    if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
        finger_pos = (event.x * display_size[0], event.y * display_size[1])
        return finger_pos
    return event.pos

