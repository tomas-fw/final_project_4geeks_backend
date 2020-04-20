import os,getpass
from flask import Flask, render_template, jsonify, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from models import db, Role, Admin, Nutritionist, Trainer, Client, Planes
from flask_jwt_extended import(
    JWTManager, get_jwt_identity, create_access_token,
    jwt_required
)
from functions import allowed_files
from werkzeug.utils import secure_filename


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS_IMAGES = {'png','jpg','jpeg', 'gif', 'svg'}

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static')

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

### BEFORE CREATING ADMIN, BE SURE TO HAVE THE ROLES CREATED, IF NOT, USE COMMAND python app.py loadroles
### ADMIN ROUTES ### --- TO REGISTER NEW ADMIN, CAN USE COMMAND python app.py createadmin

###    ADMIN ROUTES  ### -- LOGIN
@app.route('/admin/login', methods=['POST']) ## ADMIN LOGIN
def login_admin():
    if not request.is_json:
        return jsonify({"msg":"Missing JSON request"})
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or username == '':
        return jsonify({"msg": "Username Incorrect"}), 400
    if not password or password == '':
        return jsonify({"msg": "Username Incorrect"}), 400

    admin = Admin.query.filter_by(username = username).first()    
    if not admin:
        return jsonify({'msg':'Username Incorrect'})
    if not bcrypt.check_password_hash(admin.password, password):
        return jsonify({"msg":"Password Incorrect"}), 400
    else:
        access_token = create_access_token(identity = admin.username)
        data = {
            'access_token': access_token,
            'admin': admin.serialize()
        }

        return jsonify(data), 200

###    ADMIN ROUTES  ### -- REGISTER NEW ADMIN
@app.route('/admin/register-admin', methods=['POST']) ## ADMIN CREATE OTHER ADMINS
@jwt_required
def admin_register():
    currentAdmin = get_jwt_identity()
    admin = Admin.query.filter_by(username = currentAdmin).first()

    if not admin.role_id==1:
        return jsonify({"msg":"Only admin can access here"}), 401

    if not request.is_json:
        return jsonify({"msg":"Missing JSON request"}), 404
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    name = request.json.get('name', None)
    lastname = request.json.get('lastname', None)

    if not username or username == '':
        return jsonify({"msg":"A username is required"}), 400
    if not password or password == '':
        return jsonify({"msg":"A password is required"}), 400

    admin = Admin.query.filter_by( username = username). first()
    if admin:
        return jsonify({"msg":"Username already exists"})
    
    admin = Admin()
    admin.username = username
    admin.password = bcrypt.generate_password_hash(password)
    admin.name = name
    admin.lastname = lastname
    admin.role_id = 1

    db.session.add(admin)
    db.session.commit()

    access_token = create_access_token(identity=admin.username)
    data = {
        'access_token': access_token,
        'admin':admin.serialize()
    }
    return jsonify(data), 200


