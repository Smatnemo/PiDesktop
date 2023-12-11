# This script is only run once on start up to create an sqlite database
import sqlite3
import os.path as osp
from LDS.utils import LOGGER
from LDS import package_dir

DB_PATH = osp.join(package_dir,"data/legal.db")
LOGGER.info("Database path: {}".format(DB_PATH))
print("Database Path:", DB_PATH)

# Database quries
create_object_table = """CREATE TABLE IF NOT EXISTS `Object` (
  'id' bigint PRIMARY KEY NOT NULL,
  'original_name' varchar(1024) NOT NULL,
  'original_extension' varchar(12) NOT NULL,
  'etag' varchar(64) NOT NULL,
  'encryption' varchar(12) NOT NULL,
  'upload_date' datetime NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  'download_date' datetime DEFAULT NULL,
  'deletion_date' timestamp DEFAULT NULL,
  'bucket' varchar(255) NOT NULL,
  'region' text NOT NULL,
  'endpoint' text NOT NULL,
  'objectName' text NOT NULL,
  'objecturl' text NOT NULL,
  'deleted' tinyint(1) NOT NULL DEFAULT "0" 
);
"""

create_entity_table = """
CREATE TABLE IF NOT EXISTS `Entity` (
  'id' int NOT NULL PRIMARY KEY,
  'enabled' tinyint(1) NOT NULL DEFAULT '1',
  'playback_video' INT NOT NULL,
  'name' varchar(80) NOT NULL,
  'description' VARCHAR(255),
  'microsoft_tenant_id' varchar(255) DEFAULT NULL,
  'brand_logo' int NOT NULL DEFAULT '0',
  'background' int NOT NULL DEFAULT '0',
  FOREIGN KEY ('brand_logo') REFERENCES 'Object' ('id'),
  FOREIGN KEY ('playback_video') REFERENCES 'object' ('id'),
  FOREIGN KEY ('background') REFERENCES 'object' ('id')
);
"""

create_documents_table = """
CREATE TABLE IF NOT EXISTS 'Documents' (
  'order' bigint PRIMARY KEY,
  'document_path' VARCHAR(255) NOT NULL,
  'width' int NOT NULL,
  'height' int NOT NULL,
  'created_by' bigint NOT NULL,
  'downloaded_on' datetime NOT NULL,
  'deleted_on' datetime NOT NULL
);"""

create_Questions_Answers_table = """
CREATE TABLE IF NOT EXISTS `Questions_Answers` (
  'id' INTEGER PRIMARY KEY AUTOINCREMENT,
  'document_id' bigint,
  'Q1' tinyint(1),
  'Q2' tinyint(1),
  'Q3' tinyint(1),
  'Q4' tinyint(1),
  'Q5' tinyint(1),
  'Q6' tinyint(1),
  'Q7' tinyint(1),
  'Q8' tinyint(1),
  'Q9' tinyint(1),
  'Q10' tinyint(1),
  'Q11' tinyint(1),
  'Q12' tinyint(1),
  'Q13' tinyint(1),
  'Q14' tinyint(1),
  'Q15' tinyint(1),
  'Q16' tinyint(1),
  'Q17' tinyint(1),
  'Q18' tinyint(1),
  'Q19' tinyint(1),
  'Q20' tinyint(1),
  'date_answered' DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ('document_id') REFERENCES 'Documents' ('order_id')
);
"""

create_tables = [create_object_table, create_entity_table, create_documents_table, create_Questions_Answers_table,]

document_insert_query = """ INSERT INTO 'Documents'
                                  (order_id, 
                                  document_path, 
                                  width, height, 
                                  created_by, 
                                  downloaded_on, 
                                  deleted_on, 
                                  decrypt_key, 
                                  num_of_pages, 
                                  inmate_number, 
                                  signature, 
                                  status, 
                                  printed, 
                                  decrypted,
                                  encrypted_file_checksum,
                                  original_file_checksum,
                                  inmate_photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

document_update_query = """UPDATE 'Documents'
                            SET printed = 1,
                                decrypted = 1,
                                status = 'printed',
                                inmate_photo= ?,
                                printed_date= date('now')
                            WHERE order_id= ? """

Questions_Answers_insert_query = """
INSERT INTO `Questions_Answers` (
  'document_id',
  'Q1',
  'Q2',
  'Q3',
  'Q4',
  'Q5',
  'Q6',
  'Q7',
  'Q8',
  'Q9',
  'Q10',
  'Q11',
  'Q12',
  'Q13',
  'Q14',
  'Q15',
  'Q16',
  'Q17',
  'Q18',
  'Q19',
  'Q20'
)  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""
# A list of standard queries for settings
# 1. query for getting the number of enabled products. int 
# 2. query for getting the photocount per product
# 3. Represent the results of query 1 and 2 with a tuple where the length is equal to the number of enabled products and each value corresponds to the photo count
# 4. Query 4 for getting the templates associated with a particular product 





