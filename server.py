from flask import Flask
from flask import request
from flask_debugtoolbar import DebugToolbarExtension
from flask import render_template
from flask import jsonify
import asyncio
import asyncpg
from os.path import join, dirname
from dotenv import load_dotenv
from resources import queries
import os
import sys


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
 
# Accessing variables.
DBPASS = os.getenv('DBPASS')
DBHOST = os.getenv('DBHOST')
DBUSER= os.getenv('DBUSER')
DBDATABASE= os.getenv('DBDATABASE')

loop = asyncio.get_event_loop()
db = None
app = Flask(__name__)
 
app.config['SECRET_KEY'] = 'some random string'
app.debug = True
#toolbar = DebugToolbarExtension(app)


language_codes = {"en": "English", "de": "German", "fr": "French", "cs": "Czech", "zh": "Chinese", "it": "Italian", "ja": "Japanese", "ko": "Korean", "pl": "Polish", "pt": "Portuguese", "ru": "Russian", "es": "Spanish"}
valid_regions = ["USA", "Europe", "Japan", "Asia", "Australia", "France", "Germany", "Spain", "Italy", "UK", "Netherlands", "Sweden", "Russia", "China", "Korea", "Hong Kong", "Taiwan", "Brazil", "Canada", "Japan, USA", "Japan, Europe", "USA, Europe", "Europe, Australia", "Japan, Asia", "UK, Australia", "World", "Region-Free", "Other"]



def buildTable(records):
	table = '<table id="games_returned" class="game_selection"><tr id="found_games" style="text-align:left;">'
	table += '<th>Select</th>'
	for field in records[0].keys():
		if field != 'id':
			if field == "platform":
				table += f'<th style="text-align:center";>{field}</th>'
			else:
				table += f'<th>{field}</th>'			
	table += "</tr>"

	for r in records:
		table += "<tr>"
		table += f'<td><input class="select_game" type="button" style="background-color:coral;color:black;padding:.01px 9px;border-radius: 100%;" data-value="{r["id"]}"/></td>'
		for v in r.values():
			if type(v) != int:
				table += f"<td>{v}</td>"
		table += "</tr>"
	
	table += "</table>"

	return table

async def initDB():
	credentials = {"user": DBUSER, "password": DBPASS, "database": DBDATABASE, "host": DBHOST}
	global db 
	db = await asyncpg.create_pool(**credentials)
	return

async def createDescription(gameTitle, platform):
	async with db.acquire() as conn:
		game = await conn.fetch("SELECT platform AS Platform, name AS Name, id FROM games WHERE name ILIKE $1 AND platform ILIKE $2 ORDER BY platform, name LIMIT 5;", f"%{gameTitle}%", f"%{platform}%")
		if game == None:
			return "No Game Found!"
		else:
			return {'val': buildTable(game), 'game': game[0]['id']}

@app.route('/', methods = ['POST', 'GET'])
def hello_world():
	if request.method == 'POST':
		response = jsonify({'val': request.form['action']})
		response.headers.add('Access-Control-Allow-Origin', '*')
		user = request.form['action']
		return response
	return render_template('index.html', title='Welcome', username="User")

@app.route('/data', methods = ['POST', 'GET'])
def load_response():
	if request.method == 'POST':
		response = jsonify(loop.run_until_complete(createDescription(request.form['name'], "")))
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	return "error"

async def queryDetails(gameID):
	async with db.acquire() as conn:
		files = await conn.fetch(queries.SELECTDETAILS, int(gameID))
		if len(files) == 0:
			releases = await conn.fetch(queries.TESTFORRELEASES, int(gameID))
			if len(releases) == 0:
				return jsonify({'status': 1, "msg": "That game has no sources or releases!"})
			else:
				url = f"https://datomatic.no-intro.org/index.php?page=show_record&s={releases[0]['platform_id']}&n={releases[0]['archive_number']}"
				return jsonify({'status': 1, "msg": f"That game has no sources but a release was found.\nYou may be able to manually enter the info from the address below:\n{url}"})
		else:
			fileString = ""
			for f in files:
				fileString += "File: [b]"
				if f["forcename"]:
					fileString += f["forcename"]
				elif f["extension"]:
					fileString += f'{f["name"]}.{f["extension"]}'
				else:
					fileString += f["file_id"]

				fileString += f'[/b] | CRC32: [b]{f["crc32"]}[/b] | MD5: [b]{f["md5"]}[/b] | SHA-1: [b]{f["sha1"]}[/b] \n'

		f = files[0]
		desc = f"[align=center][b]{f['name']}[/b]\n\nVerified against No Intro Checksums [url=https://datomatic.no-intro.org/index.php?page=show_record&s={f['platform_id']}&n={f['archive_number']}]Datomatic - {f['company']} - {f['platform']}[/url]\n{fileString}[/align]"

		if ',' in f["languages"]:
			lang = "Multi-Language"
		else:
			try:
				lang = language_codes[f["languages"].lower()]
			except KeyError:
				lang = "Other"

		if f["regions"] in valid_regions:
			region = f["regions"]
		else:
			region = "Other"

		return {'status': 0, 'description': desc, 'year': str(f["year"]), "name": f["name"], "region": region, "lang": lang}


@app.route('/details', methods = ['POST', 'GET'])
def get_details():
	if request.method == 'POST':
		response = jsonify(loop.run_until_complete(queryDetails(request.form['id'])))
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
		
	return "error"

@app.route('/file', methods = ['POST', 'GET'])
def process_details():
	if request.method == 'POST':
		# C:\fakepath\Bosses Forever 2.Bro (World) (v2.23).torrent
		name = request.form['name'][12:-8]
		table = loop.run_until_complete(createDescription(name, ""))
		fields = loop.run_until_complete(queryDetails(table['game']))
		response = jsonify(table | fields)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
		
	return "error"



if __name__ == '__main__':
	loop.run_until_complete(initDB())
	print("initialized DB")
	app.run(host='0.0.0.0', port=5000)