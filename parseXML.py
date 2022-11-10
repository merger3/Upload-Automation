import datetime
import re
import asyncio
import asyncpg
import os
import sys
import platform
from os.path import join, dirname
from dotenv import load_dotenv
from xml.dom.minidom import parse, parseString
from datetime import datetime
import zlib
from resources import queries

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
 
# Accessing variables.
DBPASS = os.getenv('DBPASS')
DBHOST = os.getenv('DBHOST')
DBUSER= os.getenv('DBUSER')
DBDATABASE= os.getenv('DBDATABASE')


async def main():
	if platform.system() == "Windows":
		xmls = os.getcwd() + '\\xmls'
	else:
		xmls = os.getcwd() + '/xmls'

	credentials = {"user": DBUSER, "password": DBPASS, "database": DBDATABASE, "host": DBHOST}
	db = await asyncpg.create_pool(**credentials)
	
	
	async with db.acquire() as conn:
		# Reset DB
		await conn.execute("DROP TABLE IF EXISTS games CASCADE;")
		await conn.execute("DROP TABLE IF EXISTS sources CASCADE;")
		await conn.execute("DROP TABLE IF EXISTS serials CASCADE;")
		await conn.execute("DROP TABLE IF EXISTS releases CASCADE;")
		await conn.execute("DROP TABLE IF EXISTS files CASCADE;")

		# Initialize tables
		await conn.execute(queries.CREATEGAMESTABLE)
		await conn.execute(queries.CREATESOURCESTABLE)
		await conn.execute(queries.CREATESERIALSTABLE)
		await conn.execute(queries.CREATERELEASESTABLE)
		await conn.execute(queries.CREATEFILESTABLE)
		for root, dirs, files in os.walk(xmls):
			for i in files:
				with open(os.path.join(root, i)) as file:
					print(os.path.join(root, i))
					await parseXML(conn, file, i)




async def np(arg: str, format="str"):
	if arg in ["", "P", "!unknown", "!none", "!n/a", "!none!"]: 
		return None
	else:
		if format == "int":
			try:
				return int(arg)
			except TypeError:
				return 1
		elif format == "datetime":
			try:
				return datetime.strptime(arg, "%Y-%m-%d")
			except ValueError:
				return None

		return arg

