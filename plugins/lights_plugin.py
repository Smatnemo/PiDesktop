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
            #app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
            pass
        else:
            #app.leds.capture.blink(on_time=self.blink_time, off_time=self.blink_time)
            #app.leds.printer.off()
            pass

    @LDS.hookimpl
    def state_wait_do(self, app, events):
        if app.find_print_event(events) and app.previous_picture_file and app.printer.is_ready():
            if app.count.remaining_duplicates <= 0:
                #app.leds.printer.off()
                pass
            else:
                #app.leds.printer.on()
                time.sleep(1)  # Just to let the LED switched on
               # app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
                pass

        #if not app.previous_picture_file and app.leds.printer._controller:  # _controller == blinking
            #app.leds.printer.off()

    @LDS.hookimpl
    def state_wait_exit(self, app):
        #app.leds.off()
        pass

    @LDS.hookimpl
    def state_choose_enter(self, app):
        #app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        pass

    @LDS.hookimpl
    def state_choose_exit(self, app):
        if app.capture_nbr == app.capture_choices[0]:
            #app.leds.capture.on()
            #app.leds.printer.off()
            pass
        elif app.capture_nbr == app.capture_choices[1]:
            #app.leds.printer.on()
            #app.leds.capture.off()
            pass

    @LDS.hookimpl
    def state_chosen_exit(self, app):
        #app.leds.off()
        pass

    @LDS.hookimpl
    def state_print_enter(self, app):
        #app.leds.blink(on_time=self.blink_time, off_time=self.blink_time)
        pass

    @LDS.hookimpl
    def state_print_do(self, app, events):
        if app.find_print_event(events):
            #app.leds.printer.on()
            #app.leds.capture.off()
            pass

    @LDS.hookimpl
    def state_finish_enter(self, app):
        #app.leds.off()
        pass
