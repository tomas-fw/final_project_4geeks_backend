import os,getpass
from flask import Flask, render_template, jsonify, request, send_from_directory, abort, url_for
from models import db, Role, Admin, Nutritionist, Trainer, Client, Planes, ClientTrainer, ClientNutritionist
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_jwt_extended import(
    JWTManager, get_jwt_identity, create_access_token,
    jwt_required
)
from functions import allowed_files
from werkzeug.utils import secure_filename



BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS_IMAGES = {'png','jpg','jpeg', 'gif', 'svg'}
ALLOWED_EXTENSIONS_FILES = {'pdf'}

app = Flask(__name__)

app.url_map.strict_slashes = False
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['SECRET_KEY'] = '/xc3/x1a/x1a/x7fO//+b/xa2H/xd8</x0e&/xfb/xc5/x19/xfa [/xca/xdc/x8b/xa7'
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True
app.config['MAIL_USERNAME'] = 'fit.good.app@gmail.com'
app.config['MAIL_PASSWORD'] = 'dajato2020'
app.config['MAIL_DEFAULT_SENDER'] = ('Javiera de Fit Good App','fit.good.app@gmail.com')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAI_ASCII_ATTACHMENTS'] = False



jwt = JWTManager(app)

db.init_app(app)
Migrate(app,db)
CORS(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


####        DOWNLOAD DOCUMENT      ######

@app.route('/download/<document>')
def download_document(document):

    
    # return render_template('index.html')
    try:
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'download'), filename= document, as_attachment=True)

    except FileNotFoundError:
        abort(404)




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
            'user': admin.serialize()
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


