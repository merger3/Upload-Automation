SELECT 
	*
FROM 
	games INNER JOIN releases ON games.id = releases.game_id 
WHERE 
	games.id = 1463357923;


SELECT 
	COUNT(1)
FROM 
	games INNER JOIN sources ON games.id = sources.game_id
	INNER JOIN files on files.source_id = sources.id
WHERE 
	games.id = 1463357923;


-- 6221
WITH single AS (
SELECT
	DISTINCT ON (games.id)
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
WHERE games.id = 1463357923
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
	EXTRACT(YEAR FROM single.d_date) AS year,
	files.*
FROM
	single INNER JOIN files ON files.source_id = single.source_id;



SELECT
	games.platform,
	games.name,
	sources.source_id
FROM 
	games INNER JOIN sources ON games.id = sources.game_id
WHERE 
	d_date IS NULL;