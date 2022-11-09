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


#  <table>
#   <tr>
#     <th>Company</th>
#     <th>Contact</th>
#     <th>Country</th>
#   </tr>
#   <tr>
#     <td>Alfreds Futterkiste</td>
#     <td>Maria Anders</td>
#     <td>Germany</td>
#   </tr>
#   <tr>
#     <td>Centro comercial Moctezuma</td>
#     <td>Francisco Chang</td>
#     <td>Mexico</td>
#   </tr>
# </table> 

def buildTable(records):
	table = '<table id="games_returned" class="game_selection"><tr id="found_games" style="text-align:left;">'
	table += '<th>Select</th>'
	for field in records[0].keys():
		if field != 'id':
			table += f"<th>{field}</th>"
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
			return buildTable(game)

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
		# game = loop.run_until_complete(createDescription(request.form['name'], request.form['platform']))
		game = loop.run_until_complete(createDescription(request.form['name'], ""))
		response = jsonify({'val': game})
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
		return render_template('table.html', title='Welcome', records=game)
	return "error"

async def queryDetails(releaseID):
	async with db.acquire() as conn:
		# desc = "[/b]\n" + game_id + "[/b]\n\nVerified against No Intro Checksums [url=" + params.discid + "]Datomatic - Nintendo - Nintendo 3DS (Digital) (CDN)[/url]\n" + content_text +"\nTo use these files, install them on a modified 3DS or install them to Citra. These files can be converted to CIA using a program listed on the [url=https://gbatemp.net/threads/batch-cia-3ds-decryptor-a-simple-batch-file-to-decrypt-cia-3ds.512385/page-3#post-9137481]gbatemp forums[/url] \n [url=https://i.postimg.cc/d3vRHC0j/image.png]Image of post provided here to ensure longevity[/url][/align]";
		game = await conn.fetchrow(queries.SELECTDETAILS, int(releaseID))
		if game == None:
			return "No Game Found!"
		else:
			return game["crc32"]


@app.route('/details', methods = ['POST', 'GET'])
def get_details():
	if request.method == 'POST':
		# game = loop.run_until_complete(createDescription(request.form['name'], request.form['platform']))
		game = loop.run_until_complete(queryDetails(request.form['id']))
		response = jsonify({'val': game})
		response.headers.add('Access-Control-Allow-Origin', '*')
		return response
		return render_template('table.html', title='Welcome', records=game)
	return "error"



if __name__ == '__main__':
	loop.run_until_complete(initDB())
	print("initialized DB")
	app.run(host='0.0.0.0', port=5000)