### ADMIN ROUTES ##### GET ALL PROFESIONALS OR SPECIFIC PROFESIONAL BY ID, AND ALSO THE FILES THEY UPLOAD
@app.route('/admin/profesional', methods=['GET'])
@app.route('/admin/profesional/<int:role_id>', methods=['GET'])
@app.route('/admin/profesional/<int:role_id>/<int:id>/', methods=['GET','PUT'])
@app.route('/admin/profesional/<int:role_id>/<int:id>/<document>/<filename>', methods=['GET'])
def admin_profesionals(role_id=None, id = None, document = None, filename= None):
    if request.method == 'GET':
        if role_id != None and role_id != 2 and role_id != 3:       ### THIS VERIFIES THAT THE ROLE EXISTS WITHIN PROFESIONALS
            return jsonify({"msg":"role input not valid"}), 404
        if role_id is None:                                         ###     THIS BIRNGS UP EVERY PROFESIONAL
            trainers = Trainer.query.all()
            nutritionists = Nutritionist.query.all()
            profesionals ={
                "trainers":[],
                "nutritionists":[]
            }
            for trainer in trainers:
                obj={
                    "id":trainer.id,
                    'role_id':trainer.role_id,
                    "email":trainer.email,
                    "name":trainer.name,
                    "lastname": trainer.lastname,
                    'avatar':trainer.avatar,
                    "register_date":trainer.date_created,
                    "specialties": trainer.specialties,
                    'is_active':trainer.active,
                    "background": trainer.background,
                    "profesional_title": trainer.profesional_title,
                    "specialties": trainer.specialties,
                    "age": trainer.age,
                    "lastWork": trainer.lastWork,
                    "lastWorkyears": trainer.lastWorkyears,
                    "description": trainer.description,
                    "all_plans":[]
                }
                for plans in trainer.planes_id:
                    planes ={
                        "plan_detailed":plans.serialize()
                    }
                    obj["all_plans"].append(planes)
                profesionals['trainers'].append(obj)

            for nutri in nutritionists:
                obj={
                    "id":nutri.id,
                    'role_id':nutri.role_id,
                    "email":nutri.email,
                    "name":nutri.name,
                    "lastname": nutri.lastname,
                    'avatar':nutri.avatar,
                    "register_date":nutri.date_created,
                    "specialties": nutri.specialties,
                    'is_active': nutri.active,
                    "background": nutri.background,
                    "profesional_title": nutri.profesional_title,
                    'title_vaidattion':nutri.nutritionist_validation_title,
                    "specialties": nutri.specialties,
                    "age": nutri.age,
                    "lastWork": nutri.lastWork,
                    "lastWorkyears": nutri.lastWorkyears,
                    "description": nutri.description,
                    "all_plans":[]
                }
                for plan in nutri.planes_id:
                    planes ={
                        "plan_detailed":plan.serialize()
                    }
                    obj['all_plans'].append(planes)
                profesionals['nutritionists'].append(obj)
            
            return jsonify(profesionals), 200
        
        if role_id == 2 and id == None:                 #### THIS BRINGS UP EVERY NUTRITIONIST
            all_nutritionist = Nutritionist.query.all()
            nutritionists = []
            for nutri in all_nutritionist:
                obj={
                    "id":nutri.id,
                    'role_id':nutri.role_id,
                    "email":nutri.email,
                    "name":nutri.name,
                    "lastname": nutri.lastname,
                    'avatar':nutri.avatar,
                    "register_date":nutri.date_created,
                    "specialties": nutri.specialties,
                    'is_active': nutri.active,
                    "background": nutri.background,
                    "profesional_title": nutri.profesional_title,
                    'title_vaidattion':nutri.nutritionist_validation_title,
                    "specialties": nutri.specialties,
                    "age": nutri.age,
                    "lastWork": nutri.lastWork,
                    "lastWorkyears": nutri.lastWorkyears,
                    "description": nutri.description,
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
                    "id":trainer.id,
                    'role_id':trainer.role_id,
                    "email":trainer.email,
                    "name":trainer.name,
                    "lastname": trainer.lastname,
                    'avatar':trainer.avatar,
                    "register_date":trainer.date_created,
                    "specialties": trainer.specialties,
                    'is_active':trainer.active,
                    "background": trainer.background,
                    "profesional_title": trainer.profesional_title,
                    "specialties": trainer.specialties,
                    "age": trainer.age,
                    "lastWork": trainer.lastWork,
                    "lastWorkyears": trainer.lastWorkyears,
                    "description": trainer.description,
                    'all_plans':[]
                }
                for plan in trainer.planes_id:
                    plans={
                        'plans_detail':plan.serialize()
                    }
                    obj['all_plans'].append(plans)
                trainers.append(obj)
            return jsonify(trainers)

        if role_id == 2 and id and document == None:             ####   THIS BIRNGS UP A SPECIFIC NUTRITIONIST
            single_nutritionist = Nutritionist.query.get(id)
            nutritionists = Nutritionist.query.all()
            nutri =[]
            if not single_nutritionist:
                return jsonify({'msg':'Nutritionist does not exist in database'})
            else:
                for nutritionist in nutritionists:
                    if nutritionist.id == id:
                        obj ={
                            "id":nutritionist.id,
                            'role_id':nutritionist.role_id,
                            "email":nutritionist.email,
                            "name":nutritionist.name,
                            "lastname": nutritionist.lastname,
                            'avatar':nutritionist.avatar,
                            "register_date":nutritionist.date_created,
                            "specialties": nutritionist.specialties,
                            'is_active': nutritionist.active,
                            "background": nutritionist.background,
                            "profesional_title": nutritionist.profesional_title,
                            'title_vaidattion':nutritionist.nutritionist_validation_title,
                            "specialties": nutritionist.specialties,
                            "age": nutritionist.age,
                            "lastWork": nutritionist.lastWork,
                            "lastWorkyears": nutritionist.lastWorkyears,
                            "description": nutritionist.description,
                            'all_plans':[]
                        }
                        for plan in nutritionist.planes_id:
                            all_plans={
                                'plans_detail':plan.serialize()
                            }
                            obj['all_plans'].append(all_plans)
                        nutri.append(obj)
                return jsonify(nutri)
        
        if role_id == 3 and id and document == None:                 #####           THIS BRINGS UP A SPECIFIC TRAINER
            single_trainer = Trainer.query.get(id)
            all_trainers = Trainer.query.all()
            personal_trainer = []
            if not single_trainer:
                return jsonify({"msg":"Trainer not found in database"}), 400
            else:
                for trainer in all_trainers:
                    if trainer.id == id:
                        obj ={
                            "id":trainer.id,
                            'role_id':trainer.role_id,
                            "email":trainer.email,
                            "name":trainer.name,
                            "lastname": trainer.lastname,
                            'avatar':trainer.avatar,
                            "register_date":trainer.date_created,
                            "specialties": trainer.specialties,
                            'is_active':trainer.active,
                            "background": trainer.background,
                            "profesional_title": trainer.profesional_title,
                            "specialties": trainer.specialties,
                            "age": trainer.age,
                            "lastWork": trainer.lastWork,
                            "lastWorkyears": trainer.lastWorkyears,
                            "description": trainer.description,
                            'all_plans':[]
                        }
                        for plan in trainer.planes_id:
                            all_plans={
                                'plans_detail':plan.serialize()
                            }
                            obj['all_plans'].append(all_plans)
                        personal_trainer.append(obj)          
                return jsonify(personal_trainer)

        if role_id == 2 and id and document:
            if document == 'background':
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/background/nutritionist'), filename)
            elif document == 'title':
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/profesional_title/nutritionist'), filename)
            elif document == 'title_validation':
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/title_validation'), filename)
            else:
                return jsonify({'msg':'URL input invalid'})

        if role_id == 3 and id and document:
            if document == 'background':
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/background/trainer'), filename)
            elif document == 'title':
                return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/profesional_title/trainer'), filename)
            else:
                return jsonify({'msg':'URL input invalid'})



    if request.method == 'PUT':
        if role_id != None and role_id != 2 and role_id != 3:       ### THIS VERIFIES THAT THE ROLE EXISTS WITHIN PROFESIONALS
            return jsonify({"msg":"role input not valid"}), 404
        if role_id == 2 and id:
            single_nutritionist= Nutritionist.query.get(id)
            if not single_nutritionist:
                return jsonify({'msg':'nutritionist does not exist in database'}), 404
        
            active = request.form.get('active')

            if not active or active == '':
                return jsonify({"msg":"Missing active field"}),404
        
            nutritionist = Nutritionist.query.get(id)
            nutritionist.active = False if not active == 'true' else True

            db.session.commit()
        
            return jsonify(nutritionist.active), 200
        
        if role_id == 3 and id:
            single_trainer= Trainer.query.get(id)
            if not single_trainer:
                return jsonify({'msg':'trainer does not exist in database'}), 404
        
            active = request.form.get('active')

            if not active or active == '':
                return jsonify({"msg":"Missing active field"}),404
        
            trainer = Trainer.query.get(id)
            trainer.active = False if not active == 'true' else True

            db.session.commit()
        
            return jsonify(trainer.active), 200

### ADMIN ROUTES   #####   GET ALL CLIENTS IN DATABASE OR SPECIFIC CLIENT BY ID