### ADMIN ROUTES ##### GET ALL PROFESIONALS OR SPECIFIC PROFESIONAL BY ID
@app.route('/admin/profesional', methods=['GET'])
@app.route('/admin/profesional/<int:role_id>', methods=['GET'])
@app.route('/admin/profesional/<int:role_id>/<int:id>', methods=['GET'])
def admin_profesionals(role_id=None, id = None):
    if role_id != None and role_id != 2 and role_id != 3:       ### THIS VERIFIES THAT THE ROLE EXISTS WITHIN PROFESIONALS
        return jsonify({"msg":"role input not valid"}), 404
    if role_id is None:                                         ###     THIS BIRNGS UP EVERY PROFESIONAL
        trainers = Trainer.query.all()
        nutritionists = Nutritionist.query.all()
        profesionals ={
            "trainer":[],
            "nutritionist":[]
        }
        for trainer in trainers:
            obj={
                "id":trainer.id,
                "email":trainer.email,
                "name":trainer.name,
                "lastname": trainer.lastname,
                "register_date":trainer.date_created,
                "specialties": trainer.specialties,
                'is_active':trainer.active,
                "all_plans":[]
            }
            for plans in trainer.planes_id:
                planes ={
                    "plan_detailed":plans.serialize()
                }
                obj["all_plans"].append(planes)
            profesionals['trainer'].append(obj)

        for nutri in nutritionists:
            obj={
                "id":nutri.id,
                "email":nutri.email,
                "name":nutri.name,
                "lastname": nutri.lastname,
                "register_date":nutri.date_created,
                "specialties": nutri.specialties,
                'is_active': nutri.active,
                "all_plans":[]
            }
            for plan in nutri.planes_id:
                planes ={
                    "plan_detailed":plan.serialize()
                }
                obj['all_plans'].append(planes)
            profesionals['nutritionist'].append(obj)
        
        return jsonify(profesionals), 200
    
    if role_id == 2 and id == None:                 #### THIS BRINGS UP EVERY NUTRITIONIST
        all_nutritionist = Nutritionist.query.all()
        nutritionists = []
        for nutri in all_nutritionist:
            obj={
                'id':nutri.id,
                'email':nutri.email,
                'name':nutri.name,
                'lastname':nutri.lastname,
                'specialties':nutri.specialties,
                'is_active': nutri.active,
                'all_plans':[]
            }          
            for plan in nutri.planes_id:
                plans={
                    'plans_detail':plan.serialize()
                }
                obj['all_plans'].append(plans)
            nutritionists.append(obj)
        return jsonify(nutritionists)  

    if role_id == 3 and id == None:             ####  THIS BRINGS UP EVERY TRAINER
        all_trainers = Trainer.query.all()    
        trainers = []
        for trainer in all_trainers:
            obj={
                'id':trainer.id,
                'email':trainer.email,
                'name':trainer.name,
                'lastname':trainer.lastname,
                'specialties':trainer.specialties,
                'is_active': trainer.active,
                'all_plans':[]
            }
            for plan in trainer.planes_id:
                plans={
                    'plans_detail':plan.serialize()
                }
                obj['all_plans'].append(plans)
            trainers.append(obj)
        return jsonify(trainers)

    if role_id == 2 and id:             ####   THIS BIRNGS UP A SPECIFIC NUTRITIONIST
        single_nutritionist = Nutritionist.query.get(id)
        nutritionists = Nutritionist.query.all()
        nutri =[]
        if not single_nutritionist:
            return jsonify({'msg':'Nutritionist does not exist in database'})
        else:
            for nutritionist in nutritionists:
                if nutritionist.id == id:
                    obj ={
                        'id':nutritionist.id,
                        'email':nutritionist.email,
                        'name':nutritionist.name,
                        'lastname': nutritionist.lastname,
                        'specialties': nutritionist.specialties,
                        'is_active': nutritionist.active,
                        'all_plans':[]
                    }
                    for plan in nutritionist.planes_id:
                        all_plans={
                            'plans_detail':plan.serialize()
                        }
                        obj['all_plans'].append(all_plans)
                    nutri.append(obj)
            return jsonify(nutri)
    
    if role_id == 3 and id:                 #####           THIS BRINGS UP A SPECIFIC TRAINER
        single_trainer = Trainer.query.get(id)
        all_trainers = Trainer.query.all()
        personal_trainer = []
        if not single_trainer:
            return jsonify({"msg":"Trainer not found in database"}), 400
        else:
            for trainer in all_trainers:
                if trainer.id == id:
                    obj ={
                        'id':trainer.id,
                        'email':trainer.email,
                        'name':trainer.name,
                        'lastname': trainer.lastname,
                        'specialties': trainer.specialties,
                        'is_active': trainer.active,
                        'all_plans':[]
                    }
                    for plan in trainer.planes_id:
                        all_plans={
                            'plans_detail':plan.serialize()
                        }
                        obj['all_plans'].append(all_plans)
                    personal_trainer.append(obj)          
            return jsonify(personal_trainer)

        
### ADMIN ROUTES   #####   GET ALL CLIENTS IN DATABASE OR SPECIFIC CLIENT BY ID

