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
INSERT INTO "Documents" ("id","document_path","width","height","created_by","downloaded_on","deleted_on","decrypt_key","num_of_pages","inmate_number","signature","status","printed","decrypted","encrypted_file_checksum","original_file_checksum","inmate_photo","original_extension","printed_date","inmate_name","title","document_id") 
VALUES(612, 'docs/doc1.pdf', 210, 297, 0, '0', '0', '111111', 2, 12345678, NULL, 'ready', 0, 0, 'be00547f12c6fcba50b73ae820c1435bf5e914c53f4cb71cef5559b1950804af', '16a6aef32cbd724b4fc3ea89526b2d2452cf6fd72ef0232e658782c38383e45b', NULL, 'pdf', NULL, 'Joe', 'Legal Document', 340),
 (613, 'docs/doc2.pdf', 210, 297, 0, '0', '0', '111111', 3, 12345678, NULL, 'ready', 0, 0, '4b11d50777223be1325365cec4c38cc4c0e9b498b0f0f3654d8e01d767c6a60c', 'cdc6521946103570a1f0524a07f8222883e80b755758420905ae13bdf4549b3a', NULL, 'pdf', NULL, 'Joe', 'Police Narrative Report', 341),
 (614, 'docs/doc3.pdf', 210, 297, 0, '0', '0', '111111', 4, 87654321, NULL, 'ready', 0, 0, '3622ee0138d78ed8aea442f2b4c18f552e1b99126d2e041873415341768784a2', 'ca37325a6f138b22654ad79b03fd8c26899a31f856aa10adecea3481fe1c424e', NULL, 'pdf', NULL, 'Joe', 'Police Crime Report', 342);
COMMIT;