@app.route('/admin/client', methods=['GET'])
@app.route('/admin/client/<int:client_id>', methods=['GET','PUT'])
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
                    'avatar': client.avatar,
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
                            'avatar': client.avatar,
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
        single_client= Client.query.get(client_id)
        if not single_client:
            return jsonify({'msg':'client does not exist in database'}), 404
        
        active = request.form.get('active')

        if not active or active == '':
            return jsonify({"msg":"Missing name field"}),404
       
        client = Client.query.get(client_id)
        client.active = False if not active == 'true' else True

        db.session.commit()
      
        return jsonify(client.active), 200

   


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
                'user':{
                    'nutritionist_id': nutritionist.id,
                    'email': nutritionist.email,
                    'name': nutritionist.name,
                    'lastname': nutritionist.lastname,
                    'age':nutritionist.age,
                    'avatar':nutritionist.avatar,
                    'lasWork': nutritionist.lastWork,
                    'lastWorkedyears':nutritionist.lastWorkyears,
                    'active': nutritionist.active,
                    'created': nutritionist.date_created,
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
                data['user']['planes_id'].append(planes)
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
                'user':{
                    'trainer_id': trainer.id,
                    'email': trainer.email,
                    'name': trainer.name,
                    'lastname': trainer.lastname,
                    'age':trainer.age,
                    'avatar':trainer.avatar,
                    'lasWork': trainer.lastWork,
                    'lastWorkedyears':trainer.lastWorkyears,
                    'active': trainer.active,
                    'created': trainer.date_created,
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
               
                data['user']['planes_id'].append(planes)
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
                'user':{
                    'client_id': client.id,
                    'email': client.email,
                    'gender': client.gender,
                    'name': client.name,
                    'lastname': client.lastname,
                    'avatar':client.avatar,
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
                data['user']['planes_id'].append(planes)
            return jsonify(data), 200

###    PROFESIONAL ROUTES #### --REGISTER
@app.route('/register/profesional/<int:role>', methods=['POST']) ##REGISTER PROFESIONAL
def profesional_register(role):
        
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')   
    age = request.form.get('age')   
    description = request.form.get('description')   
    specialties = request.form.get('specialties')   
    
    if not email or email == '':
        return jsonify({"msg":"Missing email field"}),404
    if not password or password == '':
        return jsonify({"msg":"Missing password field"}),404
    if not name or name == '':
        return jsonify({"msg":"Missing name field"}),404
    if not lastname or lastname == '':
        return jsonify({"msg":"Missing last name field"}),404  
    if not age or age == '':
        return jsonify({"msg":"Missing age field"}),404  

    if role == 2:
        nutri = Nutritionist.query.filter_by(email =email).first()
        if nutri:
            return jsonify({"msg":'El email que intentas registrar ya existe, por favor, ingresa otro'}),400
        
        avatar = request.files['avatar']
        all_avatars = Nutritionist.query.filter_by(avatar=avatar.filename).first()
        if all_avatars:
            return jsonify({'msg':'Por favor, cambia el nombre de tu foto de perfil a tu correo o rut'}), 400
        
        if avatar and avatar.filename!= '' and allowed_files(avatar.filename, ALLOWED_EXTENSIONS_IMAGES):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/nutritionist'), filename)), 400
        else:
            return jsonify({"msg":"Tipo de archivo no permitido, tu foto de perfil tiene que ser en formato imagen"}), 400
            
        background = request.files['background']
        if not background:
            return ({'msg':'Por favor adjunta tus antecedentes'})
        all_backgrounds = Nutritionist.query.filter_by(background=background.filename).first()
        if all_backgrounds:
            return jsonify({'msg':'Por favor, cambia el nombre del archivo de tus antecedentes penales a tu correo o rut'}), 400
        if background and background.filename!= '' and allowed_files(background.filename, ALLOWED_EXTENSIONS_FILES):
            background_filename = secure_filename(background.filename)
            background.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/background/nutritionist'), background_filename))
        else:
            return jsonify({"msg":"El formato del archivo tiene que ser PDF"}), 400

        title = request.files['title']
        if not title:
            return ({'msg':'Por favor ingresa tu titulo profesional'}).first()
        all_titles = Nutritionist.query.filter_by(profesional_title=title.filename).first()
        if all_titles:
            return jsonify({'msg':'Por favor, cambia el nombre del archivo de tu titulo a tu correo o rut'}), 400
        if title and title.filename!= '' and allowed_files(title.filename, ALLOWED_EXTENSIONS_FILES):
            title_filename = secure_filename(title.filename)
            title.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/profesional_title/nutritionist'), title_filename))
        else:
            return jsonify({"msg":"El formato del archivo tiene que ser PDF"}), 400

        title_validation = request.files['title_validation']
        if not title_validation:
            return jsonify({'msg':'Por favor adjunto tu certificado de la super intendencia'})
        all_title_validation = Nutritionist.query.filter_by(nutritionist_validation_title = title_validation.filename ).first()
        if all_title_validation:
            return jsonify({'msg':'Por favor, cambia el nombre del archivo de super la intendencia a tu correo o rut'})

        if title_validation and title_validation.filename!= '' and allowed_files(title_validation.filename, ALLOWED_EXTENSIONS_FILES):
            title_validation_filename = secure_filename(title_validation.filename)
            title_validation.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/title_validation'), title_validation_filename))
        else:
            return jsonify({"msg":"El formato del archivo tiene que ser PDF"}), 400

        if not background or background == '':
            return jsonify({'msg':'background missing'})
        
        if not title:
            return jsonify({'msg':'missing title file'})
        
        if not title_validation:
            return jsonify({'msg':'missing title validation'})
        
        nutri = Nutritionist()
        nutri.email = email
        nutri.password = bcrypt.generate_password_hash(password)
        nutri.name = name
        nutri.lastname = lastname
        nutri.role_id = role
        nutri.description = description
        nutri.specialties = specialties
        nutri.age = age
        nutri.background = background_filename
        nutri.profesional_title = title_filename
        nutri.nutritionist_validation_title = title_validation_filename

        if avatar:
            nutri.avatar = filename
        

        db.session.add(nutri)
        db.session.commit()

        access_token = create_access_token(identity = nutri.email)
        data={
            'access_token': access_token,
            'user': nutri.serialize()
        }
        return jsonify(data), 200
    
    if role == 3:
        trainer = Trainer.query.filter_by(email = email).first()
        if trainer:
            return jsonify({"msg":'El email que intentas registrar ya existe, por favor, ingresa otro'}),400
        
        avatar = request.files['avatar']
        all_avatars = Trainer.query.filter_by(avatar=avatar.filename).first()
        if all_avatars:
            return jsonify({'msg':'Por favor, cambia el nombre de tu foto de perfil a tu correo o rut'}), 400
        if avatar and avatar.filename!= '' and allowed_files(avatar.filename, ALLOWED_EXTENSIONS_IMAGES):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/trainer'), filename))
        else:
            return jsonify({"msg":"Tipo de archivo no permitido, tu foto de perfil tiene que ser en formato imagen"}), 400
            
        background = request.files['background']
        if not background:
            return ({'msg':'Por favor, adjunta tus antecedentes penales'})
        all_backgrounds = Trainer.query.filter_by(background=background.filename).first()
        if all_backgrounds:
            return jsonify({'msg':' Por favor, cambia el nombre del archivo de tus antecedentes penales a tu correo o rut'}), 400
        
        if background and background.filename!= '' and allowed_files(background.filename, ALLOWED_EXTENSIONS_FILES):
            background_filename = secure_filename(background.filename)
            background.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/background/trainer'), background_filename))
        else:
            return jsonify({"msg":"El formato del archivo tiene que ser PDF"}), 400

        title = request.files['title']
        if not title:
            return ({'msg':'Por favor, adjunta tu titulo profesional'})
        all_titles = Trainer.query.filter_by(profesional_title=title.filename).first()
        if all_titles:
            return jsonify({'msg':'Por favor, cambia el nombre del archivo de tu titulo a tu correo o rut'}),400
        if title and title.filename!= '' and allowed_files(title.filename, ALLOWED_EXTENSIONS_FILES):
            title_filename = secure_filename(title.filename)
            title.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/profesional_title/trainer'), title_filename))
        else:
            return jsonify({"msg":"El formato del archivo tiene que ser PDF"}), 400

        

        trainer = Trainer()
        trainer.email = email
        trainer.password = bcrypt.generate_password_hash(password)
        trainer.name = name
        trainer.lastname = lastname
        trainer.role_id = role
        trainer.description = description
        trainer.specialties = specialties
        trainer.age = age
        trainer.background = background_filename
        trainer.profesional_title = title_filename

        if avatar:
            trainer.avatar = filename
    

        db.session.add(trainer)
        db.session.commit()

        access_token = create_access_token(identity = trainer.email)
        data={
            'access_token': access_token,
            'user': trainer.serialize()
        }
        return jsonify(data), 200





####         PROFESSIONAL EDIT PROFILE          ####
@app.route('/edit/profesional/<int:role_id>/<int:id>/', methods=['PUT'])
def edit_profesional_profile(role_id,id):
    if request.method == 'PUT':
        if role_id != None and role_id != 2 and role_id != 3:       ### THIS VERIFIES THAT THE ROLE EXISTS WITHIN PROFESIONALS
            return jsonify({"msg":"role input not valid"}), 404
        if role_id == 2 and id:
            single_nutritionist= Nutritionist.query.get(id)
            if not single_nutritionist:
                return jsonify({'msg':'nutritionist does not exist in database'}), 404
        
            age = request.form.get('age')
            specialties = request.form.get('specialties')
            description = request.form.get('description')
           

            if not age or age == '':
                return jsonify({"msg":"Missing age field"}),404            
            if not specialties or specialties == '':
                return jsonify({"msg":"Missing specialties field"}),404
            if not description or description == '':
                return jsonify({"msg":"Missing description field"}),404
            
            
        
            nutritionist = Nutritionist.query.get(id)
            nutritionist.age = age
            nutritionist.specialties = specialties
            nutritionist.description = description

            db.session.commit()
        
            return jsonify({'msg':'update complete'}), 200
        
        if role_id == 3 and id:
            single_trainer= Trainer.query.get(id)
            if not single_trainer:
                return jsonify({'msg':'trainer does not exist in database'}), 404
        
            age = request.form.get('age')
            specialties = request.form.get('specialties')
            description = request.form.get('description')

            if not age or age == '':
                return jsonify({"msg":"Missing age field"}),404            
            if not specialties or specialties == '':
                return jsonify({"msg":"Missing specialties field"}),404
            if not description or description == '':
                return jsonify({"msg":"Missing description field"}),404
            
            
        
            trainer = Trainer.query.get(id)
            trainer.age = age
            trainer.specialties = specialties
            trainer.description = description

            db.session.commit()
        
            return jsonify({'msg':'update complete'}), 200



###    PROFESIONAL CREATE A WORKOUT AND DIET PLAN       #####

@app.route('/profesional/<int:role_id>/<int:plan_id>', methods=['POST'])
def profesional_plan(role_id, plan_id):
    if not role_id:
        return jsonify({'msg':'missing role input'})
    if role_id == 2:

        diet = request.files['diet']
        oldfilename = request.form.get('oldfilename')       

        if not diet:
            return jsonify({'msg':'missing diet plan'})
        all_diets = Planes.query.filter_by(diet_plan=diet.filename).first()
        if all_diets:
            return({'msg':'Por favor, cambia el nombre de la dieta al nombre de tu cliente más el numero del plan creado '})
        if diet and diet.filename!= '' and allowed_files(diet.filename, ALLOWED_EXTENSIONS_FILES):
            filename = secure_filename(diet.filename)
            diet.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'diets'), filename))
            if oldfilename:
                if os.path.exists(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'diets'), oldfilename)):
                    os.remove(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'diets'), oldfilename))
        else:
            return jsonify({"msg":"Tipo de archivo no permitido"}), 400
        
        diet_plan = Planes.query.get(plan_id)
        diet_plan.diet_plan = filename
            
        db.session.commit()
        return jsonify(filename)

    if role_id == 3:

        workout = request.files['workout']
        oldfilename = request.form.get('oldfilename')       

        if not workout:
            return jsonify({'msg':'missing workout plan'})
        all_workouts = Planes.query.filter_by(workout_plan=workout.filename).first()
        if all_workouts:
            return({'msg':'Por favor, cambia el nombre de tu plan de entrenamiento al nombre de tu cliente más el numero del plan creado'})
        if workout and workout.filename!= '' and allowed_files(workout.filename, ALLOWED_EXTENSIONS_FILES):
            filename = secure_filename(workout.filename)
            workout.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'workouts'), filename))
            if oldfilename:
                if os.path.exists(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'workouts'), oldfilename)):
                    os.remove(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'workouts'), oldfilename))
        else:
            return jsonify({"msg":"file is not allowed"}), 400
        
        workout_plan = Planes.query.get(plan_id)
        workout_plan.workout_plan = filename
        
        db.session.commit()
        return jsonify(filename)