@app.route('/admin/client', methods=['GET'])
@app.route('/admin/client/<int:client_id>', methods=['GET','PUT','DELETE'])
def admin_clients(client_id = None):
    if request.method == 'GET':
        if client_id is None:       ####    THIS ONE SHOWS EVERY CLIENT
            clients = Client.query.all()            
            planes = [] 
            for client in clients:
                obj ={
                    "id": client.id,
                    "email": client.email,
                    "name":client.name,
                    "last_name": client.lastname,
                    "date_created": client.date_created,
                    "is_active":client.active,
                    "all_plans":[]
                }
                for plan in client.planes_id:
                    plan_detail ={
                            
                        "detail": plan.serialize()
                    }
                    obj['all_plans'].append(plan_detail)
                planes.append(obj)            
            
            return jsonify(planes),200
        else:                           ##### THIS ONE SHOWS A SPECIFIC CLIENT
            single_client= Client.query.get(client_id)
            all_clients = Client.query.all()
            specific_client=[]
            if not single_client:
                return jsonify({'msg':'client does not exist in database'}), 404
            else:
                for client in all_clients:
                    if client.id == client_id:
                        obj ={
                            "id": client.id,
                            "email": client.email,
                            "name":client.name,
                            "last_name": client.lastname,
                            "date_created": client.date_created,
                            "is_active":client.active,
                            "all_plans":[]
                            }
                        for plan in client.planes_id:
                            all_plans={
                                "detail": plan.serialize()
                            }
                            obj['all_plans'].append(all_plans)
                            
                        specific_client.append(obj)
                return jsonify(specific_client), 200
              
    if request.method == 'PUT':             #### THIS ONE DOESN'T WORK BECAUSE CANNOT DELETE FOREIGNKEY CONSTRAIN NULL,(DEPENDENCIES FROM OTHER TABLES)

        email = request.form.get('email')
        # password = request.form.get('password')
        name = request.form.get("name")
        lastname=request.form.get("lastname")
        # active = request.form.get('active')

        if not email or email == '':
            return jsonify({"msg":"Missing email field"}),404
        # if not password or password == '':
        #     return jsonify({"msg":"Missing password field"}),404
        if not name or name == '':
            return jsonify({"msg":"Missing name field"}),404
        if not lastname or lastname == '':
            return jsonify({"msg":"Missing last name field"}),404

        client = Client.query.get(client_id)
        client.email = email
        # client.password = bcrypt.generate_password_hash(password)
        client.name = name
        client.lastname = lastname
        # client.active = active

        db.session.commit()
        # access_token = create_access_token(identity = client.email)
        # data={
        #     'access_token': access_token,
        #     'profesional': nutri.serialize()
        # }

        return jsonify(client.serialize()), 200

    if request.method == 'DELETE':          #### THIS ONE DOESN'T WORK BECAUSE CANNOT DELETE FOREIGNKEY CONSTRAIN NULL,(DEPENDENCIES FROM OTHER TABLES)
        client = Client.query.get(client_id)
        if not client:
            return jsonify({"msg":"Client not found"})
        
        db.session.delete(client)
        db.session.commit()

        return jsonify({"msg":"client deleted from database"})


###LOGIN ROUTES FOR PROFESIONALS AND CLIENTS

@app.route('/login/<int:role_id>', methods=['POST'])
def login(role_id):
    if role_id != 2 and role_id != 3  and role_id != 4:
        return jsonify({"msg":'Role not found'})
    if role_id == 2:
        if not request.is_json:
            return jsonify({'msg':'Missing JSON request'})
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        if not email or email == '':
            return jsonify({'msg':'Missing email field'})
        if not password or password == '':
            return jsonify({'msg':'Missing password field'})
        
        nutritionist = Nutritionist.query.filter_by(email = email).first()
        if not nutritionist:
            return jsonify({'msg':'Email incorrect'})
        
        if not bcrypt.check_password_hash(nutritionist.password,password):
            return jsonify({'msg':'Password incorrect'})
        else:
            access_token = create_access_token(identity = nutritionist.email)
            data={
                'access_token': access_token,
                'nutritionist':{
                    'nutritionist_id': nutritionist.id,
                    'email': nutritionist.email,
                    'name': nutritionist.name,
                    'lastname': nutritionist.lastname,
                    'age':nutritionist.age,
                    'photo':nutritionist.photo,
                    'lasWork': nutritionist.lastWork,
                    'lastWorkedyears':nutritionist.lastWorkyears,
                    'active': nutritionist.active,
                    'created': nutritionist.date_created,
                    'educaction': nutritionist.education,
                    'description': nutritionist.description,
                    'specialties':nutritionist.specialties,
                    'role':nutritionist.role.serialize(),
                    'planes_id':[]
                }
            }
            for plans in nutritionist.planes_id:
                planes={
                    'all_plans':plans.serialize()
                }
                data['nutritionist']['planes_id'].append(planes)
            return jsonify(data), 200
        
        
    if role_id == 3:
        if not request.is_json:
            return jsonify({'msg':'Missing JSON request'})
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        if not email or email == '':
            return jsonify({'msg':'Missing email field'})
        if not password or password == '':
            return jsonify({'msg':'Missing password field'})
        
        trainer = Trainer.query.filter_by(email = email).first()
        if not trainer:
            return jsonify({'msg':'Email incorrect'})
        
        if not bcrypt.check_password_hash(trainer.password,password):
            return jsonify({'msg':'Password incorrect'})
        else:
            access_token = create_access_token(identity = trainer.email)
            data={
                'access_token': access_token,
                'trainer':{
                    'nutritionist_id': trainer.id,
                    'email': trainer.email,
                    'name': trainer.name,
                    'lastname': trainer.lastname,
                    'age':trainer.age,
                    'photo':trainer.photo,
                    'lasWork': trainer.lastWork,
                    'lastWorkedyears':trainer.lastWorkyears,
                    'active': trainer.active,
                    'created': trainer.date_created,
                    'educaction': trainer.education,
                    'description': trainer.description,
                    'specialties':trainer.specialties,
                    'role':trainer.role.serialize(),
                    'planes_id':[]
                }
            }
            for plans in trainer.planes_id:
                planes={
                    'all_plans':plans.serialize(),                    
                }
               
                data['trainer']['planes_id'].append(planes)
            return jsonify(data), 200
    if role_id == 4:
        if not request.is_json:
            return jsonify({'msg':'Missing JSON request'})
        email = request.json.get('email', None)
        password = request.json.get('password', None)

        if not email or email == '':
            return jsonify({'msg':'Missing email field'})
        if not password or password == '':
            return jsonify({'msg':'Missing password field'})
        
        client = Client.query.filter_by(email = email).first()
        if not client:
            return jsonify({'msg':'Email incorrect'})
        
        if not bcrypt.check_password_hash(client.password,password):
            return jsonify({'msg':'Password incorrect'})
        else:
            access_token = create_access_token(identity = client.email)
            data={
                'access_token': access_token,
                'client':{
                    'client_id': client.id,
                    'email': client.email,
                    'name': client.name,
                    'lastname': client.lastname,
                    'photo':client.photo,
                    'active': client.active,
                    'created': client.date_created,
                    'role':client.role.serialize(),
                    'planes_id':[]
                }
            }
            for plans in client.planes_id:
                planes={
                    'all_plans':plans.serialize()
                }
                data['client']['planes_id'].append(planes)
            return jsonify(data), 200

