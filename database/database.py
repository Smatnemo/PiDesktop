# This script is only run once on start up to create an sqlite database
import sqlite3
import os.path as osp



DB_PATH = "/home/pi/cpb.db"

# Database quries
create_product_table = """
CREATE TABLE IF NOT EXISTS 'product' (
  'product_id' bigint PRIMARY KEY,
  'enabled' tinyint(1) NOT NULL,
  'name' varchar(50),
  'default_background_img' varchar(255) NOT NULL,
  'photo_count' int,
  'created_by' bigint NOT NULL,
  'created_on' datetime NOT NULL,
  FOREIGN KEY ('default_background_img') REFERENCES 'Object' ('id')
);
"""

create_product_photos_table = """
CREATE TABLE IF NOT EXISTS 'product_photos' (
  'product_photo_id' bigint PRIMARY KEY,
  'photo_order' int NOT NULL,
  'product_id' bigint NOT NULL,
  'start_coord_x' int NOT NULL,
  'start_coord_y' int NOT NULL,
  'width' int NOT NULL,
  'height' int NOT NULL,
  'created_by' bigint NOT NULL,
  'created_on' datetime NOT NULL,
  FOREIGN KEY ('product_id') REFERENCES 'product' ('product_id')
);
"""
create_templates_table = """
CREATE TABLE IF NOT EXISTS 'templates' (
  'template_id' bigint PRIMARY KEY,
  'enabled' bool,
  'template_order' int,
  'product_id' bigint NOT NULL,
  'entity_id' bigint NOT NULL,
  'label' varchar(255) NOT NULL, 
  'background_img' varchar(255) NOT NULL,
  'price' decimal(10,0) NOT NULL,
  'currency' bigint NOT NULL,
  'run_on_date_range' tinyint(1) NOT NULL,
  'start_date' datetime NOT NULL,
  'end_time' datetime NOT NULL,
  'created_by' bigint NOT NULL,
  'created_on' datetime NOT NULL,
  FOREIGN KEY ('product_id') REFERENCES 'product' ('product_id'),
  FOREIGN KEY ('background_img') REFERENCES 'Object' ('id')
);
"""
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

create_tables = [create_object_table, create_product_table, create_product_photos_table, create_templates_table, create_entity_table]


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
        self.get_products()
        self.get_templates()
        self.get_settings()
        
    
    def __insert__(self):
        self.open()
        self.close()

    def __update__(self):
        self.open()
        self.close() 

    def __find__(self, feature):
        self.open()
        self.close()

    def __delete__(self):
        self.open()
        self.close()

    def reverse(self, tuple_name):
        return tuple_name[::-1]
        
    def get_capture_choices(self):
        enabled_products = self.enabled_product_templates.keys()
        capture_options = []
        for enabled_product in enabled_products:
            capture_options.append(enabled_product[4])

        return self.reverse(tuple(set((capture_options))))

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


    def get_products(self):
        # Get a list of all the products from the database
        self.open()
        self.cursor.execute("SELECT * FROM product")
        self.products = self.cursor.fetchall()

        self.cursor.execute("SELECT * FROM product WHERE enabled=True")
        self.enabled_products = self.cursor.fetchall()
        if self.enabled_products:
            # Stop app and ask for enabled products
            pass

        self.cursor.execute("SELECT * FROM product WHERE enabled=False")
        self.unenabled_products = self.cursor.fetchall()

        self.close()


    def get_templates(self):
        """
        :attr product_id: the id of the product
        :type product_id: int
        """
        self.open()
        self.cursor.execute("SELECT * FROM templates")
        self.templates = self.cursor.fetchall()

        # get a list of enabled templates
        self.cursor.execute("SELECT * FROM templates WHERE enabled=True")
        self.enabled_templates = self.cursor.fetchall()

        # get a list of unenabled templates
        self.cursor.execute("SELECT * FROM templates WHERE enabled=False")
        self.unenabled_templates = self.cursor.fetchall()

        # get a unique set of ids from products list
        self.product_ids = []
        self.product_names = []
        if self.products is not None:
            # iterate through the list of products and get the product_ids and names
            # use the product id to get all the templates associated with a product: enabled or not
            # Store values in a dictionary with the name of the product as the key and a list of all its templates as the value
            for product in self.products:
                self.product_ids.append(product[0])
                self.product_names.append(product[2])
                self.cursor.execute("SELECT * FROM templates WHERE product_id=(?)", (product[0],))
                templates = self.cursor.fetchall()
                if templates:
                    self.product_templates[product] = templates
                else: 
                    # Log info associated with the product id and name
                    # product[0] - The product id
                    # product[2] - The product name
                    continue

                # Create condition to check if the product is enbled, if so, create another dictionary for enabled products and themplates
                if product[1] == 1:
                    # Go through all its templates to check for enabled templates. 
                    # Add enabled templates to the list below
                    enabled_templates = []
                    for template in templates:
                        if template[1] == 1:
                            enabled_templates.append(template)
                        else:
                            # template[0] - template_id
                            # product[0] - product_id
                            # Log these stating clearly that this template associated with this product is not enabled
                            pass

                    # if enabled_templates list is empty. 
                    if not enabled_templates:
                        # Create log stating that none of the templates associated with product is enabled.
                        # exit this condition and return to the initial for loop
                        continue

                    # Use this to set up pibooth
                    self.enabled_product_templates[product] = enabled_templates
                    
        # create attributes to hold modified list of enabled templates associated with enabled products
        if self.enabled_product_templates is None:
            # Show output saying there are no enabled templates associated with enabled products
            # Show in error log that there must be at least one enabled template associated with at least one enabled product
            # There must be enabled templates and products for photo booth to initialize
            pass
    
        self.close()


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
        self.settings['capture_choices'] = self.get_capture_choices()
        self.settings['capture_nbr'] = self.get_object()
        self.settings['product_length'] = self.get_object()
        self.settings['enabled_product_templates'] = self.enabled_product_templates
        self.settings['product_templates'] = self.product_templates
        self.settings['black_and_white'] = True
        self.settings['coloured'] = True
        self.settings['background'] = self.get_object(self.entity[7])

        

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
            print("Could not open a connection to the database")
            return
        self.cursor = self.conn.cursor()


    def close(self):
        # Close connection if it exists
        if self.conn is None:
            return
        self.conn.commit()
        self.conn.close()