###    CLIENT ROUTES   #### -- REGISTER
@app.route('/register/client', methods=['POST'])        ### REGISTER CLIENT
def client_register():

    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    oldfilename = request.form.get('oldfilename')
    

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
        return jsonify({"msg":"El email que intenas registrar, ya existe, por favor, ingresa otro"}), 400
    
    file = request.files['avatar']
    all_avatars = Client.query.filter_by(avatar=file.filename).first()
    if all_avatars:
        return jsonify({'msg':'Por favor, cambia el nombre de tu foto de perfil a tu correo o rut'}), 400
    if file and file.filename != '' and allowed_files(file.filename, ALLOWED_EXTENSIONS_IMAGES):
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/clients'), filename))
        # if oldfilename != 'default_profile.png':
        #     if os.file.exists(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/clients'), oldfilename)):
        #         os.remove(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/clients'), oldfilename))
        
    else:
        return jsonify({"msg":"Tipo de archivo no permitido, tu foto de perfil tiene que ser en formato imagen"}), 400
        
    
    client = Client()
    
    client.email = email
    client.password = bcrypt.generate_password_hash(password)
    client.name = name
    client.lastname = lastname
    client.role_id = 4

    if file:
        client.avatar = filename
    
    db.session.add(client)
    db.session.commit()

    access_token = create_access_token(identity=client.email)
    data = {
        'access_token': access_token,
        'user': client.serialize()
    }

    return jsonify(data), 200
    

