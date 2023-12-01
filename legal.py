# To be moved to setup.py
import sys
import os
import os.path as osp
import multiprocessing
import argparse 
import logging
import pygame
import time
import tempfile
from warnings import filterwarnings


package_dir = osp.abspath(osp.dirname(__file__))

search_dir = osp.abspath(osp.dirname(package_dir))
print("Search Dir:", search_dir)
sys.path.append(search_dir)

print(sys.path)

from gpiozero import Device, ButtonBoard, LEDBoard, pi_info
from gpiozero.exc import BadPinFactory, PinFactoryFallback

import LDS
from LDS import language
from LDS.documents import initialize_documents_dirs
from LDS.database import DataBase 
from LDS.counters import Counters
from LDS.utils import (LOGGER, PoolingTimer, configure_logging, get_crash_message,
                           set_logging_level, get_event_pos)
from LDS.view.window import PiWindow
from LDS.view.documentsview import CHOSEEVENT
from LDS.view import LOGINEVENT
from LDS.states import StatesMachine
from LDS.plugins import create_plugin_manager
from LDS.printer import PRINTER_TASKS_UPDATED, PRINTEVENT, Printer
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

BACKBUTTON = pygame.USEREVENT + 17
NEXTBUTTON = pygame.USEREVENT + 18 

LOCKSCREEN = pygame.USEREVENT + 19

