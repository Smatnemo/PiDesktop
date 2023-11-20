import LDS 
from LDS.utils import LOGGER, get_crash_message, PoolingTimer
from LDS.accounts import LogIn, LogOut
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

        self.login_view = None 
        self.decrypt_view = None

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

    @LDS.hookimpl
    def state_wait_validate(self, cfg, app, events):
        if app.find_screen_event(events):
            return 'login'
        if app.find_capture_event(events):
            if len(app.capture_choices) > 1:
                return 'choose'
            if cfg.getfloat('WINDOW', 'chosen_delay') > 0:
                return 'chosen'
            return 'preview'

    @LDS.hookimpl
    def state_wait_exit(self, win):
        self.count = 0
        win.show_image(None)  # Clear currently displayed image

    @LDS.hookimpl
    def state_login_enter(self, win):
        LOGGER.info("Attempting to Login")
        # win.surface.fill((255,255,255))
        self.login_view = win.show_login() # Create a function in window module to display login page
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        # Find way to display it in the login window during login in activity
        self.choose_timer.start()
        
    @LDS.hookimpl
    def state_login_do(self, app, win, events):
        if events:
            self.choose_timer.start()
        if app.find_login_event(events):
            if self.login_view.passcode_box.input_text != '':
                app.password = self.login_view.passcode_box.input_text 
            else:
                app.password = self.login_view.get_input_text() 
            self.login_view.passcode_box.text=''
            self.login_view.passcode_box.txt_surface = self.login_view.passcode_box.font.render(self.login_view.passcode_box.text, True, self.login_view.passcode_box.color)
            # print('From Login',app.password) 
        # win.surface.fill((255, 255, 255))
        self.login_view.update_needed = app.update_needed
        self.login_view.passcode_box.handle_event(events)
        self.login_view.draw(win.surface)
        
        

    @LDS.hookimpl 
    def state_login_validate(self, cfg, app, win, events):
        # Create a way to validate username and password
        if app.find_login_event(events):
            # print('From Validate do',app.password)
            LOGGER.info("Attempting to validate password")
            login = LogIn()
            app.validated = login.authenticate(app.password)
            LOGGER.info(app.validated)
            if app.validated:
                app.validated = None
                return 'choose'
            # Write code to return to previous state if the last state was not choose
        elif self.choose_timer.is_timeout():    
            return 'wait'

        
    @LDS.hookimpl 
    def state_login_exit(self, win):
        self.count = 0
        win.show_image(None) # Clear currently displayed image

