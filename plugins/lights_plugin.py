import time 
import LDS

class LightsPlugin(object):


    name = "LDS-core:lights"

    def __init__(self,plugin_manager):
        self._pm = plugin_manager
        self.blink_time = 0.3
    
    @LDS.hookimpl
    def state_wait_enter(self, app):
        if app.previous_picture_file and app.printer.is_ready()\
                and app.count.remaining_duplicates > 0:
            app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        else:
            app.leds.capture.blink(on_time=self.blink_time, off_time=self.blink_time)
            app.leds.printer.off()
    