@app.route('/avatar/edit/<int:role_id>/<int:id>', methods=['PUT'])
def edit_client(role_id,id):
    if role_id == 2:
        specific_nutritionist= Nutritionist.query.get(id)
        if not specific_nutritionist:
            return jsonify({'msg':'Nutritionist does not exist in database'}), 404
            
        avatar = request.files['avatar']
        oldfilename = request.form.get('oldfilename')       
                
        if avatar and avatar.filename != '' and allowed_files(avatar.filename, ALLOWED_EXTENSIONS_IMAGES):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/nutritionist'), filename))
            if oldfilename != 'default_profile.png':
                if os.path.exists(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/nutritionist'), oldfilename)):
                    os.remove(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/nutritionist'), oldfilename))
            
        nutritionist = Nutritionist.query.get(id)
        nutritionist.avatar = filename
                

        db.session.commit()
            
        return jsonify({'msg':'nutritionist pictures update complete'}), 200

    if role_id == 3:
        specific_trainer= Trainer.query.get(id)
        if not specific_trainer:
            return jsonify({'msg':'Client does not exist in database'}), 404
            
        avatar = request.files['avatar']
        oldfilename = request.form.get('oldfilename')       
                
        if avatar and avatar.filename != '' and allowed_files(avatar.filename, ALLOWED_EXTENSIONS_IMAGES):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/trainer'), filename))
            if oldfilename != 'default_profile.png':
                if os.path.exists(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/trainer'), oldfilename)):
                    os.remove(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/trainer'), oldfilename))
            
        client = Trainer.query.get(id)
        client.avatar = filename
                

        db.session.commit()
            
        return jsonify({'msg':' trainer profile picupdate complete'}), 200

    if role_id == 4:
        specific_client= Client.query.get(id)
        if not specific_client:
            return jsonify({'msg':'Client does not exist in database'}), 404
            
        avatar = request.files['avatar']
        oldfilename = request.form.get('oldfilename')       
                
        if avatar and avatar.filename != '' and allowed_files(avatar.filename, ALLOWED_EXTENSIONS_IMAGES):
            filename = secure_filename(avatar.filename)
            avatar.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/clients'), filename))
            if oldfilename != 'default_profile.png':
                if os.path.exists(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/clients'), oldfilename)):
                    os.remove(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar/clients'), oldfilename))
            
        client = Client.query.get(id)
        client.avatar = filename
                

        db.session.commit()
            
        return jsonify({'msg':'update complete'}), 200


###    CLIENT ROUTES   #### -- CLIENT CREATE PLAN AND CHECK HIS PLANNES OR SPECIFIC PLAN PER CLIENT
@app.route('/client/plan/<int:id_client>', methods=['GET'])
@app.route('/client/plan/<int:id_client>/<int:plan_id>', methods=['GET'])
@app.route('/client/plan/<int:id_client>/<int:plan_id>/<schedule>/<filename>', methods=['GET'])
@app.route('/client/plan/<int:id_client>/<mail_client>/<mail_trainer>/<mail_nutritionist>', methods=['POST'])
def client_plan(id_client = None, plan_id= None, schedule = None, filename = None, mail_client = None ,mail_trainer= None ,mail_nutritionist= None):   
    if request.method == 'GET':
        client = Client.query.get(id_client)
        plan = Planes.query.filter_by(id=plan_id).first()
        if not client:
            return jsonify({"msg":"client not found"}), 400
        else:
            if not plan_id:     ### THIS BRINGS EVERY PLAN A CLIENT HAS
                _client = Planes.query.filter_by(client_id=id_client).all()
                client_plans= list(map(lambda plan: plan.serialize(), _client))
                key = client_plans
                return jsonify (key), 200
            elif plan_id and schedule == None:               #### THIS BRINGS A SPECIFIC PLAN A CLIENT HAS
                _client = Planes.query.filter_by(client_id=id_client).all()
                client_plans= list(map(lambda plan: plan.serialize(), _client))
                key = client_plans
                another_key = list(filter(lambda plan: plan if plan['id'] == plan_id else None, key ))
                if not another_key:
                    return jsonify({"msg":"plan does not exist"})                
                return jsonify(another_key), 200
            
            else:
                if schedule == 'workout':
                    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'workouts'), filename)
                elif schedule == 'diet':
                    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'diets'), filename) 
                else:
                    return jsonify({'msg':'Invalid request, you url must contain either "workout" or "diet"'})      




    if request.method == 'POST':        #### THIS ALLOWS CLIENT TO CREATE PLAN
        if not request.is_json:
            return jsonify({'msg':'Missing JSON request'}), 400

        objective = request.json.get('objective')
        client_id = request.json.get('client_id')
        client_email = request.json.get('client_email')
        nutritionist_email = request.json.get('nutritionist_email')
        trainer_email = request.json.get('trainer_email')
        actividad_fisica = request.json.get('actividad_fisica')
        alcohol = request.json.get('alcohol')
        alergias = request.json.get('alergias')
        altura = request.json.get('altura')
        ansiedad = request.json.get('ansiedad')
        apetito = request.json.get('apetito')
        ayunos = request.json.get('ayunos')
        cintura = request.json.get('cintura')
        ciruguias = request.json.get('cirugias')
        comment = request.json.get('comment')
        digestion = request.json.get('digestion')
        embarazo = request.json.get('embarazo')
        enfermedades = request.json.get('enfermedades')
        lesiones = request.json.get('lesiones')
        medicamento = request.json.get('medicamento')
        orina = request.json.get('orina')
        peso = request.json.get('peso')
        sintomas = request.json.get('sintomas')
        suplementos = request.json.get('suplementos')
        tabaco = request.json.get('tabaco')        

        if not objective or objective == '':
            return jsonify({'msg':'Missing objective'}), 400
        if not client_id or client_id == '':
            return jsonify({'msg':'Your ID is missing '}), 400
        if not Client.query.filter_by(id=client_id).all():
            return jsonify({'msg':'Client does not exists in database'})
        if not  client_id == id_client:
            return jsonify({'msg':'Client id must match client id in url'})
        if not nutritionist_email or nutritionist_email == '':
            return jsonify({'msg':'Missing nutritionist'}), 400
        if not Nutritionist.query.filter_by(email = nutritionist_email).all():
            return jsonify({"msg":"Nutritionist does not exist in database"})
        if not trainer_email or trainer_email == '':
            return jsonify({'msg':'Missing trainer'}), 400
        if not Trainer.query.filter_by(email=trainer_email).all():
            return jsonify({'msg':"Trainer does not exist in database"})        
                    
        
        plan = Planes()
        plan.objective = objective
        plan.client_id = client_id
        plan.client_email = client_email
        plan.nutritionist_email = nutritionist_email
        plan.trainer_email = trainer_email
        plan.actividad_fisica= actividad_fisica
        plan.alcohol = alcohol
        plan.alergia = alergias
        plan.altura = altura
        plan.ansiedad = ansiedad
        plan.apetito = apetito
        plan.ayunos = ayunos
        plan.cintura = cintura
        plan.cirugias = ciruguias
        plan.comment = comment
        plan.digestion = digestion
        plan.embarazo = embarazo
        plan.enfermedades = enfermedades
        plan.lesiones = lesiones
        plan.medicamento = medicamento
        plan.orina = orina
        plan.peso = peso
        plan.sintomas = sintomas
        plan.suplemento_nutricional = suplementos
        plan.tabaco = tabaco 

        db.session.add(plan)
        db.session.commit()

        msg = Message('Fit good Nuevo Plan', recipients=['fit.good.app@gmail.com'], bcc=[mail_client,mail_trainer,mail_nutritionist])
        msg.body = 'Un nuevo plan ha sido contratado, el nombre del entrenador es: ' + plan.trainer.name + ' , el nombre del nutricionista es: ' + plan.nutritionist.name

        
        mail.send(msg)


        return jsonify(plan.serialize()),200


### GET ALL AVATARS     ######

@app.route('/avatar/<int:role_id>/<filename>', methods=['GET'])
def get_avatar(role_id, filename):
    if role_id:
        if role_id == 2:
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/avatar/nutritionist'), filename)
        if role_id == 3:        
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/avatar/trainer'), filename)
        if role_id == 4:        
            return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'images/avatar/clients'), filename)
        else:
            return jsonify({'msg':'error'})
    

