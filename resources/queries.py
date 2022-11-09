CREATEGAMESTABLE = """
CREATE TABLE IF NOT EXISTS games (
	id BIGINT PRIMARY KEY,
	name TEXT,
	platform TEXT,
	archive_number INT,
	clone INT,
	regparent TEXT,
	game_name TEXT,
	alt_name TEXT,
	regions TEXT,
	languages TEXT,
	version TEXT,
	devstatus TEXT
);
"""

CREATESOURCESTABLE = """
CREATE TABLE IF NOT EXISTS sources (
	id      		BIGINT PRIMARY KEY,
	source_id		INT,
	game_id 		BIGINT,
	section 		TEXT,
	d_date 			TIMESTAMP,
	r_date 			TIMESTAMP,
	regions 		TEXT,
	dumper 			TEXT,
	project 		TEXT,
	original_format TEXT,
	comment 		TEXT,
	tool 			TEXT,
	FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE
);
"""

CREATESERIALSTABLE = """
CREATE TABLE IF NOT EXISTS serials (
	serial_type TEXT,
	code 		TEXT,
	source_id 	BIGINT,
	PRIMARY KEY(serial_type, code, source_id),
	FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
);
"""

CREATERELEASESTABLE = """
CREATE TABLE IF NOT EXISTS releases (
	id 				BIGINT PRIMARY KEY,
	release_id		INT,
	game_id 		BIGINT,
	dirname 		TEXT,
	rominfo 		TEXT,
	nfoname 		TEXT,
	nfosize 		INT,
	nfocrc 			VARCHAR(8),
	archive_name 	TEXT,
	original_format TEXT,
	release_date 	TIMESTAMP,
	group_name 		TEXT,
	region 			TEXT,
	origin 			TEXT,
	serial_code 	TEXT,
	FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE
);
"""

CREATEFILESTABLE = """
CREATE TABLE IF NOT EXISTS files (
	id 			BIGINT PRIMARY KEY,
	file_id		INT,
	source_id 	BIGINT,
	extension 	TEXT,
	forcename	TEXT,
	size 		BIGINT,
	crc32 		VARCHAR(8),
	md5 		VARCHAR(32),
	sha1 		VARCHAR(40),
	serial_code TEXT,
	format 		TEXT,
	FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
);
"""

INSERTINTOGAMES = """
INSERT INTO games (
	id,
	name, 
	platform, 
	archive_number, 
	clone, 
	regparent, 
	game_name, 
	alt_name, 
	regions, 
	languages, 
	version, 
	devstatus
	) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);
"""

INSERTINTOSOURCES = """
INSERT INTO sources (
	id,
	source_id,	
	game_id, 		
	section, 		
	d_date, 			
	r_date, 			
	regions, 		
	dumper, 			
	project, 		
	original_format, 
	comment, 		
	tool	
	) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12);
"""

INSERTINTORELEASES = """
INSERT INTO releases (
	id,
	release_id,
	game_id,
	dirname,
	rominfo,
	nfoname,
	nfosize,
	nfocrc,
	archive_name,
	original_format,
	release_date,
	group_name,
	region,	
	origin,
	serial_code
	) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15);
"""


INSERTINTOFILES = """
INSERT INTO files (
	id,
	file_id,
	source_id,
	extension,
	forcename,
	size,
	crc32,
	md5,
	sha1,
	serial_code,
	format
	) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);
"""

INSERTINTOSERIALS = """
INSERT INTO serials (
	serial_type,
	code,
	source_id
	) VALUES ($1, $2, $3);
"""

SELECTDETAILS = """
WITH single AS (
SELECT
	DISTINCT ON (games.id)
	games.archive_number,
	games.name,
	sources.source_id as s_id,
	sources.id as source_id,
	games.id as games_id
FROM 
	games INNER JOIN sources ON games.id = sources.game_id
	INNER JOIN files ON files.source_id = sources.id 
WHERE games.id = $1
ORDER BY 
	games.id,
	sources.source_id
)

SELECT
	single.games_id,
	single.s_id,
	single.name,
	files.crc32
FROM
	single INNER JOIN files ON files.source_id = single.source_id;
"""