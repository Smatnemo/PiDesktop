from tempfile import NamedTemporaryFile
from LDS import package_dir
from PyPDF2 import PdfReader, PdfWriter
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from LDS.utils import LOGGER

from hashlib import md5

import os 
import os.path as osp
import base64
import hashlib 

TEMP_DIR = "/tmp/LDS"
DOC_DIR = osp.join(package_dir, "docs")
secret_iv = b"8eejFb2rKCavp2uU"
# secret_key = b"123456"
# password = "22222"


 
def decrypt(enc, password):        
    password = hashlib.sha256(password.encode()).hexdigest()[:32].encode()      
    iv = hashlib.sha256(secret_iv).hexdigest()[:16].encode()
    cipher = AES.new(password, AES.MODE_CBC, iv)    
    return unpad(cipher.decrypt(enc), 16)    


def make_dir(dir=TEMP_DIR):
    if not os.path.exists(dir):
        os.mkdir(dir)
    return os.path.abspath(dir)

def make_temp_file(input='tmp_pdf', mode='w+b'):
	with NamedTemporaryFile(prefix=input, delete=False, mode=mode, suffix='.pdf', dir=TEMP_DIR) as temp_file:
		print(f'Temporary file path: {temp_file.name}')
	return temp_file

def count_pdf_pages(pdf_file):
    reader = PdfReader(pdf_file)
    count = len(reader.pages)
    return count 


def get_file_contents(filename):
    with open(filename, 'rb') as f:
        file_content = f.read()

    return file_content

def md5(fname):
    hash_md5 = hashlib.md5()
    hash_md5.update( open(fname,'rb').read() )
    return hash_md5.hexdigest()

def sha_checksum(filename):

    sha256_hash = hashlib.sha256()
    with open(filename,"rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_checksum(filename, original:str):
    """
    param: original: either encrypted or original
    """
    if original == "original":
        checksum = sha_checksum(filename)
    elif original == "encrypted":
        filename_full_path = osp.join(osp.abspath(osp.dirname(DOC_DIR)), filename)
        checksum = sha_checksum(filename_full_path)

    return checksum

def document_authentication(decrypted, document):
    """
    :param: document: passed from the database queried info
    :param: decrypted: temp file holding decrypted pdf
    """
    # Check if the number of pages match after decryption
    # check if the decrypted checksum matches the original document checksum
    page_count_match = False 
    checksum_match = False
    page_count = count_pdf_pages(decrypted)
    file_checksum = get_file_checksum(decrypted, "original")
    try:
        if page_count == document[8]:
            page_count_match = True
        else:
            LOGGER.error("Page count did not match")
        if file_checksum == document[15]:
            checksum_match = True 
        else:
            LOGGER.error("Database checksum: {} Checksum did not match:{}".format(document[15], file_checksum))
    except Exception as ex:
        LOGGER.error("Error {} occured while decrypting".format(ex))
    
    return True if page_count_match and checksum_match else False 
         
         

def decrypt_content(password, filename):
    filename_full_path = osp.join(osp.abspath(osp.dirname(DOC_DIR)), filename)
    encrypted = get_file_contents(filename_full_path)       

    decrypted = decrypt(encrypted, password) 

    temp_file = make_temp_file()  

    with open(temp_file.name, 'ab') as temp:
         temp.write(decrypted) 

    return temp_file            

