# [12:01] James Travers
#  $key = hash('sha256', $this->_secretKey);
#         $iv = substr(hash('sha256', $this->_secretIv), 0, 16);
#         $result = openssl_decrypt(base64_decode(file_get_contents($file)), $this->_encryptionAlgorithm, $key, 0, $iv);

# secret_iv - 8eejFb2rKCavp2uU - add this to the database 

# Algorithm - AES-256-CBC - add this to the database
# [12:16] James Travers
# private function write_temp_file($input){
#         // temp file function - mind to clean up when done with the file.
#         $f = tempnam(sys_get_temp_dir(), 'TMP_');
#         if(false !== $f){
#             file_put_contents($f, $input);
#         }                
#         return $f;
#     }
from pickle import FALSE
from tempfile import NamedTemporaryFile

from PyPDF2 import PdfReader, PdfWriter
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad, pad
from Crypto.Cipher import AES

from hashlib import md5

from Crypto import Random
import os 
import base64
import hashlib 

TEMP_DIR = "/tmp/LDS"
secret_iv = b"8eejFb2rKCavp2uU"
secret_key = b"123456"



key = "8d969eef6ecad3c29a3a629280e686cf"
iv = "81cf74ac0b21a7d2"
# # Determine salt and ciphertext
# encryptedDataB64 = 'U2FsdGVkX18A+AhjLZpfOq2HilY+8MyrXcz3lHMdUII2cud0DnnIcAtomToclwWOtUUnoyTY2qCQQXQfwDYotw=='
# encryptedData = base64.b64decode(encryptedDataB64)
# salt = encryptedData[8:16]


# ciphertext = encryptedData[16:]

# # Reconstruct Key/IV-pair
# pbkdf2Hash = PBKDF2(b'"mypassword"', salt, 32 + 16, count=100000, hmac_hash_module=SHA256)
# key = pbkdf2Hash[0:32]
# iv = pbkdf2Hash[32:32 + 16]

# # Decrypt with AES-256 / CBC / PKCS7 Padding
# cipher = AES.new(key, AES.MODE_CBC, iv)
# decrypted = unpad(cipher.decrypt(ciphertext), 16)

# print(decrypted)


# iv = hashlib.sha256(secret_iv).hexdigest()[0:16]
# key = hashlib.sha256(secret_key).hexdigest()[0:16]
# cipher = AES.new(key.encode("utf8"), AES.MODE_CBC, iv.encode("utf8"))

# with open("/home/pi/Desktop/picamera2-manual.pdf", 'rb') as document:
#     pdf = document.read()

# base64.b64decode(pdf)



# def derive_key_and_iv(password, salt, key_length, iv_length):
#     d = d_i = ''
#     while len(d) < key_length + iv_length:
#         d_i = md5(d_i + password + salt).digest()
#         d += d_i
#     return d[:key_length], d[key_length:key_length+iv_length]

def derive_key_and_iv(password, iv):
    iv = hashlib.sha256(iv).hexdigest()[0:16]
    key = hashlib.sha256(password).hexdigest()[0:32]

    return key.encode("utf8"), iv.encode("utf8")

def evp_simple(data):
    out = b''
    while len(out) < 32:
        out += md5(out + data).digest()
    return out[:32]


# def decrypt(in_file, out_file):
#     bs = AES.block_size
#     # salt = in_file.read(bs)[len('Salted__'):]
#     key, iv = derive_key_and_iv(secret_key, secret_iv)
#     cipher = AES.new(key, AES.MODE_CBC, iv)

#     decrypted = cipher.decrypt(in_file.r)
#     next_chunk = b''
#     finished = False
    
#     while not finished:
#         chunk, next_chunk = unpad(decrypted, 16)
#         # chunk.encode("utf8")
#         if len(next_chunk) == 0:
#             padding_length = ord(chunk[-1])
#             chunk = chunk[:-padding_length]
#             finished = True
#         # print("This is chunk", chunk)
#         out_file.write(next_chunk)
    
#     print("Written to this file {}".format(out_file.name))

def decrypt(in_file, out_file):
    bs = AES.block_size
    key, iv = derive_key_and_iv(secret_key, secret_iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = b''
    finished = False
    i = 0
    while not finished:
        read_data = in_file.read(bs)
        print("Data length", len(read_data))
        if len(read_data)<(bs):
            #     read_data = read_data + (' '*((1024*bs)-len(read_data))).encode("utf8")
            print("I am less than 16 bytes")
            padded_data = ' '*((bs)-len(read_data))
            print("padded-length",len(padded_data))
            padded_data = padded_data.encode("utf8")
            read_data = read_data + padded_data
            finished = True
            

        chunk, next_chunk = next_chunk, cipher.decrypt(read_data)
        if len(next_chunk) == 0:
            print(len(next_chunk))
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        
        out_file.write(chunk)
        i += 1
        print('First chunk', i)


def make_dir(temp_dir=TEMP_DIR):
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

def write_temp_file(input='tmp_pdf', mode='w+b'):
	with NamedTemporaryFile(prefix=input, delete=False, mode='w+b', suffix='.pdf', dir=TEMP_DIR) as temp_file:
		print(f'Temporary file path: {temp_file.name}')
	return temp_file

def count_pdf_pages(pdf_file):
    reader = PdfReader(pdf_file)
    count = len(reader.pages)
    return count 

def decode():
    pass
def get_file_contents(filename):
    with open(filename, 'rb') as f:
        file_content = f.read()

    return file_content

def main():
    make_dir()
    print("this is for the final file")
    tmp_file = write_temp_file(input='decrypted')
    
    filename = "/home/pi/Desktop/Video provides a powerful way to help you prove your point.pdf"
    file_content = get_file_contents(filename)
    encrypted_file_content = base64.b64decode(file_content)
    print("This is for the encoded file")
    new_tmp = write_temp_file('decoded')
    # encrypted_content = encrypted_file_content[16:]

    with open(new_tmp.name, 'wb') as tmp:
        tmp.write(encrypted_file_content)

    # with open(new_tmp.name, 'rb') as in_file, open(tmp_file.name, 'wb') as out_file:
    #     decrypt(in_file, out_file)


def main_loop():

    filename = "/home/pi/Desktop/Video provides a powerful way to help you prove your point.pdf"

    reader = PdfReader(filename)
    writer = PdfWriter()

    if reader.is_encrypted:
        reader.decrypt("123456")

    for page in reader.pages:
        writer.add_page(page)

	# Save the new PDF to a file
    with open("/tmp/decrypted-pdf.pdf", "wb") as f:
        writer.write(f)

    
if __name__ == "__main__":
     main()
     print("done")