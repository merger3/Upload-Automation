SELECT 
	* 
FROM 
	games INNER JOIN sources ON games.id = sources.game_id
	INNER JOIN files ON files.source_id = sources.id 
WHERE 
	games.archive_number = 82 AND sources.source_id = 611 
ORDER BY 
	games.name 
LIMIT 10;



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
WHERE games.platform = 'Acorn'
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
	single INNER JOIN files ON files.source_id = single.source_id
LIMIT 1000;