@app.route('/contact/profesional/<int:role_id>/<int:id_plan>', methods=['GET'])
@app.route('/contact/profesional/<int:role_id_send>/<int:role_id_recieve>/<int:id_plan>', methods=['POST'])
def contact_profesional(role_id = None,role_id_send=None, role_id_recieve = None ,id_plan=None):
    
    
    if request.method == 'GET':
        if role_id == 2:
            plan_messages = ClientNutritionist.query.filter_by(plan_id=id_plan).all()
            all_messages = list(map(lambda contact: contact.serialize(),plan_messages))
            messages = all_messages
            return jsonify(messages)
        if role_id == 3:
            plan_messages = ClientTrainer.query.filter_by(plan_id=id_plan).all()
            all_messages = list(map(lambda contact: contact.serialize(),plan_messages))
            messages = all_messages
            return jsonify(messages)


    if request.method == 'POST':

        if role_id_send == 2 and role_id_recieve == 4:

            client_email = request.json.get('client_email')
            nutritionist_email = request.json.get('nutritionist_email')
            plan_id = request.json.get('plan_id')
            comment = request.json.get('comment')
            sender = request.json.get('sender')

            
            if not comment or comment == '':
                return jsonify({'msg':'you must enter a comment'})
            if not nutritionist_email or nutritionist_email == '':
                return jsonify({'msg':'you must choose the nutritionist id'})
            if not plan_id or plan_id == '':
                return jsonify({'msg':'you must choose a plan id'})
            if not client_email or client_email == '':
                return jsonify({'msg':'you must entrer client id'})
            if not sender or sender == '':
                return jsonify({'msg':'you must entrer a sender'})
            if not Planes.query.filter_by(id=id_plan).all():
                return jsonify({'msg':'plan not found in data base'})
            if not Client.query.filter_by(email=client_email).all():
                return jsonify({'msg':'client not found in data base'})
            if not Nutritionist.query.filter_by(email=nutritionist_email).all():
                return jsonify({'msg':'nutritionist not found in data base'})
                
            client_nutritionist = ClientNutritionist()
            client_nutritionist.client_email = client_email
            client_nutritionist.nutritionist_email = nutritionist_email
            client_nutritionist.plan_id = plan_id
            client_nutritionist.comment = comment
            client_nutritionist.sender = sender

            db.session.add(client_nutritionist)
            db.session.commit()

            msg = Message('Nuevo Mensaje', recipients=['fit.good.app@gmail.com'], bcc=[client_email])
            msg.body = 'Tu nutricionista te ha enviado un mensaje, revisalo en tu Perfil' 

            
            mail.send(msg)

            return jsonify(client_nutritionist.serialize())
        if role_id_send == 4 and role_id_recieve == 2:

            client_email = request.json.get('client_email')
            nutritionist_email = request.json.get('nutritionist_email')
            plan_id = request.json.get('plan_id')
            comment = request.json.get('comment')
            sender = request.json.get('sender')


            # if not plan_id == id_plan:
            #     return jsonify({'msg':'you must match your plan id with the url input'})
            if not comment or comment == '':
                return jsonify({'msg':'you must enter a comment'})
            if not nutritionist_email or nutritionist_email == '':
                return jsonify({'msg':'you must choose the nutritionist email'})
            if not plan_id or plan_id == '':
                return jsonify({'msg':'you must choose a plan id'})
            if not client_email or client_email == '':
                return jsonify({'msg':'you must entrer client email'})
            if not sender or sender == '':
                return jsonify({'msg':'you must entrer a sender'})
            if not Planes.query.filter_by(id=id_plan).all():
                return jsonify({'msg':'plan not found in data base'})
            if not Client.query.filter_by(email=client_email).all():
                return jsonify({'msg':'client not found in data base'})
            if not Nutritionist.query.filter_by(email=nutritionist_email).all():
                return jsonify({'msg':'nutritionist not found in data base'})
                
            client_nutritionist = ClientNutritionist()
            client_nutritionist.client_email = client_email
            client_nutritionist.nutritionist_email = nutritionist_email
            client_nutritionist.plan_id = plan_id
            client_nutritionist.comment = comment
            client_nutritionist.sender = sender

            db.session.add(client_nutritionist)
            db.session.commit()

            msg = Message('Nuevo Mensaje', recipients=['fit.good.app@gmail.com'], bcc=[nutritionist_email])
            msg.body = 'Tu cliente te ha enviado un mensaje, revisalo en tu  Perfil' 

            
            mail.send(msg)

            return jsonify(client_nutritionist.serialize())
            
        if role_id_send == 3 and role_id_recieve == 4:

            client_email = request.json.get('client_email')
            trainer_email = request.json.get('trainer_email')
            plan_id = request.json.get('plan_id')
            comment = request.json.get('comment')
            sender = request.json.get('sender')


            
            if not comment or comment == '':
                return jsonify({'msg':'you must enter a comment'})
            if not trainer_email or trainer_email == '':
                return jsonify({'msg':'you must choose the trainer id'})
            if not plan_id or plan_id == '':
                return jsonify({'msg':'you must choose a plan id'})
            if not client_email or client_email == '':
                return jsonify({'msg':'you must entrer client id'})
            if not sender or sender == '':
                return jsonify({'msg':'you must entrer a sender'})
            if not Planes.query.filter_by(id=id_plan).all():
                return jsonify({'msg':'plan not found in data base'})
            if not Trainer.query.filter_by(email=trainer_email).all():
                return jsonify({'msg':'plan not found in data base'})

            client_trainer = ClientTrainer()
            client_trainer.client_email = client_email
            client_trainer.trainer_email = trainer_email
            client_trainer.plan_id = plan_id
            client_trainer.comment = comment
            client_trainer.sender = sender

            db.session.add(client_trainer)
            db.session.commit()

            msg = Message('Nuevo Mensaje', recipients=['fit.good.app@gmail.com'], bcc=[client_email])
            msg.body = 'Tu entrenador te ha enviado un mensaje, revisalo en tu Perfil' 

            
            mail.send(msg)

            return jsonify(client_trainer.serialize())

        if role_id_send == 4 and role_id_recieve == 3:

            client_email = request.json.get('client_email')
            trainer_email = request.json.get('trainer_email')
            plan_id = request.json.get('plan_id')
            comment = request.json.get('comment')
            sender = request.json.get('sender')


            
            if not comment or comment == '':
                return jsonify({'msg':'you must enter a comment'})
            if not trainer_email or trainer_email == '':
                return jsonify({'msg':'you must choose the trainer email'})
            if not plan_id or plan_id == '':
                return jsonify({'msg':'you must choose a plan id'})
            if not client_email or client_email == '':
                return jsonify({'msg':'you must entrer client id'})
            if not sender or sender == '':
                return jsonify({'msg':'you must entrer a sender'})
            if not Planes.query.filter_by(id=id_plan).all():
                return jsonify({'msg':'plan not found in data base'})
            if not Trainer.query.filter_by(email=trainer_email).all():
                return jsonify({'msg':'plan not found in data base'})

            client_trainer = ClientTrainer()
            client_trainer.client_email = client_email
            client_trainer.trainer_email = trainer_email
            client_trainer.plan_id = plan_id
            client_trainer.comment = comment
            client_trainer.sender = sender

            db.session.add(client_trainer)
            db.session.commit()

            msg = Message('Nuevo Mensaje', recipients=['fit.good.app@gmail.com'], bcc=[trainer_email])
            msg.body = 'Tu cliente te ha enviado un mensaje, revisalo en tu Perfil' 

            
            mail.send(msg)

            return jsonify(client_trainer.serialize())
        