###    PROFESIONAL ROUTES #### --REGISTER
@app.route('/register/profesional/<int:role>', methods=['POST']) ##REGISTER PROFESIONAL
def profesional_register(role):
        
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')   
    
    if not email or email == '':
        return jsonify({"msg":"Missing email field"}),404
    if not password or password == '':
        return jsonify({"msg":"Missing password field"}),404
    if not name or name == '':
        return jsonify({"msg":"Missing name field"}),404
    if not lastname or lastname == '':
        return jsonify({"msg":"Missing last name field"}),404  

    if role == 2:
        nutri = Nutritionist.query.filter_by(email =email).first()
        if nutri:
            return jsonify({"msg":'email already register'}),400
        
        file = request.files['photo']
        if file and file.filename!= '' and allowed_files(file.filename, ALLOWED_EXTENSIONS_IMAGES):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar'), filename))
        else:
            return jsonify({"msg":"file is not allowed"}), 400
        nutri = Nutritionist()
        nutri.email = email
        nutri.password = bcrypt.generate_password_hash(password)
        nutri.name = name
        nutri.lastname = lastname
        nutri.role_id = role

        if file:
            nutri.photo = filename
        

        db.session.add(nutri)
        db.session.commit()

        access_token = create_access_token(identity = nutri.email)
        data={
            'access_token': access_token,
            'profesional': nutri.serialize()
        }
        return jsonify(data), 200
    
    if role == 3:
        trainer = Trainer.query.filter_by(email = email).first()
        if trainer:
            return jsonify({"msg":'email already register'}),400
        
        file = request.files['photo']
        if file and file.filename!= '' and allowed_files(file.filename, ALLOWED_EXTENSIONS_IMAGES):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar'), filename))
        else:
            return jsonify({"msg":"file is not allowed"}), 400
        trainer = Trainer()
        trainer.email = email
        trainer.password = bcrypt.generate_password_hash(password)
        trainer.name = name
        trainer.lastname = lastname
        trainer.role_id = role

        if file:
            trainer.photo = filename
    

        db.session.add(trainer)
        db.session.commit()

        access_token = create_access_token(identity = trainer.email)
        data={
            'access_token': access_token,
            'profesional': trainer.serialize()
        }
        return jsonify(data), 200


