import LDS 
from LDS.utils import LOGGER 


class PrinterPlugin(object):
    pass


    """Plugin to manage the printer.
    """

    name = 'pibooth-core:printer'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager

    def print_picture(self, cfg, app):
        LOGGER.info("Send final picture to printer")
        app.printer.print_file(app.previous_picture_file,
                               cfg.getint('PRINTER', 'pictures_per_page'))
        app.count.printed += 1
        app.count.remaining_duplicates -= 1

    @LDS.hookimpl
    def pibooth_cleanup(self, app):
        app.printer.quit()

    @LDS.hookimpl
    def state_failsafe_enter(self, cfg, app):
        """Reset variables set in this plugin.
        """
        app.count.remaining_duplicates = cfg.getint('PRINTER', 'max_duplicates')
