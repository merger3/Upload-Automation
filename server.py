from flask import Flask
from flask import request
from flask_debugtoolbar import DebugToolbarExtension
from flask import render_template
from flask import jsonify
import asyncio
import asyncpg
from os.path import join, dirname
from dotenv import load_dotenv
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
	table = "<table><tr>"
	for field in records[0].keys():
		table += f"<th>{field}</th>"
	table += "</tr>"

	for r in records:
		table += "<tr>"
		for v in r.values():
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
		game = await conn.fetch("SELECT name, platform FROM games WHERE name ILIKE $1 AND platform ILIKE $2 ORDER BY platform, name LIMIT 100;", f"%{gameTitle}%", f"%{platform}%")
		if game == None:
			return "No Game Found!"
		else:
			return buildTable(game)

@app.route('/', methods = ['POST', 'GET'])
def hello_world():
	if request.method == 'POST':
		print("here")
		response = jsonify({'some': 'data'})
		response.headers.add('Access-Control-Allow-Origin', '*')
		user = request.form['action']
		return response
	return render_template('index.html', title='Welcome', username="merger3")

@app.route('/data', methods = ['POST', 'GET'])
def load_response():
	if request.method == 'POST':
		game = loop.run_until_complete(createDescription(request.form['name'], request.form['platform']))
		return render_template('table.html', title='Welcome', records=game)
	return "error"


if __name__ == '__main__':
	loop.run_until_complete(initDB())
	print("initialized DB")
	app.run(host='0.0.0.0', port=5000)