###    CLIENT ROUTES   #### -- REGISTER
@app.route('/register/client', methods=['POST'])        ### REGISTER CLIENT
def client_register():

    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')

    if not email or email == '':
        return jsonify({"msg":"Missing email field"}), 404
    if not password or password == '':
        return jsonify({"msg":"Missing password field"}), 404
    if not name or name == '':
        return jsonify({"msg":"Missing name field"}), 404
    if not lastname or lastname == '':
        return jsonify({"msg":"Missing lastname field"}), 404
    
    client = Client.query.filter_by(email = email).first()
    if client:
        return jsonify({"msg":"Email already register"}), 400
    
    file = request.files['photo']
    if file and file.filename != '' and allowed_files(file.filename, ALLOWED_EXTENSIONS_IMAGES):
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar'), filename))
    
    client = Client()
    
    client.email = email
    client.password = bcrypt.generate_password_hash(password)
    client.name = name
    client.lastname = lastname
    client.role_id = 4

    if file:
        client.photo = filename

    db.session.add(client)
    db.session.commit()

    access_token = create_access_token(identity=client.email)
    data = {
        'access_token': access_token,
        'client': client.serialize()
    }

    return jsonify(data), 200
    

###    CLIENT ROUTES   #### -- CLIENT CREATE PLAN AND CHECK HIS PLANNES OR SPECIFIC PLAN PER CLIENT
@app.route('/client/plan/<int:id_client>', methods=['GET','POST'])
@app.route('/client/plan/<int:id_client>/<int:plan_id>', methods=['GET'])
def client_plan(id_client = None, plan_id= None):   
    if request.method == 'GET':
        client = Client.query.get(client_id)
        plan = Planes.query.filter_by(id=plan_id).first()
        if not client:
            return jsonify({"msg":"client not found"}), 400
        else:
            if not plan_id:     ### THIS BRINGS EVERY PLAN A CLIENT HAS
                _client = Planes.query.filter_by(client_id=client_id).all()
                client_plans= list(map(lambda plan: plan.serialize(), _client))
                key = client_plans
                return jsonify (key), 200
            else:               #### THIS BRINGS A SPECIFIC PLAN A CLIENT HAS
                _client = Planes.query.filter_by(client_id=client_id).all()
                client_plans= list(map(lambda plan: plan.serialize(), _client))
                key = client_plans
                another_key = list(filter(lambda plan: plan if plan['id'] == plan_id else None, key ))
                if not another_key:
                    return jsonify({"msg":"plan does not exist"})                
                return jsonify(another_key), 200

    if request.method == 'POST':        #### THIS ALLOWS CLIENT TO CREATE PLAN
        if not request.is_json:
            return jsonify({'msg':'Missing JSON request'}), 400

        objective = request.json.get('objective')
        client_id = request.json.get('client_id')
        nutritionist_id = request.json.get('nutritionist_id')
        trainer_id = request.json.get('trainer_id')

        if not objective or objective == '':
            return jsonify({'msg':'Missing objective'}), 400
        if not client_id or client_id == '':
            return jsonify({'msg':'Your ID is missing '}), 400
        if not Client.query.filter_by(id=client_id).all():
            return jsonify({'msg':'Client does not exists in database'})
        if not  client_id == id_client:
            return jsonify({'msg':'Client id must match client id in url'})
        if not nutritionist_id or nutritionist_id == '':
            return jsonify({'msg':'Missing nutritionist'}), 400
        if not Nutritionist.query.filter_by(id =nutritionist_id).all():
            return jsonify({"msg":"Nutritionist does not exist in database"})
        if not trainer_id or trainer_id == '':
            return jsonify({'msg':'Missing trainer'}), 400
        if not Trainer.query.filter_by(id=trainer_id).all():
            return jsonify({'msg':"Trainer does not exist in database"})
        
                    
        
        plan = Planes()
        plan.objective = objective
        plan.client_id = client_id
        plan.nutritionist_id = nutritionist_id
        plan.trainer_id = trainer_id

        db.session.add(plan)
        db.session.commit()

        return jsonify(plan.serialize()),200


        

@manager.command
def loadroles():
    role = Role()
    role.name = 'admin'

    db.session.add(role)
    db.session.commit()

    role = Role()
    role.name = 'nutri'

    db.session.add(role)
    db.session.commit()

    role = Role()
    role.name = 'trainer'

    db.session.add(role)
    db.session.commit()

    role = Role()
    role.name = 'client'

    db.session.add(role)
    db.session.commit()

    print('role created')

@manager.command
def createadmin():
    username = input('Insert Admin UserName: ')
    password = getpass.getpass('Insert Admin Password: ')
    name = input('Insert Admin Name: ')
    lastname = input('Insert Admin Last Name: ')


    admin = Admin()
    admin.username = username
    admin.password = bcrypt.generate_password_hash(password)
    admin.role_id = 1
    admin.name = name
    admin.lastname = lastname

    db.session.add(admin)
    db.session.commit()

    print('admin created')

if __name__=='__main__':
    manager.run()