from LDS.database import DataBase 
from LDS.utils import LOGGER
from LDS.view.window import PiWindow
from LDS.states import StatesMachine



class PiApplication:

    def __init__(self):
       # Define states of the application
        self._machine = StatesMachine(self._pm, self._config, self, self._window)
        self._machine.add_state('videoplayback') # Add this state
        self._machine.add_state('wait')
        self._machine.add_state('beginsession') # Start - To do
        self._machine.add_state('login')
        self._machine.add_state('choose')
        self._machine.add_state('chosen')
        self._machine.add_state('preview')
        self._machine.add_state('capture')
        self._machine.add_state('showcapture') # work on showing the captured image
        self._machine.add_state('processing')
        self._machine.add_state('print')
        self._machine.add_state('finish')
        self._machine.add_state('reprint') # Add a reprint option and state.
        self._machine.add_state('endsession') # End the session

    def _initialize(self):
        pass 

    def main_loop(self):
        try:
            pass
        except Exception as e:
            # Log error
            LOGGER.error()
            # Get crash message
            LOGGER.error()
        finally:
            pass


def main():
    pass 

if __name__ == "__main__":
    main()