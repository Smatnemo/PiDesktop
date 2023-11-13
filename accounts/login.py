from LDS.database import DataBase
from LDS.utils import LOGGER
class LogIn:
    def __init__(self):
        self.db = DataBase()
        
    
    def authenticate(self, passcode):
        if passcode is not None:
            # Take the database and open a database 
            self.db.open()
            result = self.db.get_passcode(passcode)
            try:
                # Run a query to the database to get a passcode 
                if passcode == result[0]:

                    self.db.close()
                    return True
                else:
                    self.db.close()
                    return False
            except Exception as ex:
                LOGGER.error(str(ex))
                LOGGER.debug('Try using Correct Password', exc_info=True)
            finally:
                pass
            
            