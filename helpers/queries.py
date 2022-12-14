CREATEGAMESTABLE = """
CREATE TABLE IF NOT EXISTS games (
	id BIGINT PRIMARY KEY,
	name TEXT,
	company TEXT,
	platform TEXT,
	platform_id INT,
	archive_number VARCHAR,
	clone VARCHAR,
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
	company,
	platform,
	platform_id,
	archive_number, 
	clone, 
	regparent, 
	game_name, 
	alt_name, 
	regions, 
	languages, 
	version, 
	devstatus
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

INSERTINTOSERIALS = """
INSERT INTO serials (
	serial_type,
	code,
	source_id
	) VALUES (?, ?, ?);
"""

SELECTDETAILS = """
WITH single AS (
SELECT
	MIN(sources.source_id),
	games.archive_number,
	games.name,
	games.platform,
	games.company,
	games.platform_id,
	games.regions,
	games.languages,
	sources.d_date,
	sources.source_id as s_id,
	sources.id as source_id,
	games.id as games_id
FROM 
	games INNER JOIN sources ON games.id = sources.game_id
	INNER JOIN files ON files.source_id = sources.id 
WHERE games.id = ?
GROUP BY 
	games.id
ORDER BY 
	games.id,
	sources.source_id
)

SELECT
	single.games_id,
	single.archive_number,
	single.s_id,
	single.name,
	single.platform,
	single.company,
	single.regions,
	single.languages,
	single.platform_id,
	single.d_date AS year,
	files.*
FROM
	single INNER JOIN files ON files.source_id = single.source_id;
"""

TESTFORRELEASES = """
SELECT 
	*
FROM 
	games INNER JOIN releases ON games.id = releases.game_id 
WHERE 
	games.id = ?;
"""