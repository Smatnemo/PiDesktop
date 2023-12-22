from tempfile import NamedTemporaryFile
from LDS import package_dir
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad
from Crypto.Cipher import AES
from LDS.utils import LOGGER
from LDS.database.database import DataBase, document_insert_query
from LDS.media import get_filename
from random import randint

from hashlib import md5

import os 
import os.path as osp
import base64
import hashlib 
import LDS
import json
import requests 
import zipfile

TEMP_DIR = "/tmp/LDS"
DOC_DIR = osp.join(package_dir, "docs")
secret_iv = b"8eejFb2rKCavp2uU"
# secret_key = b"123456"
# password = "22222"


# List of responses from the backaoffice
response_pi_check = osp.join(DOC_DIR, "response_pi_check")
response_pi_confirm_download = osp.join(DOC_DIR, "response_pi_confirm_download")
# response_questions = osp.join(DOC_DIR, "response_questions")
py_check_url = 'https://legal.2e-admin.co.uk/webhooks/entities/py_check'
pi_confirm_download_url = 'https://legal.2e-admin.co.uk/webhooks/entities/pi_confirm_downloaded'
download_url = 'https://legal.2e-admin.co.uk/webhooks/entities/pi_file_download'

payload = {'eid':"10093", 'sha256': "d0135203a8026def89a131bcbca542160259526a548d0913029400f1b6d89c18"}
headers = {'X-lds-secret':"uriJhfB9K2amvxSDEL4dGiatDSbfQbN8LRPGPk3iz3GzUD8q",
            'User-Agent':"Legal_Document_System",
            'Content-Type':"application/json"
            }

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)
 
def get_response(filename):
    if osp.isfile(filename):
        with open(filename, 'r') as file:
            content_dict = json.load(file)
        # os.remove(filename)
    return content_dict

def get_document_list():
    res = requests.post(py_check_url, json=payload, headers=headers)
    if res.ok:
        content = res.json()
        return content
    else:
        return res.status_code

def download_and_upload():
    # document_list = get_document_list()
    document_list = get_response()
    if isinstance(document_list, list):
        try:
            for document in document_list:
                file = download_document(document['object_id'])

                check_and_upload(file, document)
                # num_list.append(num)
        except Exception as ex:
            print('Exception', ex)

def download_document(object_id, doc_dir=DOC_DIR):
    filename = "file_{}.pdf".format(object_id)
    filepath = osp.join(doc_dir, filename)
    payload.update({'object_id':"{}".format(object_id)})
    
    res = requests.post(download_url, json=payload, headers=headers)
    if res.ok:
        with open(filepath, 'wb') as f:
            f.write(res.content)
        return filepath
    else:
        return res.status_code
    

def check_and_upload(file, document):
    if osp.isfile(file):
        file_checksum = sha_checksum(file)
    else:
        raise

    if file_checksum == document['encrypted_file_checksum']: 
        payload.update({"checksum":"{}".format(file_checksum)})
        res = requests.post(pi_confirm_download_url, json=payload, headers=headers)
    if res.ok:    
        _, document_name = osp.split(file)
        document_path = "docs/"+document_name         
        
        data = (document_path, 
                210,
                297,
                0,
                0,
                0,
                document['encryption_key'], 
                document['document_page_count'], 
                document['inmate_number'], 
                'ready',
                0, 
                0, 
                document['encrypted_file_checksum'], 
                document['original_file_checksum'], 
                document['original_extension'],
                document['inmate_name'], 
                document['original_name'], 
                document['object_id'])
        db = DataBase()
        db.__insert__(document_insert_query, data)

# ------------------------------ For dummy testing ---------------------------------------


def demo_download_document():
    # unzip docs.zip folder
    LOGGER.info("Unzipping the docs.zip directory")
    with zipfile.ZipFile(osp.join(DOC_DIR,'docs.zip'), 'r') as zip_ref:
        zip_ref.extractall(osp.abspath(osp.dirname(DOC_DIR)))
    # copy all of its contents to the docs dir
    # update the database accordingly
    LOGGER.info("Deleting records from Documents")
    query = "DELETE FROM Documents;"
    db = DataBase()
    db.__delete__(query)
    reload_document_script = osp.join(DOC_DIR,"Documents.sql")
    LOGGER.info("Reloading the records for Documents table")
    db.reload_documents_table(reload_document_script)


# -----------------------------------------------------------------------------------------

def delete_encrypted_file(filename):
    filepath = osp.join(osp.abspath(osp.dirname(DOC_DIR)),filename)
    if osp.isfile(filepath):
        LOGGER.info("Deleting the file")
        os.remove(filepath)

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
    cover_page_name = get_filename('dec.pdf')
    back_page_name = get_filename('dec.pdf')
    try:
        page_count = count_pdf_pages(decrypted)
        if page_count == document[8]:
            page_count_match = True
        else:
            LOGGER.error("Page count did not match")
        file_checksum = get_file_checksum(decrypted, "original")
        if file_checksum == document[15]:
            checksum_match = True 
        else:
            LOGGER.error("Database checksum: {} Checksum did not match:{}".format(document[15], file_checksum))
        modified_document = append_pages(cover_page_name, back_page_name, decrypted)
        new_page_count = count_pdf_pages(modified_document)  
        page_count_match = True if new_page_count == document[8]+2 else False
    except Exception as ex:
        LOGGER.error("Error {} occured while documenting".format(ex))
    
    return True if page_count_match and checksum_match else False 
         

def decrypt2(password, in_file, out_file):
    bs = AES.block_size
    password = hashlib.sha256(password.encode()).hexdigest()[:32].encode()      
    iv = hashlib.sha256(secret_iv).hexdigest()[:16].encode()
    cipher = AES.new(password, AES.MODE_CBC, iv)
    next_chunk = b''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chr(chunk[-1]))
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)     

def decrypt_content(password, filename):
    filename_full_path = osp.join(osp.abspath(osp.dirname(DOC_DIR)), filename)
    encrypted = get_file_contents(filename_full_path)       
    decrypted = decrypt(encrypted, password) 
    temp_file = make_temp_file()  

    with open(temp_file.name, 'ab') as temp:
         temp.write(decrypted) 
    return temp_file            

def decrypt_content2(password, filename):
    temp_file = make_temp_file()
    filename_full_path = osp.join(osp.abspath(osp.dirname(DOC_DIR)), filename)

    with open(filename_full_path, 'rb') as in_file, open(temp_file.name, 'wb') as out_file:
        decrypt2(password, in_file, out_file)

    return temp_file

# --------- Create pages with inmate details ----
def create_pages():
    pass
# -------- Append pages to pdf ------------------
def append_pages(coverpagename, backpagename, dec_tmp_name):
    merger = PdfMerger()
    cover_page = PdfReader(coverpagename, 'rb')
    back_page = PdfReader(backpagename, 'rb')
    main_file = PdfReader(dec_tmp_name, 'rb')
    merger.append(cover_page)
    merger.append(main_file)
    merger.append(back_page)
    merger.write(dec_tmp_name)
    return dec_tmp_name