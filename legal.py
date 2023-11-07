# To be moved to setup.py
import sys
import os
import os.path as osp
import multiprocessing
import argparse 
import logging
import pygame
import tempfile
from warnings import filterwarnings

user = os.getlogin()
sys.path.append('/home/{}'.format(user))


from gpiozero import Device, ButtonBoard, LEDBoard, pi_info
from gpiozero.exc import BadPinFactory, PinFactoryFallback

import LDS
from LDS import language
from LDS.database import DataBase 
from LDS.utils import (LOGGER, PoolingTimer, configure_logging, get_crash_message,
                           set_logging_level, get_event_pos)
from LDS.view.window import PiWindow
from LDS.states import StatesMachine
from LDS.plugins import create_plugin_manager
from LDS.printer import PRINTER_TASKS_UPDATED, Printer
from LDS.config import PiConfigParser, PiConfigMenu

# Try importing pyvidplayer2
try: 
    from LDS.videoplayer import VideoPlayer, Video
    print("imported pyvideoplayer successfully!")
except ImportError:
    print("Could not Import videoplayer")  
    pass
# Set the default pin factory to a mock factory if pibooth is not started a Raspberry Pi
try:
    filterwarnings("ignore", category=PinFactoryFallback)
    GPIO_INFO = "on Raspberry pi {0}".format(pi_info().model)
except BadPinFactory:
    from gpiozero.pins.mock import MockFactory
    Device.pin_factory = MockFactory()
    GPIO_INFO = "without physical GPIO, fallback to GPIO mock"


BUTTONDOWN = pygame.USEREVENT + 1


class PiApplication:

    def __init__(self, config, plugin_manager):
        self._pm = plugin_manager
        self._config = config

        # Experiment with database module
        self.db = DataBase()
        self.db._initialize_app_settings()
        self.settings = self.db.settings

        # Create window of (width, height)
        init_size = self._config.gettyped('WINDOW', 'size')
        init_debug = self._config.getboolean('GENERAL', 'debug')
        # init_color = self._config.gettyped('WINDOW', 'background')
        init_color = self.settings['background']
        init_text_color = self._config.gettyped('WINDOW', 'text_color')
        if isinstance(init_color, str):
            if not osp.isfile(init_color):
                init_color = self._config.gettyped('WINDOW', 'background')
        elif not isinstance(init_color, (tuple, list)):
            init_color = self._config.getpath('WINDOW', 'background')
            # init_color = self.settings['backgroundpath']

        title = 'Pibooth v{}'.format(LDS.__version__)
        img = pygame.image.load(self.settings['watermarkpath'])
        if not isinstance(init_size, str):
            self._window = PiWindow(title, init_size, color=init_color,
                                    text_color=init_text_color, debug=init_debug, app_icon = img)
        else:
            self._window = PiWindow(title, color=init_color,
                                    text_color=init_text_color, debug=init_debug, app_icon = img)

       # Define states of the application
        self._machine = StatesMachine(self._pm, self._config, self, self._window)
        self._machine.add_state('wait')
        self._machine.add_state('login')
        self._machine.add_state('choose')
        self._machine.add_state('chosen')
        self._machine.add_state('preview')
        self._machine.add_state('capture')
        self._machine.add_state('processing')
        self._machine.add_state('print')
        self._machine.add_state('finish')
        self._machine.add_state('logout') # log out 

    def _initialize(self):
        print(self._machine.states)
        

    def main_loop(self):
        try:
            self._initialize()
        except Exception as e:
            # Log error
            LOGGER.error()
            # Get crash message
            LOGGER.error()
        finally:
            pass


def main():
    """Application entry point.
    """
    if hasattr(multiprocessing, 'set_start_method'):
        # Avoid use 'fork': safely forking a multithreaded process is problematic
        multiprocessing.set_start_method('spawn')

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=LDS.__doc__)

    parser.add_argument("config_directory", nargs='?', default="~/.config/pibooth",
                        help=u"path to configuration directory (default: %(default)s)")

    parser.add_argument('--version', action='version', version=LDS.__version__,
                        help=u"show program's version number and exit")

    parser.add_argument("--config", action='store_true',
                        help=u"edit the current configuration and exit")

    parser.add_argument("--translate", action='store_true',
                        help=u"edit the GUI translations and exit")

    parser.add_argument("--reset", action='store_true',
                        help=u"restore the default configuration/translations and exit")

    parser.add_argument("--nolog", action='store_true', default=False,
                        help=u"don't save console output in a file (avoid filling the /tmp directory)")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", dest='logging', action='store_const', const=logging.DEBUG,
                       help=u"report more information about operations", default=logging.INFO)
    group.add_argument("-q", "--quiet", dest='logging', action='store_const', const=logging.WARNING,
                       help=u"report only errors and warnings", default=logging.INFO)

    options = parser.parse_args()

    if not options.nolog:
        filename = osp.join(tempfile.gettempdir(), 'pibooth.log')
    else:
        filename = None
    configure_logging(options.logging, '[ %(levelname)-8s] %(name)-18s: %(message)s', filename=filename)

    plugin_manager = create_plugin_manager()

    # Load the configuration
    config = PiConfigParser(osp.join(options.config_directory, "LDS.cfg"), plugin_manager, not options.reset)

    # Register plugins
    plugin_manager.load_all_plugins(config.gettuple('GENERAL', 'plugins', 'path'),
                                    config.gettuple('GENERAL', 'plugins_disabled', str))
    LOGGER.info("Installed plugins: %s", ", ".join(
        [plugin_manager.get_friendly_name(p) for p in plugin_manager.list_external_plugins()]))

    # Load the languages
    language.init(config.join_path("translations.cfg"), options.reset)

    # Update configuration with plugins ones
    plugin_manager.hook.pibooth_configure(cfg=config)

    # Ensure config files are present in case of first pibooth launch
    if not options.reset:
        if not osp.isfile(config.filename):
            config.save(default=True)
        plugin_manager.hook.pibooth_reset(cfg=config, hard=False)

    if options.config:
        LOGGER.info("Editing the pibooth configuration...")
        config.edit()
    elif options.translate:
        LOGGER.info("Editing the GUI translations...")
        language.edit()
    elif options.reset:
        config.save(default=True)
        plugin_manager.hook.pibooth_reset(cfg=config, hard=True)
    else:
        LOGGER.info("Starting the photo booth application %s", GPIO_INFO)
        app = PiApplication(config, plugin_manager)
        app.main_loop()



if __name__ == "__main__":
    main()