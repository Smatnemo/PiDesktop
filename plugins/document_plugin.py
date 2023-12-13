
from LDS.utils import LOGGER, get_crash_message, PoolingTimer
import LDS
from LDS.documents.document import decrypt_content2, document_authentication
from LDS.database.database import DataBase, document_update_query, Questions_Answers_insert_query
from LDS.language import CURRENT


class DocumentPlugin:
    name = 'LDS-core:document'
    def __init__(self):
        self.failure_message = ""
        self.questions = []
        self.failed_view_timer = PoolingTimer(5)


    def state_failsafe_enter(self, win):
        win.show_oops(self.failure_message)
        self.failed_view_timer.start()
        LOGGER.error(get_crash_message())

    # @LDS.hookimpl
    def state_login_enter(self, app):
        # write code to query database and reveal the number of documents downloaded that are yet to be printed
        if app.database_updated:
            db = DataBase()
            app.documents, app.documents_number = db.get_inmate_documents()
            app.database_updated = None

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
                    self.failure_message = "oops"
                    return 'failsafe'
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
        elif app.find_back_event(events):
            app.chosen_document = None
            return 'chosen'
        elif app.find_lockscreen_event(events):
            app.previous_state = 'decrypt'
            return 'wait'
        elif self.choose_timer.is_timeout(): 
            app.previous_state = 'decrypt'   
            return 'wait'
        
    @LDS.hookimpl
    def state_print_enter(self, cfg, app, win): 
        if app.database_updated:
            # Get the list from database or configuration file
            question_id_list = [3, 4, 6, 7]
            # Get language choice from language module
            language_id = 1
            db = DataBase()
            self.questions = db.get_questions(language_id, *question_id_list) 
    
    @LDS.hookimpl
    def state_print_do(self, cfg, app, win, events):
        answered = app.find_question_event(events)
        if answered and self.questions:
            question_id = self.questions[0][1]
            if answered.question == 'Q2':
                self.question = 'Q3'
                self.print_status = ""
                # append the answers to the 
                if answered.answer == 'YES':
                    app.questions_answers[2] = 1
                elif answered.answer == 'NO':
                    app.questions_answers[2] = 0