async def parseXML(conn, fileObj, fileName):
	document = parse(fileObj)
	
	game_vals = {}
	source_vals = {}
	release_vals = {}
	file_vals = {}

	


	

	game_vals["platform_id"] = int(fileName[:fileName.find(' ')])
	game_vals["company"] = fileName[fileName.find(' ') + 1:fileName.find(" - ")]
	game_vals["platform"] = fileName[fileName.find(" - ") + 3:-4]
	games = document.getElementsByTagName("game")
	for game in games:
		game_vals["release_name"] = game.getAttribute("name")
		for child in game.childNodes:
			if child.nodeName == "archive":
				game_vals["archive_number"] = await np(child.getAttribute("number"))
				game_vals["clone"]          = await np(child.getAttribute("clone"))
				game_vals["regparent"]      = await np(child.getAttribute("regparent"))
				game_vals["game_name"]      = child.getAttribute("name")
				game_vals["alt_name"]       = child.getAttribute("name_alt")
				game_vals["region"]         = await np(child.getAttribute("region"))
				game_vals["languages"]      = await np(child.getAttribute("languages"))
				game_vals["version"]        = await np(child.getAttribute("version"))
				game_vals["devstatus"]      = await np(child.getAttribute("devstatus"))
				
				game_vals["id"] 			= zlib.crc32(bytes(game_vals["archive_number"] + game_vals["release_name"], 'utf-8'))

				# while True:
				# 	try:
				# 		await conn.execute(queries.INSERTINTOGAMES, game_vals["id"], game_vals["release_name"], game_vals["platform"], game_vals["archive_number"], game_vals["clone"], game_vals["regparent"], game_vals["game_name"], game_vals["alt_name"], game_vals["region"], game_vals["languages"], game_vals["version"], game_vals["devstatus"])
				# 	except asyncpg.UniqueViolationError:
				# 		game_vals["id"] = zlib.crc32(bytes(str(game_vals["id"]), 'utf-8'))
				# 	else:
				# 		break

				try:
					await conn.execute(queries.INSERTINTOGAMES, game_vals["id"], game_vals["release_name"], game_vals["company"], game_vals["platform"], game_vals["platform_id"], game_vals["archive_number"], game_vals["clone"], game_vals["regparent"], game_vals["game_name"], game_vals["alt_name"], game_vals["region"], game_vals["languages"], game_vals["version"], game_vals["devstatus"])
				except asyncpg.UniqueViolationError:
					print(f"Unable to add {game_vals['game_name']} due to duplicate ID")
				else:
					pass
					# print("Added Game")

			elif child.nodeName == "source":
				for info in child.childNodes:
					if info.nodeName == "details":
						source_vals["source_id"]			   = int(info.getAttribute("id"))
						source_vals["game_id"]		   = game_vals["id"]
						source_vals["section"]		   = await np(info.getAttribute("section"))
						source_vals["d_date"]		   = await np(info.getAttribute("d_date"), format="datetime")
						source_vals["r_date"]   	   = await np(info.getAttribute("r_date"), format="datetime")
						source_vals["regions"]		   = await np(info.getAttribute("region"))
						source_vals["dumper"]   	   = await np(info.getAttribute("dumper"))
						source_vals["project"]		   = await np(info.getAttribute("project"))
						source_vals["original_format"] = await np(info.getAttribute("originalFormat"))
						source_vals["comment"]		   = await np(info.getAttribute("comment*"))
						source_vals["tool"]			   = await np(info.getAttribute("tool"))
						source_vals["id"] 			= zlib.crc32(bytes(str(source_vals["source_id"]) + str(source_vals["game_id"]), 'utf-8'))


						try:
							await conn.execute(queries.INSERTINTOSOURCES, source_vals["id"], source_vals["source_id"], source_vals["game_id"], source_vals["section"], source_vals["d_date"], source_vals["r_date"], source_vals["regions"], source_vals["dumper"], source_vals["project"], source_vals["original_format"], source_vals["comment"], source_vals["tool"])
						except asyncpg.UniqueViolationError:
							print(f"Unable to add source with id {source_vals['source_id']} from game {game_vals['game_name']} due to duplicate ID")
						else:
							pass
							#print("Added Source")


					elif info.nodeName == "serials":
						for attrName, attrValue in info.attributes.items():
							try:
								await conn.execute(queries.INSERTINTOSERIALS, attrName[:attrName.find('_')], attrValue, source_vals["id"])
							except asyncpg.UniqueViolationError:
								print(f"Unable to add serial {attrName} ({attrValue}) to game {game_vals['game_name']} due to duplicate ID")
							else:
								pass
								# print("Added Serial")
							


					elif info.nodeName == "file":
						file_vals["file_id"] 		= await np(info.getAttribute("id"), format="int")
						file_vals["source_id"] 	= source_vals["id"]
						file_vals["extension"] 	= await np(info.getAttribute("extension"))
						file_vals["forcename"] 	= await np(info.getAttribute("forcename"))
						file_vals["size"] 		= await np(info.getAttribute("size"), format="int")
						file_vals["crc32"] 		= await np(info.getAttribute("crc32"))
						file_vals["md5"] 		= await np(info.getAttribute("md5"))
						file_vals["sha1"] 		= await np(info.getAttribute("sha1"))
						file_vals["serial"]		= await np(info.getAttribute("serial"))
						file_vals["format"] 	= await np(info.getAttribute("format"))
						file_vals["id"] 			= zlib.crc32(bytes(str(file_vals["file_id"]) + str(file_vals["source_id"]), 'utf-8'))

						try:
							await conn.execute(queries.INSERTINTOFILES, file_vals["id"], file_vals["file_id"], file_vals["source_id"], file_vals["extension"], file_vals["forcename"], file_vals["size"], file_vals["crc32"], file_vals["md5"], file_vals["sha1"], file_vals["serial"], file_vals["format"])
						except asyncpg.UniqueViolationError:
							print(f"Unable to add file with id {file_vals['file_id']} from game {game_vals['game_name']} due to duplicate ID")
						else:
							pass
							# print("Added File")


			elif child.nodeName == "release":
				for release_info in child.childNodes:
					if release_info.nodeName == "details":
						release_vals["release_id"] 		= await np(release_info.getAttribute("id"), format="int")
						release_vals["game_id"] 		= game_vals["id"]
						release_vals["dirname"] 		= await np(release_info.getAttribute("dirname"))
						release_vals["rominfo"] 		= await np(release_info.getAttribute("id"))
						release_vals["nfoname"] 		= await np(release_info.getAttribute("nfoname"))
						release_vals["nfosize"] 		= await np(release_info.getAttribute("nfosize"), format="int")
						release_vals["nfocrc"] 			= await np(release_info.getAttribute("nfocrc"))
						release_vals["archivename"] 	= await np(release_info.getAttribute("archivename"))
						release_vals["originalformat"] 	= await np(release_info.getAttribute("originalformat"))
						release_vals["release_date"] 	= await np(release_info.getAttribute("date"), format="datetime")
						release_vals["group"] 			= await np(release_info.getAttribute("group"))
						release_vals["region"] 			= await np(release_info.getAttribute("region"))
						release_vals["origin"]			= await np(release_info.getAttribute("origin"))
						release_vals["id"] 			= zlib.crc32(bytes(str(release_vals["release_id"]) + str(release_vals["game_id"]), 'utf-8'))

					elif release_info.nodeName == "serials":
						release_vals["serial_code"] 	= await np(release_info.getAttribute("media_serial1"))


				try:
					await conn.execute(queries.INSERTINTORELEASES, release_vals["id"], release_vals["release_id"], release_vals["game_id"], release_vals["dirname"], release_vals["rominfo"], release_vals["nfoname"], release_vals["nfosize"], release_vals["nfocrc"], release_vals["archivename"], release_vals["originalformat"], release_vals["release_date"], release_vals["group"], release_vals["region"], release_vals["origin"], release_vals["serial_code"])
				except asyncpg.UniqueViolationError:
					print(f"Unable to add release with id {release_vals['release_id']} from game {game_vals['game_name']} due to duplicate ID")
				else:
					pass
					# print("Added Release")

if __name__ == '__main__':
	asyncio.run(main())						