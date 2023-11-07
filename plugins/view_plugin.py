import LDS 
from LDS.utils import LOGGER, get_crash_message, PoolingTimer

class ViewPlugin(object):

    """Plugin to manage the LDS window dans transitions.
    """

    name = 'LDS-core:view'
    

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.count = 0
        self.forgotten = False
        # Seconds to display the failed message
        self.failed_view_timer = PoolingTimer(2)
        # Seconds between each animated frame
        self.animated_frame_timer = PoolingTimer(0)
        # Seconds before going back to the start
        self.choose_timer = PoolingTimer(30)
        # Seconds to display the selected layout
        self.layout_timer = PoolingTimer(4)
        # Seconds to display the selected layout
        self.print_view_timer = PoolingTimer(0)
        # Seconds to display the selected layout
        self.finish_timer = PoolingTimer(1)

    @LDS.hookimpl
    def state_failsafe_enter(self, win):
        win.show_oops()
        self.failed_view_timer.start()
        LOGGER.error(get_crash_message())

    @LDS.hookimpl
    def state_failsafe_validate(self):
        if self.failed_view_timer.is_timeout():
            return 'wait'
        
    @LDS.hookimpl
    def state_wait_enter(self, cfg, app, win):
        self.forgotten = False
        if app.previous_animated:
            previous_picture = next(app.previous_animated)
            # Reset timeout in case of settings changed
            self.animated_frame_timer.timeout = cfg.getfloat('WINDOW', 'animate_delay')
            self.animated_frame_timer.start()
        else:
            previous_picture = app.previous_picture

        win.show_intro(previous_picture, app.printer.is_ready()
                       and app.count.remaining_duplicates > 0)
        if app.printer.is_installed():
            win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())

    @LDS.hookimpl
    def state_wait_do(self, app, win, events):
        if app.previous_animated and self.animated_frame_timer.is_timeout():
            previous_picture = next(app.previous_animated)
            win.show_intro(previous_picture, app.printer.is_ready()
                           and app.count.remaining_duplicates > 0)
            self.animated_frame_timer.start()
        else:
            previous_picture = app.previous_picture

        event = app.find_print_status_event(events)
        if event and app.printer.is_installed():
            tasks = app.printer.get_all_tasks()
            win.set_print_number(len(tasks), not app.printer.is_ready())

        if app.find_print_event(events) or (win.get_image() and not previous_picture):
            win.show_intro(previous_picture, app.printer.is_ready()
                           and app.count.remaining_duplicates > 0)

