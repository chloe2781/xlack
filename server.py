
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import time
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#added to use sessions
#app.secret_key = 'mysecretkey'


# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "cn2489"
DATABASE_PASSWRD = "6642"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"



# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI)


# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
with engine.connect() as conn:
	create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
	res = conn.execute(text(create_table_command))
	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)

	
	# example of a database query

	# select_query = "SELECT name from test"
	# cursor = g.conn.execute(text(select_query))
	# names = []
	# for result in cursor:
	# 	names.append(result[0])
	# cursor.close()



	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#
	# context = dict(data = emails)


	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/signup/<email>')
def signup(email):
	return render_template("signup.html", email=email)

@app.route('/workspace/<user_id>')
def workspace(user_id):
	# query to get all workspaces that the user is a part of
	select_query = text("""
		SELECT ws_id, name FROM \"workspace\" 
		WHERE ws_id IN (SELECT ws_id FROM \"join\" 
						WHERE user_id = :user_id)""")
	cursor = g.conn.execute(select_query, {"user_id": user_id})

	workspaces = []
	for result in cursor:
		workspaces.append(result)
	cursor.close()
	return render_template("workspace.html", data=workspaces, user_id=user_id)

@app.route('/channel/<user_id>/<ws_id>')
def channel(user_id, ws_id):
	# query to get all workspaces that the user is a part of
	select_query = text("""
		SELECT ws_id, name FROM \"workspace\" 
		WHERE ws_id IN (SELECT ws_id FROM \"join\" 
						WHERE user_id = :user_id)""")
	cursor = g.conn.execute(select_query, {"user_id": user_id})
	workspaces = []
	for result in cursor:
		workspaces.append(result)
	cursor.close()

	# query to get all channels in the workspace
	select_query = text("""
		SELECT channel_id, name FROM \"channel\" 
		WHERE ws_id = :ws_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id})
	channels = []
	for result in cursor:
		channels.append(result)
	cursor.close()

	# query to get all the direct messages in the workspace
	# only display dms that have messages sent --> no empty ones
	select_query = text("""
			SELECT dm_id, name FROM \"is_posted_in_dm\", \"user\"
			WHERE ws_id = :ws_id AND recipient_id = :user_id AND user_id = sender_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id, "user_id": user_id})
	dms = []
	for result in cursor:
		dms.append(result)
	cursor.close()

	#query to get workspace name
	select_query = text("""
			SELECT name FROM \"workspace\" 
			WHERE ws_id = :ws_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id})
	ws_name = cursor.fetchone()[0]
	cursor.close()

	return render_template("channel.html", workspaces=workspaces, channels=channels, user_id=user_id, ws_id=ws_id,
						   dms=dms, ws_name=ws_name)

@app.route('/chat/<user_id>/<ws_id>/<channel_id>')
def chat(user_id, ws_id, channel_id):
	# query to get all workspaces that the user is a part of
	select_query = text("""
		SELECT ws_id, name FROM \"workspace\" 
		WHERE ws_id IN (SELECT ws_id FROM \"join\" 
						WHERE user_id = :user_id)""")
	cursor = g.conn.execute(select_query, {"user_id": user_id})
	workspaces = []
	for result in cursor:
		workspaces.append(result)
	cursor.close()

	# query to get all channels in the workspace
	select_query = text("""
		SELECT channel_id, name FROM \"channel\" 
		WHERE ws_id = :ws_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id})
	channels = []
	for result in cursor:
		channels.append(result)
	cursor.close()

	# query to get all the direct messages in the workspace
	# only display dms that have messages sent --> no empty ones
	select_query = text("""
				SELECT dm_id, name FROM \"is_posted_in_dm\", \"user\"
				WHERE ws_id = :ws_id AND recipient_id = :user_id AND user_id = sender_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id, "user_id": user_id})
	dms = []
	for result in cursor:
		dms.append(result)
	cursor.close()

	# query to get all messages in the channel
	select_query = text("""
		SELECT M.mess_id, M.content, U.name
		FROM "user" U, message M, is_posted_in_channel P
		WHERE P.ws_id = :ws_id 
			AND P.channel_id = :channel_id 
			AND M.mess_id = P.mess_id 
			AND U.user_id = M.user_id;""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id, "channel_id": channel_id})
	messages = []
	for result in cursor:
		messages.append(result)
	cursor.close()

	# query to get channel name
	select_query = text("""
		SELECT name FROM \"channel\" 
		WHERE channel_id = :channel_id""")
	cursor = g.conn.execute(select_query, {"channel_id": channel_id})
	channel_name = cursor.fetchone()[0]
	cursor.close()

	# query to get workspace name
	select_query = text("""
				SELECT name FROM \"workspace\" 
				WHERE ws_id = :ws_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id})
	ws_name = cursor.fetchone()[0]
	cursor.close()

	time.sleep(0.5)

	return render_template("chat.html",workspaces=workspaces, channels=channels, dms=dms, user_id=user_id,
			ws_id=ws_id, channel_id=channel_id, messages=messages, channel_name=channel_name, ws_name=ws_name)


@app.route('/dm/<user_id>/<ws_id>/<dm_id>')
def dm(user_id, ws_id, dm_id):
	# query to get all workspaces that the user is a part of
	select_query = text("""
		SELECT ws_id, name FROM \"workspace\" 
		WHERE ws_id IN (SELECT ws_id FROM \"join\" 
						WHERE user_id = :user_id)""")
	cursor = g.conn.execute(select_query, {"user_id": user_id})
	workspaces = []
	for result in cursor:
		workspaces.append(result)
	cursor.close()

	# query to get all channels in the workspace
	select_query = text("""
			SELECT channel_id, name FROM \"channel\" 
			WHERE ws_id = :ws_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id})
	channels = []
	for result in cursor:
		channels.append(result)
	cursor.close()

	# query to get all the direct messages in the workspace
	# only display dms that have messages sent --> no empty ones
	select_query = text("""
				SELECT dm_id, name FROM \"is_posted_in_dm\", \"user\"
				WHERE ws_id = :ws_id AND recipient_id = :user_id AND user_id = sender_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id, "user_id": user_id})
	dms = []
	for result in cursor:
		dms.append(result)
	cursor.close()

	# query to get all messages in the dm
	select_query = text("""
		SELECT M.mess_id, M.content, U.name
		FROM "user" U, message M, is_posted_in_dm P
		WHERE P.ws_id = :ws_id 
			AND P.dm_id = :dm_id 
			AND M.mess_id = P.mess_id 
			AND U.user_id = M.user_id;""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id, "dm_id": dm_id})
	messages = []
	for result in cursor:
		messages.append(result)
	cursor.close()

	# query to get channel name
	#select_query = text("""
	#		SELECT name FROM \"channel\"
	#		WHERE channel_id = :channel_id""")
	#cursor = g.conn.execute(select_query, {"channel_id": channel_id})
	#channel_name = cursor.fetchone()[0]
	#cursor.close()

	# query to dm name (name of other person in dm)
	select_query = text("""
				SELECT name FROM \"is_posted_in_dm\", \"user\"  
				WHERE ws_id = :ws_id AND user_id = sender_id AND recipient_id = :user_id  AND dm_id = :dm_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id, "user_id": user_id, "dm_id": dm_id})
	dm_name = cursor.fetchone()[0]
	cursor.close()

	# query to get workspace name
	select_query = text("""
					SELECT name FROM \"workspace\" 
					WHERE ws_id = :ws_id""")
	cursor = g.conn.execute(select_query, {"ws_id": ws_id})
	ws_name = cursor.fetchone()[0]
	cursor.close()

	time.sleep(0.5)

	#removed channel_id=channel_id ???
	# and channel_name=channel_name,
	return render_template("dm_chat.html",workspaces=workspaces, channels=channels, dms=dms, user_id=user_id,
			ws_id=ws_id, dm_id=dm_id, messages=messages, ws_name=ws_name, dm_name=dm_name)


# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
# 	# accessing form inputs from user
# 	name = request.form['name']
	
# 	# passing params in for each variable into query
# 	params = {}
# 	params["new_name"] = name
# 	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
# 	g.conn.commit()
# 	return redirect('/')

@app.route('/next', methods=['POST'])
def next():
	# accessing form inputs from user
	curr_email = request.form['email']

	# checking if email already exists
	# select_query = "SELECT email from \"user\""
	# cursor = g.conn.execute(text(select_query))
	# emails = []
	# for result in cursor:
	# 	emails.append(result[0])
	# cursor.close()

	# # if email already exists, redirect to user's workspace
	# if email in emails:
	# 	select_query = """SELECT user_id from \"user\"
	# 					WHERE email = :email"""
	# 	cursor = g.conn.execute(select_query, email)
	# 	curr_user_id = [cursor.fetchone()[0]]
	# 	cursor.close()
	# 	return redirect(url_for('workspace', user_id = curr_user_id))
	
	# Query the database to find the user_id corresponding to the email
	select_query = text("""SELECT user_id FROM "user" WHERE email = :email""")
	result = g.conn.execute(select_query, {"email": curr_email}).fetchone()
    
	if result is None:
		return redirect(url_for('signup', email=curr_email))
    
	user_id = result[0]
	return redirect(url_for('workspace', user_id=user_id))

	# if email does not exist, redirect to signup page
	
	# params = {}
	# params["new_name"] = name
	# g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	# g.conn.commit()
	
@app.route('/submit', methods=['POST'])
def submit():
	# accessing form inputs from user
	email = request.form['user_email']
	name = request.form['user_name']
	dob_str = request.form['dob']
	dob = datetime.strptime(dob_str, '%Y-%m-%d')
	dob = str(dob.date())

	# Query the database to find the most recent user_id
	select_query = text("""SELECT MAX(CAST(user_id AS INTEGER)) FROM \"user\"""")
	result = g.conn.execute(select_query).fetchone()
	prev_user_id = result[0]

	# insert new user into database
	params = {}
	params["user_id"] = str(int(prev_user_id) + 1)
	params["email"] = email
	params["name"] = name
	params["dob"] = dob
	g.conn.execute(text('INSERT INTO "user"(user_id, email, name, dob) VALUES (:user_id, :email, :name, :dob)'), params)
	g.conn.commit()

	# Query the database to find the user_id corresponding to the email
	select_query = text("""SELECT user_id FROM "user" WHERE email = :email""")
	result = g.conn.execute(select_query, {"email": email}).fetchone()

	user_id = result[0]

	return redirect(url_for('workspace', user_id=user_id))


@app.route('/login')
def login():
	abort(401)
	this_is_never_executed()


@app.route('/chooseWS', methods=['POST'])
def chooseWS():
	ws_id = request.form['workspace_id']
	user_id = request.form['user_id']

	return redirect(url_for('channel',user_id=user_id, ws_id=ws_id))

@app.route('/chooseChannel', methods=['POST'])
def chooseChannel():
	channel_id = request.form['channel_id']
	user_id = request.form['user_id']
	ws_id = request.form['ws_id']

	return redirect(url_for('chat',user_id=user_id, ws_id=ws_id, channel_id=channel_id))

@app.route('/chooseDM', methods=['POST'])
def chooseDM():
	dm_id = request.form['dm_id']
	user_id = request.form['user_id']
	#recipient_id = request.form['recipient_id']
	ws_id = request.form['ws_id']

	return redirect(url_for('dm', user_id=user_id, ws_id=ws_id, dm_id=dm_id))

@app.route('/addWSButton', methods=['POST'])
def addWSButton():
	user_id = request.form['user_id']

	# 1 second delay to deal with concurrency issues
	time.sleep(1)

	return render_template("add_workspace.html", user_id=user_id)


@app.route('/addChannelButton', methods=['POST'])
def addChannelButton():
	ws_id = request.form['ws_id']
	user_id = request.form['user_id']

	# 1 second delay to deal with concurrency issues
	time.sleep(1)

	return render_template("add_channel.html", ws_id=ws_id, user_id=user_id)

@app.route('/addDMButton', methods=['POST'])
def addDMButton():
	ws_id = request.form['ws_id']
	user_id = request.form['user_id']

	#list through all people in the workspace

	# Query the database to find all users.
	# do NOT include current user bc we don't want them to do a DM with self


	#ALSOOOOOOOO fix so doesn't show users who already have a DM with

	select_query = text("""SELECT J.user_id, name FROM \"join\" J, \"user\" U
						WHERE ws_id = :ws_id AND J.user_id = U.user_id AND J.user_id != :user_id""")
	ws_users = g.conn.execute(select_query, {"ws_id": ws_id, "user_id": user_id}).fetchall()

	# 1 second delay to deal with concurrency issues
	time.sleep(1)

	return render_template("add_dm.html", ws_id=ws_id, user_id=user_id, ws_users=ws_users)


#assumes we handle GET and POST when we don't explicitly define methods
@app.route('/addWS', methods=['POST'])
def addWS():
	# accessing form inputs from user
	name = request.form['ws_name']
	user_id = request.form['user_id']

	# Query the database to find the most recent ws_id
	select_query = text("""SELECT ws_id FROM \"workspace\"""")
	id_list = g.conn.execute(select_query).fetchall()

	#strip ws_id because formated as "w#", where # is some number
	max_tail = 0
	max_head = ''
	for id in id_list:
		s = id[0]
		head = s.rstrip('0123456789')
		tail = int(s[len(head):])
		if tail > max_tail:
			max_tail = tail
			max_head = head

	# insert new workspace into database
	params = {}
	params["ws_id"] = max_head + str(int(max_tail) + 1)
	params["name"] = name
	params["user_id"] = user_id
	g.conn.execute(text('INSERT INTO "workspace"(ws_id, name, user_id) VALUES (:ws_id, :name, :user_id)'), params)
	g.conn.commit()
	#also need to have user join that workspace
	g.conn.execute(text('INSERT INTO "join"(user_id,ws_id) VALUES (:user_id,:ws_id)'), params)

	g.conn.commit()

	return redirect(url_for('workspace', user_id=user_id))

@app.route('/addChannel', methods=['POST'])
def addChannel():
	# accessing form inputs from user
	name = request.form['channel_name']
	ws_id = request.form['ws_id']
	user_id = request.form['user_id']

	# Query the database to find the most recent channel_id given a ws
	select_query = text("""SELECT channel_id FROM "channel" WHERE ws_id = :ws_id""")
	id_list = g.conn.execute(select_query, {"ws_id": ws_id}).fetchall()

	#strip ws_id because formated as "c$-#",
	# where $ is some number for ws-id, and # is some number for the channel id in that ws
	ws_head = ws_id.rstrip('0123456789')
	ws_id_num = ws_id[len(ws_head):]

	#if return none, create the first channel in that ws
	if len(id_list) == 0:
		result = "c" + ws_id_num + "-1"
	else:
		max_tail = 0
		max_head = ''
		for id in id_list:
			s = id[0]
			head, tail = s.split('-')
			if int(tail) > max_tail:
				max_tail = int(tail)
				max_head = head
		#max_head includes "w#" need to add "-"
		result = max_head + "-" + str(int(max_tail) + 1)

	# insert new channel into database
	params = {}
	params["ws_id"] = ws_id
	params["channel_id"] = result
	params["name"] = name
	params["user_id"] = user_id
	g.conn.execute(text('INSERT INTO "channel"(ws_id, channel_id, name, user_id) VALUES (:ws_id, :channel_id, :name, :user_id)'), params)

	g.conn.commit()

	#redirect to channel
	return redirect(url_for('channel', user_id=user_id, ws_id=ws_id))


@app.route('/addDM', methods=['POST'])
def addDM():
	# accessing form inputs from user
	ws_id = request.form['ws_id']
	user_id = request.form['user_id']
	#recipient_id = request.form['recipient_id']

	#return


@app.route('/sendMessage', methods=['POST'])
def sendMessage():
	# accessing form inputs from user
	message = request.form['message']
	user_id = request.form['user_id']
	ws_id = request.form['ws_id']
	channel_id = request.form['channel_id']

	# Query the database to find the most recent message_id
	select_query = text("""SELECT MAX(CAST(SUBSTRING(mess_id, 2) AS INTEGER)) FROM \"message\"""")
	result = g.conn.execute(select_query).fetchone()
	prev_message_id = result[0]

	# insert new message into database
	params = {}
	params["mess_id"] = "m" + str(int(prev_message_id) + 1)
	params["message"] = message
	params["user_id"] = user_id
	params["channel_id"] = channel_id
	params["ws_id"] = ws_id
	g.conn.execute(text('INSERT INTO "message"(mess_id, post_date, content, user_id) VALUES (:mess_id,CURRENT_TIMESTAMP, :message, :user_id)'), params)
	g.conn.execute(text('INSERT INTO "is_posted_in_channel"(mess_id, channel_id, ws_id, user_id) VALUES (:mess_id,:channel_id, :ws_id, :user_id)'), params)
	
	g.conn.commit()

	return redirect(url_for('chat', user_id=user_id, ws_id=ws_id, channel_id=channel_id))


@app.route('/sendDM', methods=['POST'])
def sendDM():
	#DOES NOT WORK YET
	# accessing form inputs from user
	message = request.form['message']
	sender_id = request.form['user_id']
	ws_id = request.form['ws_id']
	dm_id = request.form['dm_id']

	#query to find recipient-id
	select_query = text("""SELECT MAX(CAST(user_id AS INTEGER)) FROM \"user\"""")
	result = g.conn.execute(select_query).fetchone()
	prev_user_id = result[0]

	# Query the database to find the most recent message_id
	select_query = text("""SELECT MAX(CAST(SUBSTRING(mess_id, 2) AS INTEGER)) FROM \"message\"""")
	result = g.conn.execute(select_query).fetchone()
	prev_message_id = result[0]

	# insert new message into database
	params = {}
	params["mess_id"] = "m" + str(int(prev_message_id) + 1)
	params["message"] = message
	params["sender_id"] = sender_id
	#params["recipient_id"] = recipient_id
	params["dm_id"] = dm_id
	params["ws_id"] = ws_id
	g.conn.execute(text(
		'INSERT INTO "message"(mess_id, post_date, content, user_id) VALUES (:mess_id,CURRENT_TIMESTAMP, :message, :user_id)'),
				   params)
	g.conn.execute(text(
		'INSERT INTO "is_posted_in_dm"(mess_id, dm_id, ws_id, sender_id, recipient_id) VALUES (:mess_id,:dm_id, :ws_id, :sender_id, :recipient_id)'),
				   params)

	g.conn.commit()

	print("HEREE")

	return redirect(url_for('dm', user_id=sender_id, ws_id=ws_id, dm_id=dm_id))


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