def send_reset_email_client(user):
    token = user.get_reset_token(app.config['SECRET_KEY'])
    confirm_url = 'http://localhost:3000/confirmation/'+'4'+'/' + token
    msg = Message('Cambiar Contraseña',
                    sender='fit.good.app@gmail.com',
                    recipients=[user.email])
    msg.body = f''' Para cambiar tu contraseña, haz click en el siguiente link:
    
    {render_template('email_confirmation.html', token = token, confirm_url=confirm_url,_external=True)}
    
    Si no haz solicitado el cambio de tu contraseña, simplemente ignora este correo
     '''

    mail.send(msg)
def send_reset_email_trainer(user):
    token = user.get_reset_token(app.config['SECRET_KEY'])
    confirm_url = 'http://localhost:3000/confirmation/'+'3'+'/' + token
    msg = Message('Cambiar Contraseña',
                    sender='fit.good.app@gmail.com',
                    recipients=[user.email])
    msg.body = f''' Para cambiar tu contraseña, haz click en el siguiente link:
    
    {render_template('email_confirmation.html', token = token, confirm_url=confirm_url,_external=True)}
    
    Si no haz solicitado el cambio de tu contraseña, simplemente ignora este correo
     '''

    mail.send(msg)
def send_reset_email_nutritionist(user):
    token = user.get_reset_token(app.config['SECRET_KEY'])
    confirm_url = 'http://localhost:3000/confirmation/' +'2'+'/' +token
    msg = Message('Cambiar Contraseña',
                    sender='fit.good.app@gmail.com',
                    recipients=[user.email])
    msg.body = f''' Para cambiar tu contraseña, haz click en el siguiente link:
    
    {render_template('email_confirmation.html', token = token, confirm_url=confirm_url,_external=True)}
    
    Si no haz solicitado el cambio de tu contraseña, simplemente ignora este correo
     '''

    mail.send(msg)

