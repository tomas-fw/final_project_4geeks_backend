from flask import Flask, render_template, jsonify, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db
from flask_jwt_extended import(
    JWTManager, get_jwt_identity, create_access_token,
    jwt_required
)


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config[''] = ''

jwt = JWTManager(app)

db.init_app(app)
Migrate(app,db)
CORS(app)
bcrypt = Bcrypt(app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@app.route('/')
def index():
    return render_template('index.html')


if __name__=='__main__':
    manager.run()