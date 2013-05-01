import sqlite3, json, os
from flask import Flask,request
app = Flask(__name__)
import logging, sys
logging.basicConfig(stream=sys.stderr)

DATABASE = 'data.db'

#prints logs to the console


def db_init():
    connection = sqlite3.connect(DATABASE)
    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (name TEXT, facebook_id INTEGER)')
    cur.execute('CREATE TABLE IF NOT EXISTS segments (user_id INTEGER, distance REAL, interval REAL, mode TEXT, time TEXT)')
    connection.commit()
    connection.close()

#routes -------------------------------------------------------------------

@app.route('/')
def index():
    return json.dumps({'message': 'hello world'})

@app.route('/users/<id>', methods=['GET'])
def get_user(id):
    #get the user with the id <id> from the database
    single_resource = query_db('SELECT * FROM users WHERE rowid = ?', [id], True)
    return json.dumps(single_resource)

@app.route('/segments', methods=['GET'])
def get_segments():
    #return all segments
    resources = query_db('SELECT * FROM segments', [], False)
    return json.dumps(resources)

@app.route('/users/<id>/track', methods=['GET'])
def get_stats_for_user(id):
    params = request.args
    results = dict()

    #for each mode of transportation
    #get the sum of the time and distance for the user with the user_id <id> from the database
    for mode in ['bike','car','walk']:
        day = query_db('SELECT sum(distance), sum(interval) FROM segments WHERE user_id = ? AND mode = ? AND DATE(time) BETWEEN date("now","-1 day") AND date("now")', [id, mode], False)
        week = query_db('SELECT sum(distance), sum(interval) FROM segments WHERE user_id = ? AND mode = ? AND DATE(time) BETWEEN date("now","-7 day") AND date("now")', [id, mode], False)
        month = query_db('SELECT sum(distance), sum(interval) FROM segments WHERE user_id = ? AND mode = ? AND DATE(time) BETWEEN date("now","-30 day") AND date("now")', [id, mode], False)
        year = query_db('SELECT sum(distance), sum(interval) FROM segments WHERE user_id = ? AND mode = ? AND DATE(time) BETWEEN date("now","-365 day") AND date("now")', [id, mode], False)
        results[mode] = { "day" : day[0], "week" : week[0], "month" : month[0], "year" : year[0] }
    return json.dumps(results)

@app.route('/users', methods=['POST'])
def add_user():
    #access message of the POST with request.form
    #then add a new user to the database
    #return the id of the new user
    params = request.form
    new_user_id = add_to_db('INSERT INTO users values(?,?)', [params.get('name'), params.get('facebook_id')])
    return json.dumps({'id' : new_user_id})

@app.route('/segments', methods=['POST'])
def add_segment():
    #access message of the POST with request.form
    #then add a new item to the database
    #return the id of the new item
    params = request.form
    new_leg_id = add_to_db('INSERT INTO segments values(?,?,?,?,?)', [params.get('user_id'), params.get('distance'), params.get('interval'), params.get('mode'),  params.get('time')])
    return json.dumps({'id' : new_leg_id})


def connect_db():
    db_init()
    return sqlite3.connect(DATABASE)

def query_db(query, args=(), one=False):
    connection = connect_db()
    cur = connection.cursor().execute(query,args)
    if one:
        rows = cur.fetchone()
    else:
        rows = cur.fetchall()
    connection.close()
    return rows

def add_to_db(query, args=()):
    connection = connect_db()
    cur = connection.cursor().execute(query,args)
    connection.commit()
    id = cur.lastrowid
    connection.close()
    return id

if __name__ == '__main__':
    debug=True
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



