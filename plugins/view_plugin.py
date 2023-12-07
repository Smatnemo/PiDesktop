import LDS 
import os
import sys
import pygame
from LDS.utils import LOGGER, get_crash_message, PoolingTimer
from LDS.accounts import LogIn, LogOut
from LDS.documents.document import decrypt_content, document_authentication
from LDS.database.database import DataBase, document_update_query

BUTTONDOWN = pygame.USEREVENT + 1
class ViewPlugin(object):

    """Plugin to manage the LDS window dans transitions.
    """

    name = 'LDS-core:view'
    

    def __init__(self, plugin_manager):
        self._pm = plugin_manager
        self.count = 0
        self.count_failed_attempts = 0
        self.forgotten = False
        # Seconds to display the failed message
        self.failed_view_timer = PoolingTimer(5)
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
        # Lock screen timer for failed login or failed decryption after 3 attempts
        self.lock_screen_timer = PoolingTimer(30)

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
        win.show_intro()

    @LDS.hookimpl
    def state_wait_do(self, app, win, events):
        """Write logic to continuously query database for update
        """

    @LDS.hookimpl
    def state_wait_validate(self, cfg, app, events):
        event = app.find_screen_event(events)
        if event:
            LOGGER.info("This is the event from wait state:{}".format(event))
            return 'login'
      

    @LDS.hookimpl
    def state_wait_exit(self, win):
        self.count = 0
        win.show_image(None)  # Clear currently displayed image

    @LDS.hookimpl
    def state_login_enter(self, app, win):
        LOGGER.info("Attempting to Login")
        self.login_view = win.show_login(app.previous_state) # Create a function in window module to display login page
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        # Find way to display it in the login window during login in activity
        self.choose_timer.start()
        
    @LDS.hookimpl
    def state_login_do(self, app, win, events):
        
        if events:
            # LOGGER.info("Events:{}".format(events))
            self.choose_timer.start()
        if app.find_login_event(events):
            if self.login_view.passcode_box.input_text != '':
                app.password = self.login_view.passcode_box.input_text 
            else:
                app.password = self.login_view.get_input_text() 
            self.login_view.passcode_box.text=''
            self.login_view.passcode_box.txt_surface = self.login_view.passcode_box.font.render(self.login_view.passcode_box.text, True, self.login_view.passcode_box.color)
        self.login_view.update_needed = app.update_needed
        self.login_view.passcode_box.handle_event(events)
        self.login_view.draw(win.surface)
        
        

    @LDS.hookimpl 
    def state_login_validate(self, cfg, app, win, events):
        # Create a way to validate username and password
        if app.find_login_event(events):
            LOGGER.info("Attempting to validate password")
            login = LogIn()
            app.validated = login.authenticate(app.password)
            LOGGER.info(app.validated)
            if app.validated:
                app.validated = None
                return app.previous_state if app.previous_state != 'wait' and app.previous_state != 'login' and app.previous_state is not None else 'choose'
            else:
                self.count_failed_attempts += 1
                LOGGER.info("This is failed attempt number {}".format(self.count_failed_attempts))
                if self.count_failed_attempts == app.attempt_count:
                    self.count_failed_attempts = 0
                    return 'lock'
                else:
                    app.previous_state = 'login'
                    return 'passfail'
            # Write code to return to previous state if the last state was not choose
        elif self.choose_timer.is_timeout():    
            return 'wait'

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
            self.choose_timer.start()

        win._current_documents_foreground.inmate_documents_view.update_needed = app.update_needed
        win.show_choices(app.documents)

        # update for buttons
        win._current_background.backbutton.draw(app.update_needed)
        win._current_background.lockbutton.draw(app.update_needed)
        win._current_documents_foreground.nextbutton.draw(app.update_needed)
        win._current_documents_foreground.previousbutton.draw(app.update_needed)

        event = app.find_choose_event(events)
        if event:
            app.inmate_number = win._current_documents_foreground.inmate_documents_view.choseninmaterow.inmate_number
   
    @LDS.hookimpl
    def state_choose_validate(self, cfg, app, events):
        if app.find_next_back_event(events):
            return 'login'
        elif app.find_lockscreen_event(events):
            app.previous_state = 'choose'
            return 'wait'
        elif app.inmate_number:
            return 'chosen'
        elif self.choose_timer.is_timeout():
            return 'wait'
        
        

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

        win._current_documents_foreground.nextbutton.draw(app.update_needed)
        win._current_documents_foreground.previousbutton.draw(app.update_needed)

        event = app.find_choose_event(events)
        if event:
            app.chosen_document = win._current_documents_foreground.document_view.chosendocumentrow
        

    @LDS.hookimpl
    def state_chosen_validate(self, app, win, events):
        if app.find_next_back_event(events):
            app.inmate_number = None
            app.chosen_document = None
            # Drop cached foreground
            win.documents_foreground = {}
            return 'choose'
        elif app.find_lockscreen_event(events):
            app.previous_state = 'wait'
            return 'wait'
        elif app.chosen_document:
            app.previous_state = 'chosen'
            return 'decrypt'
        elif self.choose_timer.is_timeout():
            app.previous_state = 'wait'
            return 'wait'
        
        
    @LDS.hookimpl
    def state_chosen_exit(self, app):
        # Exit the chosen state
        pass


    @LDS.hookimpl
    def state_decrypt_enter(self, app, win):
        LOGGER.info("Entered the decrypt state")
        print("This is the previous state", app.previous_state)
        self.decrypt_view = win.show_decrypt(app.previous_state) # Create a function in window module to display login page
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

        # update for backbutton and lockbutton
        win._current_background.backbutton.draw(app.update_needed)
        win._current_background.lockbutton.draw(app.update_needed)

        self.decrypt_view.passcode_box.handle_event(events)
        self.decrypt_view.draw(win.surface)

    @LDS.hookimpl
    def state_decrypt_validate(self, cfg, app, win, events):
        # Create a way to compare decrypt key entered by the user and the one in the document
        if app.find_login_event(events) and app.chosen_document and app.decrypt_key:
            # print('From Validate do',app.password)
            LOGGER.info("Attempting to validate decrypt_key, decrypt_key:{}, with decrypt_key from chosen document:{}".format(app.decrypt_key, app.chosen_document.document[7]))
            app.validated = app.chosen_document.document[7] == app.decrypt_key
            LOGGER.info(app.validated)
            if app.validated:
                app.validated = None
                # Decrypt the document using the document file path and check if the documents pages match
                result = decrypt_content(app.chosen_document.document[7], app.chosen_document.document[1])
                verify_decryption = document_authentication(result.name, app.chosen_document.document)
                if verify_decryption:
                    app.decrypted_file = result.name
                    LOGGER.info("Done Decrypting")
                    app.print_job = result.name        
                    return 'print'
                else:
                    LOGGER.error("Encountered error decrypting file:".format(app.chosen_document.document_name))
                    app.chosen_document = None
                    return 'failsafe'
            else:
                self.count_failed_attempts += 1
                LOGGER.info("This is failed attempt number {}".format(self.count_failed_attempts))
                if self.count_failed_attempts == app.attempt_count:
                    self.count_failed_attempts = 0
                    return 'lock'
                else:
                    app.previous_state = 'decrypt'
                    return 'passfail'
            # Write code to return to previous state if the last state was not choose
        elif app.find_next_back_event(events):
            app.chosen_document = None
            return 'chosen'
        elif app.find_lockscreen_event(events):
            app.previous_state = 'decrypt'
            return 'wait'
        elif self.choose_timer.is_timeout(): 
            app.previous_state = 'decrypt'   
            return 'wait'
        
   

    # ----------------------------- Lock State -----------------------------
    # This state is entered when password attempt is failed a number of times
    @LDS.hookimpl
    def state_lock_enter(self,app,win):
        LOGGER.info("This is the lock state")
        self.lock_screen_timer.start()
        
        win.show_locked('locked', app.attempt_count)

    @LDS.hookimpl
    def state_lock_do(self, app, win, events):
        win.show_locked('locked')
            
    @LDS.hookimpl
    def state_lock_validate(self, cfg, app, events): 
        if self.lock_screen_timer.is_timeout():
            return 'login' 

    # ----------------------------- PassFail State           --------------------------------

    @LDS.hookimpl
    def state_passfail_enter(self,app,win):
        LOGGER.info("This is the passfail state")
        self.failed_view_timer.start()
        print("Previous state was {}".format(app.previous_state))
        if app.previous_state == 'decrypt':
            message = 'wrong_decrypt'
        elif app.previous_state == 'login':
            message = 'wrong_password'
        win.show_locked(message)
            
    @LDS.hookimpl
    def state_passfail_validate(self, cfg, app, events): 
        if self.failed_view_timer.is_timeout():
            return app.previous_state
        
