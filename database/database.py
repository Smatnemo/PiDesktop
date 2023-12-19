# This script is only run once on start up to create an sqlite database
import sqlite3
import os.path as osp
from LDS.utils import LOGGER
from LDS import package_dir

DB_PATH = osp.join(package_dir,"data/legal.db")
LOGGER.info("Database path: {}".format(DB_PATH))
# print("Database Path:", DB_PATH)

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
CREATE TABLE IF NOT EXISTS "Documents" (
	"id"	INTEGER PRIMARY KEY AUTOINCREMENT,
	"document_path"	VARCHAR(128) NOT NULL,
	"width"	int,
	"height"	int,
	"created_by"	bigint NOT NULL,
	"downloaded_on"	datetime NOT NULL,
	"deleted_on"	datetime NOT NULL,
	"decrypt_key"	VARCHAR(20) NOT NULL,
	"num_of_pages"	int,
	"inmate_number"	int,
	"signature"	BLOB,
	"status"	VARCHAR(127),
	"printed"	tinyint(1),
	"decrypted"	tinyint(1),
	"encrypted_file_checksum"	VARCHAR(128),
	"original_file_checksum"	VARCHAR(128),
	"inmate_photo"	BLOB,
	"original_extension"	VARCHAR(10),
	"printed_date"	datetime,
	"inmate_name"	VARCHAR(128),
	"title"	VARCHAR(128),
	"document_id"	INTEGER NOT NULL
);
"""

create_languages_table = """
CREATE TABLE IF NOT EXISTS 'Languages' (
  `language_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `iso-code` varchar(3) NOT NULL DEFAULT '',
  `description` varchar(20) NOT NULL DEFAULT '',
  `icon` varchar(20) NOT NULL DEFAULT '',
  `enabled` tinyint(1) NOT NULL DEFAULT '0'
);"""

create_questions_table = """
CREATE TABLE IF NOT EXISTS `Questions` (
  `question_id` bigint NOT NULL PRIMARY KEY,
  `sequence_number` int NOT NULL,
  `created_date` DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

create_questions_answers_table = """
CREATE TABLE IF NOT EXISTS `Questions_answers` (
  `question_answer_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `question_id` bigint DEFAULT NULL,
  `answer` int DEFAULT NULL,
  `object_id` bigint DEFAULT NULL,
  `answer_date` DATETIME DEFAULT CURRENT_TIMESTAMP
);"""
create_unique_index = """
CREATE UNIQUE INDEX 'question_id' on 'Questions_Answers' ('question_id', 'object_id');
"""

create_questions_text_table = """
CREATE TABLE IF NOT EXISTS `Questions_text` (
  `questions_text_id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `question_id` bigint NOT NULL,
  `language_id` bigint NOT NULL,
  `question_text` text NOT NULL,
  FOREIGN KEY (`language_id`) REFERENCES `Languages` (`language_id`),
  FOREIGN KEY (`question_id`) REFERENCES `Questions` (`question_id`)
);"""


create_tables = [create_object_table, create_entity_table, create_documents_table, create_questions_answers_table, \
                 create_languages_table,create_questions_table, create_questions_text_table]

document_insert_query = """INSERT INTO 'Documents'
                                  (document_path, 
                                  width,
                                  height, 
                                  created_by,
                                  downloaded_on,
                                  deleted_on,
                                  decrypt_key, 
                                  num_of_pages, 
                                  inmate_number, 
                                  status, 
                                  printed, 
                                  decrypted,
                                  encrypted_file_checksum,
                                  original_file_checksum,
                                  original_extension,
                                  inmate_name,
                                  title,
                                  document_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

document_update_query = """UPDATE 'Documents'
                            SET printed = ?,
                                decrypted = 1,
                                status = 'printed',
                                inmate_photo= ?,
                                printed_date= date('now')
                            WHERE order_id= ? """

# Questions_Answers_insert_query = 
insert_questions_query ="""INSERT INTO `Questions` (
                                        `question_id`, 
                                        `sequence_number`, 
                                        `created_date`) VALUES (?, ?, ?);
"""
insert_languages_query = """INSERT INTO `Languages` (
                            `language_id`, 
                            `iso-code`, 
                            `description`, 
                            `icon`, 
                            `enabled`) VALUES (?, ?, ?, ?, ?);"""

insert_questions_text_query = """INSERT INTO `Questions_text` (
                            `questions_text_id`,
                            `question_id`,
                            `language_id`,
                            `question_text`,
                            ) VALUES (?, ?, ?, ?);"""
insert_questions_answer_query="""INSERT INTO `Questions_answers` (
                                            `question_id`, 
                                            `answer`, 
                                            `object_id`) VALUES (?, ?, ?);"""

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
    
    def get_column(self, table_name:str, column:str, condition):
        self.cursor.execute("SELECT " + column + " FROM " + table_name + " WHERE status=(?)", (condition,))
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

    def get_questions(self, language):
        self.open()
        questions = []
        # query = "SELECT * FROM Questions_text WHERE language_id=(?) AND question_id=(?)"
        query = """select Questions_text.* 
                    from Questions_text
                    left join Questions on Questions.question_id = Questions_text.question_id
                    left join Languages on Languages.language_id = Questions_text.language_id
                    where Questions_text.language_id = ?
                    order by Questions.sequence_number;"""
        self.cursor.execute(query, (language,)) 
        questions = self.cursor.fetchall()
        self.close()
        return questions

    def get_inmate_documents(self):
        self.open()
        # Query table to get inmate numbers
        inmate_documents = {}
        # use this on the login page
        documents = self.get_table("Documents")
        number_of_documents = len(documents)

        # use this list to build dictionary
        # Make this list a set
        inmate_number_list = self.get_column("Documents", "inmate_number", "ready")
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


