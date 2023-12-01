from LDS import package_dir 
from .document import *
from LDS.utils import LOGGER

# Create directory for documents using the LDS package
def initialize_documents_dirs():
    encrypted_doc_dir = make_dir(DOC_DIR)
    temp_dir = make_dir(TEMP_DIR)
    LOGGER.info("Directory for Encrypted Documents: {}".format(encrypted_doc_dir))
    LOGGER.info("Directory for Documents to be printed: {}".format(temp_dir))



# Class that will decrypt the document and update the status
class DecryptDocument:
    def __init__(self):
        pass