@app.route('/reset_password/<int:role_id>', methods=['GET','POST'])
def reset_request(role_id):

    if role_id == 2:            

        email = request.json.get('email')
        if not email or email == '':
            return jsonify({'msg':'you must enter an email'}), 404

        nutritionist = Nutritionist.query.filter_by(email = email).first()
        if not nutritionist:
            return jsonify({'msg':"Nutritionist doesn't exist"}), 400
        
        send_reset_email_nutritionist(nutritionist)

        return jsonify({'msg':'Te hemos enviado un correo'})
    if role_id == 3:            

        email = request.json.get('email')
        if not email or email == '':
            return jsonify({'msg':'you must enter an email'}), 404

        trainer = Trainer.query.filter_by(email = email).first()
        if not trainer:
            return jsonify({'msg':"Trainer doesn't exist"}), 400
        
        send_reset_email_trainer(trainer)

        return jsonify({'msg':'Te hemos enviado un correo'})
    if role_id == 4:            

        email = request.json.get('email')
        if not email or email == '':
            return jsonify({'msg':'you must enter an email'}), 404

        client = Client.query.filter_by(email = email).first()
        if not client:
            return jsonify({'msg':"client doesn't exist"}), 400
        
        send_reset_email_client(client)

        return jsonify({'msg':'Te hemos enviado un correo'})

@app.route('/reset_password/<int:role_id>/<token>', methods=['GET','POST'])
def reset_token(role_id,token):

    if role_id == 2:
        password = request.json.get('password')

        nutritionist = Nutritionist.verify_reset_token(token, app.config['SECRET_KEY'])
        if not nutritionist:
            return jsonify({'msg':'Token es invalido o ha expirado'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password)
        nutritionist.password = hashed_password

        db.session.commit()

        return jsonify({'msg':'Password actualizado'}), 200

    if role_id == 3:
        password = request.json.get('password')

        trainer = Trainer.verify_reset_token(token, app.config['SECRET_KEY'])
        if not trainer:
            return jsonify({'msg':'Token es invalido o ha expirado'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password)
        trainer.password = hashed_password

        db.session.commit()

        return jsonify({'msg':'Password actualizado'}), 200

    if role_id == 4:
        password = request.json.get('password')

        client = Client.verify_reset_token(token, app.config['SECRET_KEY'])
        if not client:
            return jsonify({'msg':'Token es invalido o ha expirado'}), 400
        
        hashed_password = bcrypt.generate_password_hash(password)
        client.password = hashed_password

        db.session.commit()

        return jsonify({'msg':'Password actualizado'}), 200


@app.route('/contact-us', methods=['POST'])
def contact():
    if not request.is_json:
        return jsonify({'msg':'Missing JSON request'})
    
    name = request.json.get('name')
    email = request.json.get('email')
    message = request.json.get('message')

    if not name or name =='':
        return jsonify({"msg": 'missing name field'}), 400
    if not email or email =='':
        return jsonify({"msg": 'missing email field'}), 400
    if not message or message =='':
        return jsonify({"msg": 'missing message field'}), 400

    data = {
        'name' : name,
        'email': email,
        'message': message
    }

    msg = Message('Contacto Fit Good', sender = email, recipients=['fit.good.app@gmail.com'])
    
    msg.html = render_template('email_template.html', data=data )
    mail.send(msg)

    return jsonify({"success": "mail sent"}), 200
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