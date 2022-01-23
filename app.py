from flask import Flask, request, render_template, redirect, jsonify, send_from_directory
from flask import make_response
from flask_mysqldb import MySQL
import os
import yaml
from apispec import APISpec
from apispec_webframeworks.flask import FlaskPlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

conf = yaml.safe_load(open("db.yaml"))
app.config['MYSQL_HOST'] = conf['mysql_host']
app.config['MYSQL_USER'] = conf['mysql_user']
app.config['MYSQL_PASSWORD'] = conf['mysql_password']
app.config['MYSQL_DB'] = conf['mysql_db']
app.config['SECRET_KEY'] = conf['secret_key']


mysql = MySQL(app)

@app.route('/')
def homepage():  # put application's code here
    return render_template("homepage.html")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')   # http://localhost:4444/route?token/a34achahdv3
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except PermissionError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    return decorated


@app.route('/login')
def api_login():
    auth = request.authorization
    if auth:
        un = auth.username
        psw = auth.password
        cursor = mysql.connection.cursor()
        query1 = f"select name, password from users where name = '{un}' and " \
                 f"password = '{psw}'"

        rows = cursor.execute(query1)
        if rows == 1:
            token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() +
                                datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
            return jsonify({'token': token.decode('UTF-8')})
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/', methods=['POST'])
def checklogin():
    un = request.form['uname']
    psw = request.form['psw']

    cursor = mysql.connection.cursor()
    query1 = f"select name, password from users where name = '{un}' and " \
             f"password = '{psw}'"

    rows = cursor.execute(query1)
    data = cursor.fetchall()
    cursor.close()
    if len(rows) == 1:
        return render_template("loggedin.html")
    else:
        return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        dUN = request.form["uname"]
        dPW = request.form["psw"]
        uemail = request.form["email"]
        cursor = mysql.connection.cursor()
        query1 = f"insert into users (name, password, email) values ('{dUN}', '{dPW}', '{uemail}')"

        try:
            cursor.execute(query1)
        except:
            return jsonify({'message': f'{dUN} already exists. Try another username'}), 403
        mysql.connection.commit()
        cursor.close()
        return redirect("/")
    return render_template("register.html")

spec = APISpec(
    title="flask-api-swagger-doc",
    version='1.0.0',
    openapi_version='3.0.2',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)

@app.route("/api/swagger.json")
def create_swagger_spec():
    return jsonify(spec.to_dict())


class TodoResponseSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    status = fields.Boolean()


class TodoListResponseSchema(Schema):
    todo_list = fields.List(fields.Nested(TodoResponseSchema))


@app.route("/todo")
@token_required
def todo():
    """Get List of Todo
    ---
    get:
        description: Get List of Todos
        responses:
            200:
                description: Return a todo list
                content:
                    application/json:
                        schema: TodoListResponseSchema
    """
    dummy_data = [{'id':1,
                  'title':'Finish this task',
                  'status':False},
                  {
                      'id':2,
                      'title':'Finish the task',
                      'status':True
                  }]

    return TodoListResponseSchema().dump({'todo_list': dummy_data})


with app.test_request_context():
    spec.path(view=todo)


@app.route("/docs")
@app.route("/docs/<path:path>")
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs')
    else:
        return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),
            port=int(os.getenv('PORT', 4444)))