class DataBase(object):
    """Class to handle the Sqlite Database.
    The following attributes are available for use in by settings menu and start up configurations:

    settings key value pair
    :attr watermarkpath: This is the logo path
    :type watermarkpath: string
    :attr videopath: video path for playback on startup
    :type videopath: str
    :attr capture_choices: possible choices of capture numbers which is got from the number of products. A tuple of photo count
    :type capture_choices: tuple: if length of tuple is more than 3, create overflow display to preview products
    :attr capture_nbr: This is from photo count, the number of images on a photo/template of a product
    :type capture_nbr: int
    :attr product_length: This is the number of enabled products
    :type product_length: int


    :attr template_number: The number of templates associated with a particular product
    :type template_number: int: if templates number is more than 3, create overflow display to preview captured images with templates
    :attr coloured: This is whether or not there should be coloured option
    :type coloured: boolean:True or False
    :attr black_and_white: whether or not it should be black and white option
    :type black_and_white: boolean
    :attr session_length: how long a session should last
    :type session_length: float
    :attr session_type: This determines what products are available to the user. By default photos 
    :type session_type: str
    :attr price_per_session: price 
    :type price_per_session: float
    :attr reprint: whether the client should be able to reprint their photos or not
    :type reprint: boolean
    :attr price_per_print: the cost of each print. only available if reprint is true
    :type price_per_print: float 
    :attr reprint_number: the maximum number of reprints available per session
    :type reprint_number: int

    """
    def __init__(self):

        self.conn = None 
        self.cursor = None
        self.create_tables()
        
        # A list of all the settings it requires after querying the database on start up in a json
        self.settings = {}

        self.products = []
        self.enabled_products = []
        self.unenabled_products = []

        self.templates = []
        self.product_templates = {}

        self.enabled_product_templates = {}

    
    def _initialize_app_settings(self):
        # Create all the steps to query and initialize the settings that will be used in the app
        self.entity = self.get_entity()
        # self.get_products()
        # self.get_templates()
        self.get_settings()
        
    
    def __insert__(self, query, document):
        self.open()
        self.cursor.execute(query, document)
        self.close()

    def __update__(self, query, value):
        self.open()
        self.cursor.execute(query, value)
        self.close() 

    def __find__(self, feature):
        self.open()
        self.close()

    def __delete__(self):
        self.open()
        self.close()

    def reverse(self, tuple_name):
        return tuple_name[::-1]
        

    def get_entity(self):
        # Get al the details from the entity table
        self.open()
        self.cursor.execute("SELECT * FROM entity WHERE enabled=True AND id=True")
        entity = self.cursor.fetchall()
        self.close()
        if entity is not None:
            return entity[0]
        else:
            # Log error
            return
         


    def get_object(self, object_id=None):
        # Get objects associated with templates and products or any other item

        if object_id is None:
            # Log error saying that there must be a an object id
            return
        self.open()
        # Write a query to get all the objects from the database 
        self.cursor.execute("SELECT objectname, objectname, id FROM object;")
        self.objects = self.cursor.fetchall()
        if isinstance(object_id, int):
            self.cursor.execute("SELECT objecturl FROM object WHERE id=(?)",(object_id,))
            objectpath=self.cursor.fetchall()
            if objectpath is not None:
                objectpath=objectpath[0][0]
            else:
                return

        if isinstance(object_id, (list,tuple)):
            # object id can be a list of ids to be queried against the database or a single id
            objectpath = []
            for oid in object_id:
                self.cursor.execute("SELECT objecturl FROM object WHERE id=(?)", (oid,))
                objectpath = self.cursor.fetchall()
                objectpath.append(objectpath[0][0])   
            
        self.close()
        return objectpath
    
    def get_settings(self):
        # call get object on each item set to get the object from the disk and add it into a dictionary called the settings dictionary.
        # A list of things required
        # settings key value pair
        # :attr watermarkpath: This is the logo path
        # :type watermarkpath: string
        # :attr videopath: video path for playback on startup
        # :type videopath: str
        # :attr capture_choices: possible choices of capture numbers which is got from the number of products. A tuple of photo count
        # :type capture_choices: tuple: if length of tuple is more than 3, create overflow display to preview products
        # :attr capture_nbr: This is from photo count, the number of images on a photo/template of a product
        # :type capture_nbr: int
        # :attr product_length: This is the number of enabled products
        # :type product_length: int
        # :attr black_and_white: whether or not the photos taken should be available in black and white
        # :type black_and_white: boolean
        # :attr coloured: whether or not the photos taken should be available in coloured option
        # :type coloured: boolean
        # :attr background: The default background for every entity
        # :type background: str 

        # Ineffective method of building the dictionary but temporary fix for POC
        # get all the keys of the self.enabled_product_templates
        enabled_products = self.enabled_product_templates.keys()
        self.settings['videopath'] = self.get_object(self.entity[2])
        self.settings['watermarkpath'] = self.get_object(self.entity[6])
        self.settings['capture_nbr'] = self.get_object()
        self.settings['background'] = self.get_object(self.entity[7])
        self.settings['inmate_documents'], self.settings['documents_number'] = self.get_inmate_documents()
        self.settings['attempt_count'] = None
        self.settings['use_camera'] = True

    def get_passcode(self, passcode:str):
        self.cursor.execute("SELECT passcode FROM entity WHERE passcode=(?)",(passcode,))
        return self.cursor.fetchone()
    
    
    def get_decryption_key(self, table_name:str, decrypt_key:str):
        # When a document is clicked on the GUI, get its order number.
        # Use the order number and decrypt key columns to get the decryption key from the database
        self.cursor.execute("SELECT decrypt_key FROM " + table_name + " WHERE decrypt_key=(?)",(decrypt_key,))
        return self.cursor.fetchone()
    
    def get_column(self, table_name:str, column:str):
        self.cursor.execute("SELECT " + column + " FROM " + table_name)
        return self.cursor.fetchall()

    def get_record(self, table_name:str, column:str, column_value, status):
        # Get all the records from a table where field conditions meet certain requirements
        self.cursor.execute("SELECT * FROM " + table_name + " WHERE " + column +"=(?) AND status=(?)",(column_value, status))
        return self.cursor.fetchall()
    
    def get_table(self, table_name:str, condition=None):
        if condition:
            self.cursor.execute("SELECT * FROM " + table_name + " WHERE status=(?)", (condition,))
        else:
            self.cursor.execute("SELECT * FROM " + table_name)
        return self.cursor.fetchall()

    def get_inmate_documents(self):
        self.open()
        # Query table to get inmate numbers
        inmate_documents = {}
        # use this on the login page
        documents = self.get_table("Documents")
        number_of_documents = len(documents)

        # use this list to build dictionary
        # Make this list a set
        inmate_number_list = self.get_column("Documents", "inmate_number")
        unique_inmate_number_list = list(set(inmate_number_list))
        
        for inmate_number in unique_inmate_number_list:
            docs = self.get_record("Documents", "inmate_number", inmate_number[0], "ready")
            inmate_documents[inmate_number[0]] = docs
        self.close()
        return inmate_documents, number_of_documents

    def create_tables(self):
        # create sql tables if the don't exists
        self.open()
        for table in create_tables:
            self.cursor.execute(table) 
        self.close()


    def open(self):
        # open connection and return a cursor
        try:
            self.conn = sqlite3.connect(DB_PATH)
        except:
            # Log the error
            LOGGER.error("Could not open a connection to the database")
            return
        self.cursor = self.conn.cursor()


    def close(self):
        # Close connection if it exists
        if self.conn is None:
            return
        self.conn.commit()
        self.conn.close()


