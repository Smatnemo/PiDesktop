import LDS 
import os
import sys
import pygame
import time
from LDS.utils import LOGGER, get_crash_message, PoolingTimer
from LDS.accounts import LogIn, LogOut
from LDS.documents.document import decrypt_content2, document_authentication, download_and_upload, demo_download_document, delete_encrypted_file
from LDS.database.database import DataBase, document_update_query, insert_questions_answer_query


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
        # query the database every 30 seconds for downloaded documents
        self.query_database_timer = PoolingTimer(30)
        self.query_database_timer.start()

        self.input_label = ''

        self.login_view = None 
        self.decrypt_view = None

        self.failure_message = "oops"
        self.questions = ""

    @LDS.hookimpl
    def state_failsafe_enter(self, app, cfg, win):
        win.show_oops(self.failure_message, cfg)
        self.failed_view_timer.start() 
        if self.failure_message == 'downloading':
            # # download_and_upload()
            demo_download_document()
            app.database_updated = True
            self.failure_message = 'oops'
        LOGGER.error(get_crash_message())

    @LDS.hookimpl
    def state_failsafe_do(self, app, win, events):
        """Create option to download documents here either from backoffice or locally
        """
        self.input_label = "Enter Facility Unlock Code"
        app.find_touch_effects_event(events)
        if self.failure_message == 'download_orders':
            win._current_background.downloadbutton.draw(app.update_needed)
        
        event = app.find_download_event(events)
        if event:
            self.failure_message = 'downloading'
            
            # demo_download_document()
            # app.database_updated = True

    @LDS.hookimpl
    def state_failsafe_validate(self, app):
        if self.failure_message == 'downloading':            
            return 'failsafe'
        if self.failed_view_timer.is_timeout():
            if (self.failure_message == 'no_printer' or self.failure_message == 'no_camera'\
                 or self.failure_message == 'no_document'):
                return 'chosen'
            elif self.failure_message == 'no_orders':
                app.database_updated = False
                self.failure_message = 'download_orders'
                # Expanded timer to give time to unzip files.
                self.failed_view_timer = PoolingTimer(60)
                return 'failsafe'
            # elif self.failure_message == 'download_orders':
            #     self.failure_message = 'oops'
            #     return 'wait'
            elif self.failure_message == 'oops':
                self.input_label = "Enter Facility Unlock Code"
                self.failed_view_timer = PoolingTimer(5)
                return 'login'
            else:
                self.input_label = "Enter Facility Unlock Code"
                self.failed_view_timer = PoolingTimer(5)
                self.failure_message = 'oops'
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
        app.previous_state = 'wait'
        event = app.find_screen_event(events)
        if event:
            return 'login'
      

    @LDS.hookimpl
    def state_wait_exit(self, win):
        self.count = 0
        win.show_image(None)  # Clear currently displayed image

    @LDS.hookimpl
    def state_login_enter(self, cfg, app, win):
        LOGGER.info("Attempting to Login")

        #if self.input_label == "Enter CO Unlock Code":
        #   app.previous_state = "choose"

        if app.previous_state == 'wait':
            self.input_label = "Enter Facility Unlock Code"

        if app.previous_state == 'choose':
            self.input_label = "Enter CO Unlock Code"

        # Makes sense?     
        # if app.previous_state == 'chosen':
        #     self.input_label = "Enter Decryption Code"
        self.login_view = win.show_login(self.input_label, cfg) 
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        if app.database_updated or self.query_database_timer.is_timeout():
            db = DataBase()
            app.documents, app.documents_number = db.get_inmate_documents()
            win.documents_foreground = {}
            app.database_updated = None
            self.query_database_timer.start()
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
        if self.input_label == "Enter CO Unlock Code":
            win._current_background.backbutton.draw(app.update_needed)
            win._current_background.lockbutton.draw(app.update_needed)

        self.login_view.update_needed = app.update_needed
        self.login_view.passcode_box.handle_event(events)
        self.login_view.draw(win.surface)
        

    @LDS.hookimpl 
    def state_login_validate(self, cfg, app, win, events):
        # Create a way to validate username and password
        if app.find_login_event(events):
            if app.previous_state == "choose" and app.staff:
                app.validated = app.password==app.staff[1]
            else:
                LOGGER.info("Attempting to validate password")
                login = LogIn()
                app.validated = login.authenticate(app.password)
                LOGGER.info(app.validated)

            if app.validated:
                app.validated = None
                self.count_failed_attempts = 0
                if app.staff and app.previous_state == 'choose':
                    # Log staff session before making it empty
                    app.staff = []
                    app.previous_state = 'choose'
                    return 'choose'
                app.previous_state = "login"

                app.staff = ()
                return "choose"
            else:
                self.count_failed_attempts += 1
                LOGGER.info("This is failed attempt number {}".format(self.count_failed_attempts))
                if self.count_failed_attempts == app.attempt_count:
                    self.count_failed_attempts = 0
                    return 'lock'
                else:
                    app.previous_state = 'login'
                    return 'passfail'
        elif app.find_back_event(events):
            app.previous_state = 'login'
            app.staff = ()
            return 'choose'
        elif app.find_lockscreen_event(events):
            app.staff = ()
            return 'wait'
            # Write code to return to previous state if the last state was not choose
        elif self.choose_timer.is_timeout():    
            return 'wait'
    
    # @LDS.hookimpl
    # def state_login_exit(self, app):
    #     app.previous_state = 'login'

    @LDS.hookimpl
    def state_choose_enter(self, cfg, app, win):
        LOGGER.info("Show document choice (nothing selected)")
        win.set_print_number(0, False)  # Hide printer status
    
        if app.staff_list and app.previous_state=='login':
            try:
                win.show_co_choices(app.staff_list, cfg)
            except Exception as ex:
                self.failure_message = 'no_staff'
                raise ex
        if app.previous_state=='choose':
            try:
                win.show_choices(app.documents, cfg)
            except Exception as ex:
                print("Document list: ", app.documents)
                self.failure_message = 'no_orders' if not app.documents else 'oops'
                raise ex
            
        app.inmate_number = None
        win._current_background.reset_timer = True
        self.choose_timer.start()

    @LDS.hookimpl
    def state_choose_do(self, cfg, app, win, events):
        if events:
            win._current_background.reset_timer = events
            self.choose_timer.start()

        app.find_touch_effects_event(events)
        # For CO

        # For documents
        win._current_documents_foreground.view.update_needed = app.update_needed
        if app.previous_state == 'login':
            win.show_co_choices(app.staff_list, cfg)
        if app.previous_state == 'choose':
            win.show_choices(app.documents, cfg)

        # update for buttons
        win._current_background.backbutton.draw(app.update_needed)
        win._current_background.lockbutton.draw(app.update_needed)
        win._current_documents_foreground.nextbutton.draw(app.update_needed)
        win._current_documents_foreground.previousbutton.draw(app.update_needed)


        event = app.find_choose_event(events)
        if event:
            if app.previous_state=='choose':
                app.inmate_number = win._current_documents_foreground.view.choseninmaterow.inmate_number
                # Is this correct?
            elif app.previous_state=='login':
                app.staff = win._current_documents_foreground.view.chosenStaffRow.staff
        
        next_previous_foreground_event = app.find_next_previous_event(events)
        if next_previous_foreground_event:
            win._current_documents_foreground.view.change_view = next_previous_foreground_event
   
    @LDS.hookimpl
    def state_choose_validate(self, cfg, app, events):
        if app.find_back_event(events):
            app.previous_state = 'choose'
            self.input_label = "Enter Facility Unlock Code"
            return 'wait'
        elif app.find_lockscreen_event(events):
            app.previous_state = 'choose'
            self.input_label = "Enter Facility Unlock Code"
            return 'wait'
        elif app.inmate_number:
            return 'chosen'
        elif app.staff:
            app.previous_state = 'choose'
            return 'login'
        elif self.choose_timer.is_timeout():
            return 'wait'
        
        

    @LDS.hookimpl
    def state_chosen_enter(self, cfg, app, win):
        LOGGER.info("Show chosen inmate document choice (inmate %s selected)", app.inmate_number)
        win.show_choices(app.documents, cfg, selected=app.inmate_number)
        # Reset timeout in case of settings changed
        win._current_background.reset_timer = True
        self.choose_timer.start()

    @LDS.hookimpl
    def state_chosen_do(self, cfg, app, win, events):
        if events:
            # If there is any event restart timer
            win._current_background.reset_timer = events
            self.choose_timer.start()

        app.find_touch_effects_event(events)

        win._current_documents_foreground.view.update_needed = app.update_needed
        win.show_choices(app.documents, cfg, selected=app.inmate_number)

        # update for backbutton
        win._current_background.backbutton.draw(app.update_needed)
        win._current_background.lockbutton.draw(app.update_needed)

        win._current_documents_foreground.nextbutton.draw(app.update_needed)
        win._current_documents_foreground.previousbutton.draw(app.update_needed)

        event = app.find_choose_event(events)
        if event:
            app.chosen_document = win._current_documents_foreground.view.chosendocumentrow
        
        next_previous_foreground_event = app.find_next_previous_event(events)
        if next_previous_foreground_event:
            win._current_documents_foreground.view.change_view = next_previous_foreground_event
   

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
            if app.printer.is_ready() and app.camera:
                app.previous_state = 'chosen'
                return 'decrypt'
            elif not app.printer.is_ready():
                self.failure_message = "no_printer"
                app.chosen_document = None
                return 'failsafe'
            elif not app.camera:
                self.failure_message = 'no_camera'
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
    def state_decrypt_enter(self, app, cfg, win):
        LOGGER.info("Entered the decrypt state")
        self.decrypt_view = win.show_decrypt(cfg) # Create a function in window module to display login page
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        # Find way to display it in the login window during login in activity
        win._current_background.reset_timer = True
        self.choose_timer.start()

    @LDS.hookimpl
    def state_decrypt_do(self, app, win, events):
        if events:
            win._current_background.reset_timer = True
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

        # update timer by calling current background - change during refactoring to the window module
        win._current_background.resize(win.surface)
        win._current_background.paint(win.surface)

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
                self.count_failed_attempts = 0
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
            return 'chosen' if app.documents else 'wait'
        elif app.find_lockscreen_event(events):
            app.previous_state = 'decrypt' if app.documents else 'choose'
            return 'wait'
        elif self.choose_timer.is_timeout(): 
            app.previous_state = 'decrypt' if app.documents else 'choose' 
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
            self.input_label = "Enter Facility Unlock Code"
            return 'wait' 

    # ----------------------------- PassFail State           --------------------------------
    @LDS.hookimpl
    def state_passfail_enter(self,app,win):
        LOGGER.info("This is the passfail state")
        self.failed_view_timer.start()
        print("Previous state was {}".format(app.previous_state))
        if app.previous_state == 'decrypt':
            message = 'wrong_decrypt'        
        elif app.staff and app.previous_state == 'login':
            self.input_label = "Enter Facility Unlock Code"
            message = 'wrong_co'
        elif app.previous_state == 'login':
            self.input_label = "Enter Facility Unlock Code"
            message = 'wrong_password'
        elif app.previous_state == 'finish':
            message = 'finished'
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
    def state_processing_exit(self):
        self.count = 0

    @LDS.hookimpl
    def state_print_enter(self, cfg, app, win):
        if app.print_job and app.printer.is_ready():
            LOGGER.info("Display the Document details to be printed")
            LOGGER.info("Printing Document: {}".format(app.print_job.name))
            app.print_event()
            self.print_status = "print"
            self.question = "Q1"
            app.questions_answers = ['' for _ in range(1)]
            self.document_name = app.chosen_document.document_name
            self.enable_button = True
            win.show_print(cfg, app.previous_picture, self.print_status, self.question, self.document_name, app.chosen_document.page_count)     
        elif not app.printer.is_ready():
            LOGGER.info("Printer status is not available")
        elif app.database_updated:
            if not self.questions:
                # Run this state after taking photograph or signature of the inmate
                language_id = 1
                # Query database to get questions
                db = DataBase()
                self.questions = db.get_questions(language_id)
            if self.questions:
                self.index = 0
                self.question = self.questions[0]
                self.print_status = '' # Goes to Do.
              
                   
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
                # Breaking logic here for Demo - hiding controls
                if answered.answer==True:
                    self.print_status = "print_successful"
                else:
                    self.print_status = "print_unsuccessful"
                # append answers to the list
                if answered.answer == True:
                    app.questions_answers[0] = 1
                elif answered.answer == False:
                    app.questions_answers[0] = 0
            self.document_name = ''
                
            
        # Draw screen with the new question
        win.show_print(cfg, app.previous_picture, self.print_status, self.question, self.document_name)

        # Enable the buttons of the page
        win._current_background.yesbutton.enabled(self.enable_button)
        win._current_background.nobutton.enabled(self.enable_button)

        # Update the buttons to listen to events
        win._current_background.yesbutton.draw(app.update_needed)
        if self.question != 'capture_photo':
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
        # After answering last questions and updating the database return to wait
        answered = app.find_question_event(events)
        if answered and (answered.question in self.questions):      
            app.questions_answers = [answered.question[1], answered.answer, 340]
            # append answers to the list
            if answered.answer == True:
                app.questions_answers[1] = 1
            elif answered.answer == False:
                app.questions_answers[1] = 0

            db = DataBase()
            db.__insert__(insert_questions_answer_query, tuple(app.questions_answers))
            self.questions.pop(0)
            self.input_label = "Enter Facility Unlock Code"
            if self.questions:
                return 'print'            
            else: 
                return 'signature'
            
            
        
    @LDS.hookimpl
    def state_signature_enter(self, cfg, app, win):
        """Capture signature        
        """    
        print("This is the count",self.count)    
        if not self.count:
            self.count = 1
        self.question = "Inmate Signature"                
        win.show_signature(cfg, question=self.question, image="sig.png")
        win._current_background.donebutton.draw(app.update_needed)
        self.enable_button = True
    @LDS.hookimpl
    def state_signature_do(self, cfg, app, win, events):
        """Keep calling it in a loop
        """ 
        # This assigns a touch event to app.update_needed before passing update_needed to the draw method in line 679
        app.find_touch_effects_event(events) 
                  
        self.done = app.find_signature_event(events) 
        if self.done and self.count == 2:
            self.failure_message = 'finished'            
        elif self.done and self.count == 1:
            self.count = self.count + 1
            self.question = "Correctional Officer Signature"
            # After changing the question, this diplays the changed question once
            win.show_signature(cfg, question=self.question, image="sig.png")
        # this runs in a loop and continues to update the event for the button for finger down and finger up
        win._current_background.donebutton.draw(app.update_needed)
    @LDS.hookimpl
    def state_signature_validate(self, cfg, app, win, events):
        """Verify conditions for the next state
        """                
        if self.failure_message == 'finished':  
            self.count = 0       
            return 'failsafe'
        


    @LDS.hookimpl
    def state_finish_enter(self, cfg, app, win):
        self.print_status = 'capture_again'
        self.question = 'capture_photo'
        win.show_print(cfg, app.previous_picture, self.print_status, self.question)

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
        # Change to if self.forgotten.answer == True - Approve Photo
        if self.forgotten:
            if self.forgotten.answer == True:
                # read image into blob
                blob=app.convertToBinaryData(app.previous_picture_file)
                os.remove(app.previous_picture_file)
                # win._current_documents_foreground.view.inmate_documents
                win._current_documents_foreground.view.update_view(app.inmate_number, blob, decrypted=True, printed=True)
                app.documents = win._current_documents_foreground.view.inmate_documents  

                db = DataBase()
                db.__update__(document_update_query, (app.questions_answers[0], app.chosen_document.document[16], app.chosen_document.document[0]))
                app.database_updated = True
 
                
                # delete decrypted file
                app.print_job.close()
                os.unlink(app.print_job.name)
                app.print_job = None

                # delelte Encrypted file
                delete_encrypted_file(app.chosen_document.document[1])

                app.chosen_document = None
                app.previous_picture = None
                app.previous_state = 'finish'
                app.inmate_number = None               
                win.drop_cache()
                return 'print' #state_print_enter
            
            elif self.forgotten.answer == False:
                win._current_foreground = None
                return 'preview'
            

        
        