# Default original
    # @LDS.hookimpl
    # def state_choose_enter(self, app, win):
    #     LOGGER.info("Show picture choice (nothing selected)")
    #     win.set_print_number(0, False)  # Hide printer status
    #     win.show_choice(app.capture_choices)
    #     self.choose_timer.start()

    # @LDS.hookimpl
    # def state_choose_validate(self, cfg, app):
    #     if app.capture_nbr:
    #         if cfg.getfloat('WINDOW', 'chosen_delay') > 0:
    #             return 'chosen'
    #         else:
    #             return 'preview'
    #     elif self.choose_timer.is_timeout():
    #         return 'wait'

    @LDS.hookimpl
    def state_choose_enter(self, app, win):
        LOGGER.info("Show document choice (nothing selected)")
        win.set_print_number(0, False)  # Hide printer status
        # Create logic to fetch documents from database
        win.show_choices(app.documents)
        self.choose_timer.start()

    @LDS.hookimpl
    def state_choose_do(self, app, win, events):
        if events:
            # If there is any event restart timer
            LOGGER.info("Restarting timer in choose state")
            self.choose_timer.start()

        win._current_documents_foreground.inmate_documents_view.update_needed = app.update_needed
        win.show_choices(app.documents)

        # update for backbutton
        win._current_background.backbutton.draw(app.update_needed)
        win._current_background.lockbutton.draw(app.update_needed)

        event = app.find_choose_event(events)
        if event:
            app.inmate_number = win._current_documents_foreground.inmate_documents_view.choseninmaterow.inmate_number
   
    @LDS.hookimpl
    def state_choose_validate(self, cfg, app, events):
        if app.find_next_back_event(events):
            return 'login'
        elif app.find_lockscreen_event(events):
            return 'wait'
        elif app.inmate_number:
            return 'chosen'
        elif self.choose_timer.is_timeout():
            # once the time is reached return to wait state
            return 'wait'
        

    @LDS.hookimpl
    def state_choose_exit(self, app):
        # app.inmate_number = None
        pass
        

    @LDS.hookimpl
    def state_chosen_enter(self, cfg, app, win):
        LOGGER.info("Show chosen inmate document choice (inmate %s selected)", app.inmate_number)
        win.show_choices(app.documents, selected=app.inmate_number)
        # Reset timeout in case of settings changed
        self.choose_timer.start()

    @LDS.hookimpl
    def state_chosen_do(self, app, win, events):
        if events:
            # If there is any event restart timer
            LOGGER.info("Restarting timer in chosen state")
            self.choose_timer.start()

        win._current_documents_foreground.document_view.update_needed = app.update_needed
        win.show_choices(app.documents, selected=app.inmate_number)

        # update for backbutton
        win._current_background.backbutton.draw(app.update_needed)
        win._current_background.lockbutton.draw(app.update_needed)

        event = app.find_choose_event(events)
        if event:
            app.chosen_document = win._current_documents_foreground.document_view.chosendocumentrow.document

    @LDS.hookimpl
    def state_chosen_validate(self, app, win, events):
        if app.find_next_back_event(events):
            app.inmate_number = None
            app.chosen_document = None
            # Drop cached foreground
            win.documents_foreground = {}
            return 'choose'
        elif app.find_lockscreen_event(events):
            return 'wait'
        elif app.chosen_document:
            return 'decrypt'
        elif self.choose_timer.is_timeout():
            return 'wait'
        
        
    @LDS.hookimpl
    def state_chosen_exit(self, app):
        # Exit the chosen state
        pass


    @LDS.hookimpl
    def state_decrypt_enter(self, win):
        LOGGER.info("Entered the decrypt state")
        # win.surface.fill((255,255,255))
        self.decrypt_view = win.show_decrypt() # Create a function in window module to display login page
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        # Find way to display it in the login window during login in activity
        self.choose_timer.start()

    @LDS.hookimpl
    def state_decrypt_do(self, app, win, events):
        if events:
            self.choose_timer.start()
        if app.find_login_event(events):
            if self.decrypt_view.passcode_box.input_text != '':
                app.decrypt_key = self.decrypt_view.passcode_box.input_text 
            else:
                app.decrypt_key = self.decrypt_view.get_input_text() 
            self.decrypt_view.passcode_box.text=''
            self.decrypt_view.passcode_box.txt_surface = self.decrypt_view.passcode_box.font.render(self.decrypt_view.passcode_box.text, True, self.decrypt_view.passcode_box.color)
            # print('From Login',app.password) 
        # win.surface.fill((255, 255, 255))
        self.decrypt_view.update_needed = app.update_needed

        # update for backbutton
        win._current_background.backbutton.draw(app.update_needed)
        win._current_background.lockbutton.draw(app.update_needed)

        self.decrypt_view.passcode_box.handle_event(events)
        self.decrypt_view.draw(win.surface)

    @LDS.hookimpl
    def state_decrypt_validate(self, cfg, app, win, events):
        # Create a way to compare decrypt key entered by the user and the one in the document
        if app.find_login_event(events) and app.chosen_document and app.decrypt_key:
            # print('From Validate do',app.password)
            LOGGER.info("Attempting to validate decrypt_key, decrypt_key:{}, with decrypt_key from chosen document:{}".format(app.decrypt_key, app.chosen_document[7]))
            app.validated = app.chosen_document[7] == app.decrypt_key
            LOGGER.info(app.validated)
            if app.validated:
                app.validated = None
                app.chosen_document = None
                return 'chosen'
            # Write code to return to previous state if the last state was not choose

        elif app.find_next_back_event(events):
            app.chosen_document = None
            return 'chosen'
        elif app.find_lockscreen_event(events):
            return 'wait'
        elif self.choose_timer.is_timeout():    
            return 'wait'

    @LDS.hookimpl 
    def state_decrypt_exit(self, win):
        pass

    @LDS.hookimpl
    def state_preview_enter(self, app, win):
        self.count += 1
        win.set_capture_number(self.count, app.capture_nbr)

    @LDS.hookimpl
    def state_preview_validate(self):
        return 'capture'

    @LDS.hookimpl
    def state_capture_do(self, app, win):
        win.set_capture_number(self.count, app.capture_nbr)

    @LDS.hookimpl
    def state_capture_validate(self, app):
        if self.count >= app.capture_nbr:
            return 'processing'
        return 'preview'

    @LDS.hookimpl
    def state_processing_enter(self, win):
        win.show_work_in_progress()

    @LDS.hookimpl
    def state_processing_validate(self, cfg, app):
        if app.printer.is_ready() and cfg.getfloat('PRINTER', 'printer_delay') > 0\
                and app.count.remaining_duplicates > 0:
            return 'print'
        return 'finish'  # Can not print

    @LDS.hookimpl
    def state_print_enter(self, cfg, app, win):
        LOGGER.info("Display the final picture")
        win.show_print(app.previous_picture)
        win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())

        # Reset timeout in case of settings changed
        self.print_view_timer.timeout = cfg.getfloat('PRINTER', 'printer_delay')
        self.print_view_timer.start()

    @LDS.hookimpl
    def state_print_validate(self, app, win, events):
        printed = app.find_print_event(events)
        self.forgotten = app.find_capture_event(events)
        if self.print_view_timer.is_timeout() or printed or self.forgotten:
            if printed:
                win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())
            return 'finish'

    @LDS.hookimpl
    def state_finish_enter(self, cfg, app, win):
        if cfg.getfloat('WINDOW', 'finish_picture_delay') > 0 and not self.forgotten:
            win.show_finished(app.previous_picture)
            timeout = cfg.getfloat('WINDOW', 'finish_picture_delay')
        else:
            win.show_finished()
            timeout = 1

        # Reset timeout in case of settings changed
        self.finish_timer.timeout = timeout
        self.finish_timer.start()

    @LDS.hookimpl
    def state_finish_validate(self):
        if self.finish_timer.is_timeout():
            return 'wait'