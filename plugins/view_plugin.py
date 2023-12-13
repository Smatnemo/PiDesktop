import LDS 
import os
import sys
import pygame
import time
from LDS.utils import LOGGER, get_crash_message, PoolingTimer
from LDS.accounts import LogIn, LogOut
from LDS.documents.document import decrypt_content2, document_authentication
from LDS.database.database import DataBase, document_update_query, Questions_Answers_insert_query

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
        # Create a delay before allowing the next state
        self.delay_state_timer = PoolingTimer(2)

        self.login_view = None 
        self.decrypt_view = None

        self.failure_message = ""
        self.questions = ""

    @LDS.hookimpl
    def state_failsafe_enter(self, win):
        win.show_oops(self.failure_message)
        self.failed_view_timer.start()
        LOGGER.error(get_crash_message())

    @LDS.hookimpl
    def state_failsafe_validate(self):
        if (self.failure_message == 'no_printer' or self.failure_message) and self.failed_view_timer.is_timeout():
            return 'chosen'
        elif self.failed_view_timer.is_timeout():
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
            return 'login'
      

    @LDS.hookimpl
    def state_wait_exit(self, win):
        self.count = 0
        pygame.event.clear()
        win.show_image(None)  # Clear currently displayed image

    @LDS.hookimpl
    def state_login_enter(self, app, win):
        LOGGER.info("Attempting to Login")
        self.login_view = win.show_login() 
        app.database_updated = True
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        if app.database_updated:
            db = DataBase()
            app.documents, app.documents_number = db.get_inmate_documents()
            app.database_updated = None
        # Find way to display it in the login window during login in activity
        self.choose_timer.start()
        
    @LDS.hookimpl
    def state_login_do(self, app, win, events):
        
        if events:
            self.choose_timer.start()

        app.find_touch_effects_event(events)

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
                return app.previous_state if (app.previous_state=='chosen' and app.inmate_number) or app.previous_state != 'wait' and app.previous_state != 'finish'\
                      and app.previous_state != 'login' and app.previous_state is not None else 'choose'
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
        app.inmate_number = None
        self.choose_timer.start()

    @LDS.hookimpl
    def state_choose_do(self, app, win, events):
        if events:
            self.choose_timer.start()

        app.find_touch_effects_event(events)

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

        next_previous_foreground_event = app.find_next_previous_event(events)
        if next_previous_foreground_event:
            win._current_documents_foreground.inmate_documents_view.change_view = next_previous_foreground_event
   
    @LDS.hookimpl
    def state_choose_validate(self, cfg, app, events):
        if app.find_back_event(events):
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
            self.choose_timer.start()

        app.find_touch_effects_event(events)

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
        if app.find_back_event(events):
            app.inmate_number = None
            app.chosen_document = None
            # Drop cached foreground
            win.documents_foreground = {}
            return 'choose'
        elif app.find_lockscreen_event(events):
            app.previous_state = 'wait'
            return 'wait'
        elif app.chosen_document:
            if app.printer.is_ready():
                app.previous_state = 'chosen'
                return 'decrypt'
            elif not app.printer.is_ready():
                self.failure_message = "no_printer"
                app.chosen_document = None
                return 'failsafe'
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
        self.decrypt_view = win.show_decrypt() # Create a function in window module to display login page
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        # Find way to display it in the login window during login in activity
        self.choose_timer.start()

    @LDS.hookimpl
    def state_decrypt_do(self, app, win, events):
        if events:
            self.choose_timer.start()
        
        app.find_touch_effects_event(events)

        if app.find_login_event(events):
            if self.decrypt_view.passcode_box.input_text != '':
                app.decrypt_key = self.decrypt_view.passcode_box.input_text 
            else:
                app.decrypt_key = self.decrypt_view.get_input_text() 
            self.decrypt_view.passcode_box.text=''
            self.decrypt_view.passcode_box.txt_surface = self.decrypt_view.passcode_box.font.render(self.decrypt_view.passcode_box.text, True, self.decrypt_view.passcode_box.color)
            
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
                try:
                    result = decrypt_content2(app.chosen_document.document[7], app.chosen_document.document[1])
                    verify_decryption = document_authentication(result.name, app.chosen_document.document)
                except Exception as ex:
                    LOGGER.error("Encountered an error:{}".format(ex))
                    self.failure_message = "decryption_failed"
                    if result:
                        result.close()
                        os.unlink(result.name)
                    return 'failsafe'
                if verify_decryption:
                    LOGGER.info("Done Decrypting")
                    app.print_job = result       
                    return 'print'
                else:
                    LOGGER.error("Encountered error verifying decrypted file:{}".format(app.chosen_document.document_name))
                    app.chosen_document = None
                    # write code to clean decrypted 
                    app.print_job = None 
                    result.close
                    os.unlink(result.name)
                    self.failure_message = "incomplete"
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
        elif app.find_back_event(events):
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
        LOGGER.info("Printing Document: {}".format(app.print_job.name))   
        if app.print_job and app.printer.is_ready():
            app.print_event()
            self.print_status = "print"
            self.question = "Q1"
            self.document_name = app.chosen_document.document_name
            self.enable_button = False
            win.show_print(app.previous_picture, self.print_status, self.question, self.document_name, app.chosen_document.page_count)     
        elif not app.printer.is_ready():
            LOGGER.info("Printer status is not available")
        elif app.database_updated:
            question_id_list = [3, 4, 6, 7]
            language_id = 1
            # Query database to get questions
            db = DataBase()
            self.questions = db.get_questions(language_id, *question_id_list)
            self.question = ''
        

    @LDS.hookimpl
    def state_print_do(self, cfg, app, win, events):
        # Flag for database questions
        app.find_touch_effects_event(events)

        printed = app.find_print_status_event(events)
        if printed:
            self.enable_button = True
            win.set_print_number(len(app.printer.get_all_tasks()), not app.printer.is_ready())
        
        answered = app.find_question_event(events)
        if answered:
            self.enable_button = True
            if answered.question == 'Q1':
                self.question = 'capture_photo'
                if answered.answer=='YES':
                    self.print_status = "print_successful"
                else:
                    self.print_status = "print_unsuccessful"
                # append answers to the list
                if answered.answer == 'YES':
                    app.questions_answers[1] = 1
                elif answered.answer == 'NO':
                    app.questions_answers[1] = 0
            self.document_name = ''
         
        
        if answered and self.questions:
            question = str(self.questions[0][1])
            print("Question id", question)
            # if answered.question == 'Q2':
            #     self.question = 'Q3'
            #     self.print_status = ""
            #     # append the answers to the 
            #     if answered.answer == 'YES':
            #         app.questions_answers[2] = 1
            #     elif answered.answer == 'NO':
            #         app.questions_answers[2] = 0
            
                
            
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

        app.find_touch_effects_event(events)

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

                app.questions_answers[0] = app.chosen_document.document[0]
                db = DataBase()
                db.__update__(document_update_query, (app.questions_answers[1], app.chosen_document.document[16], app.chosen_document.document[0]))
                db.__insert__(Questions_Answers_insert_query, tuple(app.questions_answers))
                app.database_updated = True
                
                app.chosen_document = None
                app.previous_picture = None
                app.previous_state = 'finish'
                app.inmate_number = None 
                
                # delete file
                app.print_job.close()
                os.unlink(app.print_job.name)
                app.print_job = None
                app.questions_answers = ['' for _ in range(21)]
                win.drop_cache()
                return 'print'
            
            elif self.forgotten.answer == 'YES':
                win._current_foreground = None
                return 'preview'
            

        
        