
"""LDS configuration.
"""

import io
import ast
import os
import os.path as osp
import itertools
import inspect
from configparser import RawConfigParser
from collections import OrderedDict as odict
from LDS.utils import LOGGER, open_text_editor
from LDS import language

class PiConfigParser(object):
    
    def __init__(self,):
        pass