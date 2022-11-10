CREATE TABLE IF NOT EXISTS games (
	id BIGINT PRIMARY KEY,
	name TEXT,
	company TEXT,
	platform TEXT,
	platform_id INT,
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

CREATE TABLE IF NOT EXISTS serials (
	serial_type TEXT,
	code 		TEXT,
	source_id 	BIGINT,
	PRIMARY KEY(serial_type, code, source_id),
	FOREIGN KEY(source_id) REFERENCES sources(id) ON DELETE CASCADE
);

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