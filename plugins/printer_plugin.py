import LDS 
from LDS.utils import LOGGER 


class PrinterPlugin(object):


    """Plugin to manage the printer.
    """

    name = 'LDS-core:printer'

    def __init__(self, plugin_manager):
        self._pm = plugin_manager

    def print_picture(self, cfg, app):
        LOGGER.info("Send final picture to printer")
        app.printer.print_file(app.previous_picture_file,
                               cfg.getint('PRINTER', 'pictures_per_page'))
        app.count.printed += 1
        app.count.remaining_duplicates -= 1

    def print_document(self, cfg, app):
        LOGGER.info("Send final document to printer")
        app.printer.print_file(app.print_job.name)
        app.count.printed += 1
        app.count.remaining_duplicates -= 1
    
    @LDS.hookimpl
    def lds_cleanup(self, app):
        app.printer.quit()

    @LDS.hookimpl
    def state_failsafe_enter(self, cfg, app):
        """Reset variables set in this plugin.
        """
        app.count.remaining_duplicates = cfg.getint('PRINTER', 'max_duplicates')

    @LDS.hookimpl
    def state_wait_do(self, cfg, app, events):
        """Find printer information
        """

    @LDS.hookimpl
    def state_processing_enter(self, cfg, app):
        app.count.remaining_duplicates = cfg.getint('PRINTER', 'max_duplicates')

    @LDS.hookimpl
    def state_processing_do(self, cfg, app):
        if app.previous_picture_file and app.printer.is_ready():
            number = cfg.gettyped('PRINTER', 'auto_print')
            if number == 'max':
                number = cfg.getint('PRINTER', 'max_duplicates')
            for i in range(number):
                if app.count.remaining_duplicates > 0:
                    self.print_picture(cfg, app)

    @LDS.hookimpl
    def state_print_do(self, cfg, app, events):
        self.print_job_status = None
        if app.find_print_event(events) and app.print_job:
            self.print_document(cfg, app)