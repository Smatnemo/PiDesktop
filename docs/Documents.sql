BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Documents" (
	"id"	INTEGER,
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
	"document_id"	INTEGER NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "Documents" ("id","document_path","width","height","created_by","downloaded_on","deleted_on","decrypt_key","num_of_pages","inmate_number","signature","status","printed","decrypted","encrypted_file_checksum","original_file_checksum","inmate_photo","original_extension","printed_date","inmate_name","title","document_id") VALUES (612,'docs/file_340.pdf',210,297,0,0,0,'111111',1,12345678,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'Edward','DS-RX1_PrinterDriverInstruction_For7,8_V1.11_English',340),
 (613,'docs/file_341.pdf',210,297,0,0,0,'111111',1,12345678,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'James','LIAM-order-1105',341),
 (614,'docs/file_342.pdf',210,297,0,0,0,'111111',1,87654321,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'Edward','Glenbervie-Christmas-Brochure-2023',342),
 (615,'docs/file_347.pdf',210,297,0,0,0,'111111',1,87654321,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'Edward','test',347),
 (616,'docs/file_348.pdf',210,297,0,0,0,'111111',1,87654321,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'Edward','LIAM-order-1106',348),
 (617,'docs/file_349.pdf',210,297,0,0,0,'111111',1,24682468,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'Edward','LIAM-order-1106',349),
 (618,'docs/file_350.pdf',210,297,0,0,0,'111111',2,13571357,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'Edward','test',350),
 (619,'docs/file_351.pdf',210,297,0,0,0,'111111',1,13571357,NULL,'ready',0,0,'2e6148d58b0a03617deee8d2f623e8c7b3e50f3646cf6e24b454bba2a50bf68a','bc83ca713f0dc8a9338daa49cc397982b0aa081f4428ad1180c49df14a72c565',NULL,'pdf',NULL,'Edward','LIAM-order-1105',351);
COMMIT;
