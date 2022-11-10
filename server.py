from flask import Flask
from flask import request
from flask_debugtoolbar import DebugToolbarExtension
from flask import render_template
from flask import jsonify
from helpers import queries
import sqlite3

db = sqlite3.connect(r'resources/nointro.db', detect_types = sqlite3.PARSE_DECLTYPES, check_same_thread=False)
db.row_factory = sqlite3.Row 
db.execute('PRAGMA journal_mode=wal;')

app = Flask(__name__)
 
app.config['SECRET_KEY'] = 'some random string'
app.debug = True
#toolbar = DebugToolbarExtension(app)


language_codes = {"en": "English", "de": "German", "fr": "French", "cs": "Czech", "zh": "Chinese", "it": "Italian", "ja": "Japanese", "ko": "Korean", "pl": "Polish", "pt": "Portuguese", "ru": "Russian", "es": "Spanish"}
valid_regions = ["USA", "Europe", "Japan", "Asia", "Australia", "France", "Germany", "Spain", "Italy", "UK", "Netherlands", "Sweden", "Russia", "China", "Korea", "Hong Kong", "Taiwan", "Brazil", "Canada", "Japan, USA", "Japan, Europe", "USA, Europe", "Europe, Australia", "Japan, Asia", "UK, Australia", "World", "Region-Free", "Other"]



def buildTable(records):
	if len(records) == 0:
		return 1

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
		for v in dict(r).values():
			if type(v) != int:
				table += f"<td>{v}</td>"
		table += "</tr>"
	
	table += "</table>"

	return table

def createDescription(gameTitle, platform):
	conn = db.cursor()
	conn.execute("SELECT platform AS Platform, name AS Name, id FROM games WHERE name LIKE ? AND platform LIKE ? ORDER BY platform, name LIMIT 5;", (f"%{gameTitle}%", f"%{platform}%"))
	game = conn.fetchall()
	if len(game) == 0:
		return {'val': None, 'game': -1}
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
		response = jsonify(createDescription(request.form['name'], ""))
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
	return "error"

def queryDetails(gameID):
	conn = db.cursor()
	conn.execute(queries.SELECTDETAILS, (int(gameID),))
	files = conn.fetchall()
	if len(files) == 0:
		conn.execute(queries.TESTFORRELEASES, (int(gameID),))
		releases = conn.fetchall() 
		
		if len(releases) == 0:
			return {'status': 1, "msg": "That game has no sources or releases!"}
		else:
			url = f"https://datomatic.no-intro.org/index.php?page=show_record&s={releases[0]['platform_id']}&n={releases[0]['archive_number']}"
			return {'status': 1, "msg": f"That game has no sources but a release was found.\nYou may be able to manually enter the info from the address below:\n{url}"}
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

	return {'status': 0, 'description': desc, 'year': str(f["year"].year), "name": f["name"], "region": region, "lang": lang}


@app.route('/details', methods = ['POST', 'GET'])
def get_details():
	if request.method == 'POST':
		response = jsonify(queryDetails(request.form['id']))
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
		
	return "error"

@app.route('/file', methods = ['POST', 'GET'])
def process_details():
	if request.method == 'POST':
		# C:\fakepath\Bosses Forever 2.Bro (World) (v2.23).torrent
		name = request.form['name'][12:-8]
		table = createDescription(name, "")
		fields = queryDetails(table['game'])
		response = jsonify(table | fields)
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
		
	return "error"



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)