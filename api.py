import flask
from flask import request, jsonify
import pyodbc
from dotenv import load_dotenv
import os
from flask_cors import CORS, cross_origin

load_dotenv()

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
@cross_origin()
def home():
    return '''<h1>To-Do App API</h1>
<p>A prototype API for a To-Do app.</p>'''


@app.route('/api/v1/resources/todos/all', methods=['GET'])
def api_all():
    server = '127.0.0.1'
    database = 'toDoApi'
    username = 'sa'
    password = os.environ.get('SQLPASS')
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()

    cursor.execute('SELECT * FROM todos;')

    to_dos = {}
    all_to_dos = []

    for row in cursor.fetchall():
        to_do = {'id': str(row[0]), 'description': row[1], 'completed': row[2]}
        all_to_dos.append(to_do)

    return jsonify(all_to_dos)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/v1/resources/todos', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    descript = query_parameters.get('description')
    completed = query_parameters.get('completed')

    query = "SELECT * FROM todos WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if descript:
        query += ' description=? AND'
        to_filter.append(descript)
    if completed:
        query += ' completed=? AND'
        to_filter.append(completed)
    if not (id or descript or completed):
        return page_not_found(404)

    query = query[:-4] + ';'

    server = '127.0.0.1'
    database = 'toDoApi'
    username = 'sa'
    password = os.environ.get('SQLPASS')
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()

    cursor.execute(query, to_filter)
    results = ''
    to_dos = {}
    for row in cursor.fetchall():
        to_dos.update({'id: ' + str(row[0]): {'description ': row[1], 'completed: ': row[2]}})
    return jsonify(to_dos)


@app.route('/api/v1/resources/todos', methods=['POST'])
def create_todo():
    query_parameters = request.args
    descript = query_parameters.get('description')
    completed = query_parameters.get('completed')

    query = '''INSERT INTO [toDoApi].[dbo].[todos] ([descript], [completed]) VALUES (?, ?);'''

    server = '127.0.0.1'
    database = 'toDoApi'
    username = 'sa'
    password = os.environ.get('SQLPASS')
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    cursor.execute(query, descript, completed)
    cnxn.commit()

    query = '''SELECT TOP 1 [id] FROM [toDoApi].[dbo].[todos] ORDER BY [id] DESC;'''
    cursor.execute(query)
    id = cursor.fetchall()
    return str(id[0][0])


@app.route('/api/v1/resources/todos', methods=['DELETE'])
def delete_todo():
    query_parameters = request.args
    id = query_parameters.get('id')

    query = '''DELETE FROM [toDoApi].[dbo].[todos] WHERE [id] = ?'''

    server = '127.0.0.1'
    database = 'toDoApi'
    username = 'sa'
    password = os.environ.get('SQLPASS')
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    cursor.execute(query, id)
    cnxn.commit()

    return "Deleted!"

app.run()