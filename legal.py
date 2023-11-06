# To be moved to setup.py
import sys
import os
import multiprocessing
import argparse 
import logging

user = os.getlogin()
sys.path.append('/home/{}'.format(user))

import LDS
from LDS import language
from LDS.database import DataBase 
from LDS.utils import (LOGGER, PoolingTimer, configure_logging, get_crash_message,
                           set_logging_level, get_event_pos)
from LDS.view.window import PiWindow
from LDS.states import StatesMachine
from LDS.plugins import create_plugin_manager
from LDS.printer import PRINTER_TASKS_UPDATED, Printer



class PiApplication:

    def __init__(self):
       # Define states of the application
        self._machine = StatesMachine(self._pm, self._config, self, self._window)
        self._machine.add_state('videoplayback') # Add this state
        self._machine.add_state('wait')
        self._machine.add_state('beginsession') # Start - To do
        self._machine.add_state('login')
        self._machine.add_state('choose')
        self._machine.add_state('chosen')
        self._machine.add_state('preview')
        self._machine.add_state('capture')
        self._machine.add_state('showcapture') # work on showing the captured image
        self._machine.add_state('processing')
        self._machine.add_state('print')
        self._machine.add_state('finish')
        self._machine.add_state('reprint') # Add a reprint option and state.
        self._machine.add_state('endsession') # End the session

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
    config = PiConfigParser(osp.join(options.config_directory, "pibooth.cfg"), plugin_manager, not options.reset)

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