# -----------------------------------------------------------------
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
            return 'finish'
        return 'failsafe'  # Can not process photo

    @LDS.hookimpl
    def state_print_enter(self, cfg, app, win):
        LOGGER.info("Display the Document details to be printed")
        LOGGER.info("Printing Document: {}".format(app.print_job))
        self.print_status = "print"
        self.question = "Q1"
        self.document_name = app.chosen_document.document_name
        self.enable_button = False
        win.show_print(app.previous_picture, self.print_status, self.question, self.document_name, app.chosen_document.page_count)
        if app.print_job and app.printer.is_ready():
            app.print_event()

    @LDS.hookimpl
    def state_print_do(self, cfg, app, win, events):
        
        printed = app.find_print_status_event(events)
        if printed:
            self.enable_button = True
            win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())
            app.print_job = None
        
        question_answers = {}
        answered = app.find_question_event(events)
        if answered:
            self.enable_button = True
            # Fetch different question
            print(answered)
            if answered.question == 'Q1':
                self.question = 'Q2'
                if answered.answer=='YES':
                    self.print_status = "print_successful"
                else:
                    self.print_status = "print_unsuccessful"
                # Write the answer to the database for Q1
            elif answered.question == 'Q2':
                self.question = 'Q3'
                self.print_status = ""
                # Write this into the database for Q2
            elif answered.question == 'Q3':
                self.question = 'capture_photo'
                # win._current_background.yesbutton_enabled = False

                # Write this into the database for Q3
            self.document_name = ''
        # Draw screen with the new question
        win.show_print(app.previous_picture, self.print_status, self.question, self.document_name)

        # Enable the buttons of the page
        win._current_background.yesbutton.enabled(self.enable_button)
        win._current_background.nobutton.enabled(self.enable_button)

        # Update the buttons to listen to events
        win._current_background.yesbutton.draw(app.update_needed)
        win._current_background.nobutton.draw(app.update_needed)

        
       
    @LDS.hookimpl
    def state_print_validate(self, app, win, events):
        # This event will trigger the capture process
        self.forgotten = app.find_capture_event(events)
        if self.forgotten:
            self.question = ""
            app.picture_name = str(app.inmate_number) + str(app.chosen_document.document[0])
            app.capture_nbr = 1
            return 'preview'
        
    @LDS.hookimpl
    def state_capture_signature_enter(self):
        """Capture signature
        """
    @LDS.hookimpl
    def state_capture_signature_do(self):
        """Keep calling it in a loop
        """
    @LDS.hookimpl
    def state_capture_signature_validate(self):
        """Verify conditions for the next state
        """
    @LDS.hookimpl
    def state_capture_signature_exit(self):
        """Validate for the next state
        """

    @LDS.hookimpl
    def state_finish_enter(self, cfg, app, win):
        self.print_status = 'capture_again'
        self.question = 'capture_photo'
        win.show_print(app.previous_picture, self.print_status, self.question)

    @LDS.hookimpl
    def state_finish_do(self, cfg, app, win, events):
        # Enable the buttons of the page
        win._current_background.yesbutton.enabled(self.enable_button)
        win._current_background.nobutton.enabled(self.enable_button)

        # Update the buttons to listen to events
        win._current_background.yesbutton.draw(app.update_needed)
        win._current_background.nobutton.draw(app.update_needed)


    @LDS.hookimpl
    def state_finish_validate(self, app, win, events):
        self.forgotten = app.find_capture_event(events)
        if self.forgotten:
            if self.forgotten.answer == 'NO':
                # read image into blob
                blob=app.convertToBinaryData(app.previous_picture_file)
                os.remove(app.previous_picture_file)
                # win._current_documents_foreground.document_view.inmate_documents
                win._current_documents_foreground.document_view.update_view(app.inmate_number, blob, decrypted=True, printed=True)
                app.documents = win._current_documents_foreground.document_view.inmate_documents  
                win.documents_foreground = {}
                db = DataBase()
                db.__update__(document_update_query, (app.chosen_document.document[16], app.chosen_document.document[0]))
                # print(app.chosen_document.document[16])
                # insert tuple into database
                app.chosen_document = None
                app.previous_picture = None
                return 'login'
            
            elif self.forgotten.answer == 'YES':
                win._current_foreground = None
                return 'preview'
            

        
        