
import time

from LDS.utils import LOGGER 
class StatesMachine(object):

    """
    :attr states: a set of states that the pi application goes through 
    :type states: set
    :attr failsafe_state: the state the application goes into when there is an error
    :type failsafe_state: None or
    :attr active_state: the current state of the application 
    :type active_state: str or None
    :attr app: the application object passed in at class instantiation
    :type app: PiApplication
    :attr win: This is the window created using pygame
    :type win: PiWindow
    :attr cfg: configuration from the database 
    :type cfg: DataBase or ConfigParser
    :attr pm: This is a plugin manager that uses the generic plugins designs
    :type pm: 
    """
    def __init__(self, plugins_manager, configuration, application, window):
        self.states = set()
        self.failsafe_state = None
        self.active_state = None

        # Share the application to manage between states
        self.app = application
        self.win = window
        self.cfg = configuration
        self.pm = plugins_manager

        self._start_time = time.time()


    def add_state(self, state:str)->None:
        """
        Add state to the internal set of states
        """
        self.states.add(state)


    def remove_state(self, state:str)-> None:
        """
        Remove state from the internal collection of states
        """
        self.states.discard(state)
        if state == self.failsafe_state: # investigate why this is being used
            self.failsafe_state = None


    def add_failsafe_state(self, state:str)-> None:
        """
        Add a state that will be called in case of an exception
        :attr state: the name of the state
        :type state: str
        """
        self.failsafe_state = state
        self.add_state(state)


    def process(self, events:list):
        """
        Process events and let the current state do its thing
        :attr events: This is a list of events
        """
        # Only proceed if there is an active state
        if self.active_state is None:
            return
        
        try:
            # Perform the actions of the current state
            hook = getattr()
            hook()
            
            # Check conditions to activate the next state 
            hook = getattr()
            new_state_name = hook()
        except Exception as ex:
            LOGGER.error(str(ex))
            LOGGER.error('Back to failsafe state due to error:', exc_info = True)
        finally:
            pass 

        if new_state_name is not None:
            self.set_state(new_state_name)

    def set_state(self):
        pass