CAPTUREEVENT = pygame.USEREVENT + 21

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
        init_color = osp.join(LDS.package_dir,self.settings['background'])
        init_text_color = self._config.gettyped('WINDOW', 'text_color')
        if isinstance(init_color, str):
            if not osp.isfile(init_color):
                init_color = self._config.gettyped('WINDOW', 'background')
        elif not isinstance(init_color, (tuple, list)):
            init_color = self._config.getpath('WINDOW', 'background')
            # init_color = self.settings['backgroundpath']

        title = 'Legal v{}'.format(LDS.__version__)
        
        logo_path = osp.join(LDS.package_dir,self.settings['watermarkpath'])

        img = pygame.image.load(logo_path)
        if not isinstance(init_size, str):
            self._window = PiWindow(title, init_size, color=init_color,
                                    text_color=init_text_color, debug=init_debug, app_icon = img)
        else:
            self._window = PiWindow(title, color=init_color,
                                    text_color=init_text_color, debug=init_debug, app_icon = img)
        self._menu = None
        self._multipress_timer = PoolingTimer(config.getfloat('CONTROLS', 'multi_press_delay'), False)
        self._fingerdown_events = []
       # Define states of the application
        self._machine = StatesMachine(self._pm, self._config, self, self._window)
        self._machine.add_state('wait')
        self._machine.add_state('login')
        self._machine.add_state('choose') # This state should be used to choose documents
        self._machine.add_state('chosen') # This state should be used after document has been chosen
        self._machine.add_state('decrypt') # State similar to login for decrypting documents
        self._machine.add_state('preview') # This state should be used to see the chosen document
        self._machine.add_state('capture') # This state should is either for capturing signature or image to prove that the document has been received
        self._machine.add_state('processing')
        self._machine.add_state('print')# This state should be used to print document instead
        self._machine.add_state('finish')
        self._machine.add_state('lock') # log out 
        self._machine.add_state('passfail')

        # State to return to after screen is locked and logged back into
        self.previous_state = None

        # Variables shared with plugins
        # Change them may break plugins compatibility
        self.capture_nbr = 1
        self.capture_date = None
        self.capture_choices = (4, 1)

        self.inmate_number = None
        self.chosen_document = None
        self.document_row = None
        self.documents = self.settings['inmate_documents']
        self.previous_picture = None
        self.previous_animated = None
        self.previous_picture_file = None

        self.password = ''
        self.validated = None 
        self.update_needed = None
        self.decrypt_key = None
        self.decrypted_file = None
        self.print_job = None
        self.picture_name = None
        # Get count from data base
        if self.settings['attempt_count']:
            self.attempt_count = self.settings['attempt_count']
        else:
            self.attempt_count = 3

        self.count = Counters(self._config.join_path("counters.pickle"),
                              taken=0, printed=0, forgotten=0,
                              remaining_duplicates=self._config.getint('PRINTER', 'max_duplicates'))
        
        try:
            if self.settings['use_camera']:
                self.camera = self._pm.hook.lds_setup_camera(cfg=self._config)
        except Exception as ex:
            LOGGER.error("Camera could not be set up: {}".format(ex))
            self.settings['use_signature'] = True
            pass
        try: 
            if self.settings['use_signature']:
                self.capture_signature = None 
        except Exception as ex:
            LOGGER.error("Signature functionality could not be set up: {}".format(ex))
            pass 

        self.leds = LEDBoard(capture="BOARD" + config.get('CONTROLS', 'picture_led_pin'),
                             printer="BOARD" + config.get('CONTROLS', 'print_led_pin'))

        self.printer = Printer(config.get('PRINTER', 'printer_name'),
                               config.getint('PRINTER', 'max_pages'),
                               config.gettyped('PRINTER', 'printer_options'),
                               self.count)

    def _initialize(self):
        self.printer.max_pages = self._config.getint('PRINTER', 'max_pages')

    @property
    def picture_filename(self):
        """Return the final picture file name.
        """
        if not self.picture_name:
            raise EnvironmentError("The 'picturename' attribute is not set yet")
        return "{}_.jpg".format(self.picture_name)  
    
    def convertToBinaryData(self, filename):
        # Convert digital data to binary format
        with open(filename, 'rb') as file:
            blobData = file.read()
        return blobData

    def print_event(self):
        pygame.event.post(pygame.event.Event(PRINTEVENT))
     
    def find_quit_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.QUIT:
                return event
        return None

    def find_resize_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                return event
        return None

    def find_fullscreen_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and \
                    event.key == pygame.K_f and pygame.key.get_mods() & pygame.KMOD_CTRL:
                return event
        return None
    
    def find_screen_event(self, events):
        """
        Should only be used in wait state to activate login state
        """
        for event in events:
            if event.type == pygame.FINGERDOWN:
                print('pygame.FINGERDOWN')
                return event 
            if event.type == pygame.FINGERUP:
                print('pygame.FINGERUP')
                return event
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return event
        return None
        
    def find_login_event(self, events):
        for event in events:
            if event.type == LOGINEVENT:
                return event
        return None

            
    def find_lockscreen_event(self, events):
        for event in events:
            if event.type == LOCKSCREEN:
                return event
        return None

    def find_print_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == PRINTEVENT:
                return event
        return None
    
    def find_print_status_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == PRINTER_TASKS_UPDATED:
                return event
        return None    
    
    def find_settings_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return event
            if event.type == BUTTONDOWN and event.capture and event.printer:
                return event
            if event.type == pygame.FINGERDOWN:
                # Press but not release
                self._fingerdown_events.append(event)
            if event.type == pygame.FINGERUP:
                # Resetting touch_events
                self._fingerdown_events = []
            if len(self._fingerdown_events) > 3:
                # 4 fingers on the screen trigger the menu
                self._fingerdown_events = []
                return pygame.event.Event(BUTTONDOWN, capture=1, printer=1,
                                          button=self.buttons)
        return None
    
    def find_choice_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                return event
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                return event
            if (event.type == pygame.MOUSEBUTTONUP and event.button in (1, 2, 3)) or event.type == pygame.FINGERUP:
                pos = get_event_pos(self._window.display_size, event)
                rect = self._window.get_rect()
                if pygame.Rect(0, 0, rect.width // 2, rect.height).collidepoint(pos):
                    event.key = pygame.K_LEFT
                else:
                    event.key = pygame.K_RIGHT
                return event
            if event.type == BUTTONDOWN:
                if event.capture:
                    event.key = pygame.K_LEFT
                else:
                    event.key = pygame.K_RIGHT
                return event
        return None
    
    def find_choose_event(self, events):
        for event in events:
            if event.type == CHOSEEVENT:
                return event
        return None
    
    def find_next_back_event(self, events):
        for event in events:
            if event.type == BACKBUTTON:
                return event
            if event.type == NEXTBUTTON:
                return event 
        return None 

    def find_capture_event(self, events):
        """Return the first found event if found in the list.
        """
        for event in events:
            if event.type == BUTTONDOWN and event.capture:
                return event
            if event.type == CAPTUREEVENT:
                return event
        return None
        
    def main_loop(self):
        try:
            fps = 40
            clock = pygame.time.Clock()
            self._initialize()
            self._pm.hook.lds_startup(cfg=self._config, app=self)
            self._machine.set_state('wait')
            self.previous_state = 'wait'

            start = True
            
            while start:
                events = list(pygame.event.get())

                if self.find_quit_event(events):
                    break 

                if self.find_fullscreen_event(events):
                    self._window.toggle_fullscreen()

                event = self.find_resize_event(events)
                if event:
                    self._window.resize(event.size)
                # For keypad
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN or event.type==pygame.MOUSEMOTION or event.type==pygame.MOUSEBUTTONUP: 
                        self.update_needed = event
                    else:
                        self.update_needed = None

                if not self._menu and self.find_settings_event(events):
                    self.camera.stop_preview()
                    self.leds.off()
                    self._menu = PiConfigMenu(self._pm, self._config, self, self._window)
                    self._menu.show()
                    self.leds.blink(on_time=0.1, off_time=1)
                elif self._menu and self._menu.is_shown():
                    self._menu.process(events)
                elif self._menu and not self._menu.is_shown():
                    self.leds.off()
                    self._initialize()
                    self._machine.set_state('wait')
                    self.start = time.time()
                    self._menu = None
                else:
                    self._machine.process(events)
                # self._machine.process(events)

                pygame.display.update()
                clock.tick(fps)                
        except Exception as ex:
            # Log error
            LOGGER.error(str(ex), exc_info=True)
            # Get crash message
            LOGGER.error(get_crash_message())
        finally:
            if self.settings['use_camera']:
                self._pm.hook.lds_cleanup(app=self)
            pygame.quit()


def main():
    """Application entry point.
    """
    if hasattr(multiprocessing, 'set_start_method'):
        # Avoid use 'fork': safely forking a multithreaded process is problematic
        multiprocessing.set_start_method('spawn')

    parser = argparse.ArgumentParser(usage="%(prog)s [options]", description=LDS.__doc__)

    parser.add_argument("config_directory", nargs='?', default="~/.config/LDS",
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
        filename = osp.join(tempfile.gettempdir(), 'lds.log')
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
    plugin_manager.hook.lds_configure(cfg=config)

    # Initializing documents directory
    initialize_documents_dirs()

    # Ensure config files are present in case of first pibooth launch
    if not options.reset:
        if not osp.isfile(config.filename):
            config.save(default=True)
        plugin_manager.hook.lds_reset(cfg=config, hard=False)

    if options.config:
        LOGGER.info("Editing the LDS configuration...")
        config.edit()
    elif options.translate:
        LOGGER.info("Editing the GUI translations...")
        language.edit()
    elif options.reset:
        config.save(default=True)
        plugin_manager.hook.lds_reset(cfg=config, hard=True)
    else:
        LOGGER.info("Starting the LDS application %s", GPIO_INFO)
        app = PiApplication(config, plugin_manager)
        app.main_loop()



if __name__ == "__main__":
    main()