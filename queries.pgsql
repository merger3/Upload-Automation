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