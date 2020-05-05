from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
# from app import app


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
   
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }
#######
# Administrador
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    lastname = db.Column(db.String(100), nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable = False)
    role = db.relationship(Role)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "lastname": self.lastname,
            "role": self.role.serialize(),
            "created": self.date_created,
        }
########
# CLIENTE
class Client(db.Model):
    __tablename__ = 'client'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False )
    planes_id = db.relationship('Planes', backref ='client_detail', lazy = True )
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    client_trainer = db.relationship('ClientTrainer', backref='client_author', lazy=True)
    client_nutritionist = db.relationship('ClientNutritionist', backref='client_author', lazy=True)
    # objective = db.relationship('Objective', backref ='client_detail', lazy=True)
    # age = db.Column(db.Integer, nullable=True)
    avatar = db.Column(db.String(100), nullable=True, default='default_profile.png')
    role = db.relationship('Role')
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    active = db.Column(db.Boolean, nullable=True ,default = True)

    def serialize(self):
        return {
            "client_id": self.id,
            'gender':self.gender,
            "name": self.name,
            "lastname": self.lastname,
            "email": self.email,
            "avatar": self.avatar,
            "role": self.role.serialize(),
            "created": self.date_created,
            "planes_id": self.planes_id,
            "active": self.active

        }

    def get_reset_token(self,secret_key ,expires_sec=1800):
        s = Serializer(secret_key, expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token, secret_key):
        s = Serializer(secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Client.query.get(user_id)

######static\images\avatar\default_profile.png
# PROFESIONALES (Personal trainer y nutricionista)
class Nutritionist(db.Model):
    __tablename__ = 'nutritionist'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    planes_id = db.relationship('Planes', backref = 'nutritionist_detail', lazy=True)
    client_trainer = db.relationship('ClientNutritionist', backref='nutritionist_author', lazy=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(100), nullable=True, default='default_profile.png')
    background = db.Column(db.String(100), nullable=False)
    profesional_title = db.Column(db.String(100), nullable=False)
    nutritionist_validation_title = db.Column(db.String(100), nullable=True)
    specialties = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    lastWork = db.Column(db.String(100), nullable=True)
    lastWorkyears = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    role = db.relationship(Role)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    active = db.Column(db.Boolean, nullable=True ,default = False)


    def serialize(self):
        return {
            "nutritionist_id": self.id,
            "active":self.active,
            "email": self.email,
            "name": self.name,
            "lastname": self.lastname,
            'gender':self.gender,
            "avatar": self.avatar,
            "background": self.background,
            "profesional_title": self.profesional_title,
            'title_vaidattion':self.nutritionist_validation_title,
            "specialties": self.specialties,
            "age": self.age,
            "lastWork": self.lastWork,
            "lastWorkyears": self.lastWorkyears,
            "description": self.description,
            "role": self.role.serialize(),
            "created": self.date_created,
            "planes_id": self.planes_id

        }

    def get_reset_token(self,secret_key ,expires_sec=1800):
        s = Serializer(secret_key, expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token, secret_key):
        s = Serializer(secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Nutritionist.query.get(user_id)

class Trainer(db.Model):
    __tablename__ = 'trainer'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    planes_id = db.relationship('Planes', backref = 'trainer_detail', lazy=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(100), nullable=True, default='default_profile.png')
    background = db.Column(db.String(100), nullable=False)
    profesional_title = db.Column(db.String(100), nullable=False)
    specialties = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    lastWork = db.Column(db.String(100), nullable=True)
    lastWorkyears = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    role = db.relationship(Role)
    client_trainer = db.relationship('ClientTrainer', backref='trainer_author', lazy=True)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    active = db.Column(db.Boolean, nullable=True , default = False)


    def serialize(self):
        return {
            "trainer_id": self.id,
            "active":self.active,
            "email": self.email,
            "name": self.name,
            "lastname": self.lastname,
            'gender':self.gender,
            "avatar": self.avatar,
            "background": self.background,
            "profesional_title": self.profesional_title,
            "specialties": self.specialties,
            "age": self.age,
            "lastWork": self.lastWork,
            "lastWorkyears": self.lastWorkyears,
            "description": self.description,
            "role": self.role.serialize(),
            "created": self.date_created,
            "planes_id": self.planes_id

        }
    
    def get_reset_token(self,secret_key ,expires_sec=1800):
        s = Serializer(secret_key, expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token, secret_key):
        s = Serializer(secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Trainer.query.get(user_id)
####### CONVERSAR SI ESTO VA O NO
#  Plan de cada cliente q tiene nut y pt en cada plan para q quede como historial 
class Planes(db.Model):
    __tablename__ = 'planes'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    nutritionist_email = db.Column(db.Integer, db.ForeignKey('nutritionist.email'), nullable=False)
    trainer_email = db.Column(db.Integer, db.ForeignKey('trainer.email',), nullable=False)
    client = db.relationship('Client')
    nutritionist = db.relationship('Nutritionist')
    trainer = db.relationship('Trainer')
    objective = db.Column(db.String(250), nullable=False)
    comment = db.Column(db.Text, nullable = True)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    active = db.Column(db.String(50), nullable=True, default = 'active')
    embarazo = db.Column(db.String(100), nullable=True)
    enfermedades = db.Column(db.String(100), nullable=True)
    medicamento = db.Column(db.String(100), nullable=True)
    cirugias = db.Column(db.String(100), nullable=True)
    orina = db.Column(db.String(100), nullable=True)
    digestion = db.Column(db.String(100), nullable=True)
    sintomas = db.Column(db.String(100), nullable=True)#signos y sintomas
    ayunos = db.Column(db.String(100), nullable=True)
    apetito = db.Column(db.String(100), nullable=True)
    ansiedad = db.Column(db.String(100), nullable=True)
    tabaco = db.Column(db.String(100), nullable=True)
    alcohol = db.Column(db.String(100), nullable=True)
    actividad_fisica = db.Column(db.String(100), nullable=True)
    suplemento_nutricional = db.Column(db.String(100), nullable=True)
    lesiones = db.Column(db.String(100), nullable=True)
    alergia = db.Column(db.String(100), nullable=True)
    peso = db.Column(db.String(100), nullable=True)
    altura = db.Column(db.String(100), nullable=True)
    cintura = db.Column(db.String(100), nullable=True)
    workout_plan = db.Column(db.String(100), nullable=True )
    diet_plan = db.Column(db.String(100), nullable=True)


    # schedule = db.relationship('Schedule',backref = 'plan_detail', lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "client_id": self.client_detail.id,
            'client_email':self.client_detail.email,
            'client_name':self.client_detail.name,
            'client_lastname':self.client_detail.lastname,
            "nutritionist_id": self.nutritionist.id,
            "nutritionist_email": self.nutritionist_email,
            'nutritionist_name':self.nutritionist_detail.name,
            'nutritionist_last_name':self.nutritionist_detail.lastname,
            'nutritionist_avatar':self.nutritionist_detail.avatar,
            "trainer_id": self.trainer.id,
            "trainer_email": self.trainer_email,
            'trainer_name':self.trainer_detail.name,
            'trainer_last_name':self.trainer_detail.lastname,
            'trainer_avatar':self.trainer_detail.avatar,
            "objective" : self.objective,
            "comment" : self.comment,
            "created" : self.date_created,
            "active": self.active,
            'embarazo':self.embarazo,
            'medicamento':self.medicamento,
            'ciruguias':self.cirugias,
            'sintomas':self.sintomas,
            'suplementos':self.suplemento_nutricional,
            'lesiones':self.lesiones,
            'altura':self.altura,
            'cintura':self.cintura,
            'alcohol':self.alcohol,
            'peso':self.peso,
            'orina':self.orina,
            'digestion':self.digestion,
            'ansiedad':self.ansiedad,
            'ayunos':self.ayunos,
            'alergias':self.alergia,
            'tabaco':self.tabaco,
            'actividad_fisica':self.actividad_fisica,
            'enfermedades':self.enfermedades,
            'apetito':self.apetito,
            'entrenamiento':self.workout_plan,
            'dieta':self.diet_plan
            # 'schedule': self.schedule
        }
    


class ClientTrainer(db.Model):
    __tablename__='client_trainer'
    id = db.Column(db.Integer, primary_key=True)
    client_email = db.Column(db.Integer, db.ForeignKey('client.email'), nullable=False)
    trainer_email = db.Column(db.Integer, db.ForeignKey('trainer.email'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
    comment = db.Column(db.String(250), nullable=True)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    sender =  db.Column(db.String(250), nullable=True)

    def serialize(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'client_email':self.client_email,
            'client_name':self.client_author.name,
            'client_lastname':self.client_author.lastname,
            'trainer_email':self.trainer_email,
            'trainer_name':self.trainer_author.name,
            'trainer_lastname':self.trainer_author.lastname,
            'comment':self.comment,
            'date_created':self.date_created,
            "sender": self.sender
        }
class ClientNutritionist(db.Model):
    __tablename__='client_nutritionist'
    id = db.Column(db.Integer, primary_key=True)
    client_email = db.Column(db.Integer, db.ForeignKey('client.email'), nullable=False)
    nutritionist_email = db.Column(db.Integer, db.ForeignKey('nutritionist.email'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
    comment = db.Column(db.String(250), nullable=True)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    sender =  db.Column(db.String(250), nullable=True)



    def serialize(self):
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'client_email':self.client_email,
            'client_name':self.client_author.name,
            'client_lastname':self.client_author.lastname,
            'nutritionist_email':self.nutritionist_email,
            'nutritionist_name':self.nutritionist_author.name,
            'nutritionist_lastname':self.nutritionist_author.lastname,
            'comment':self.comment,
            'date_created':self.date_created,
            "sender": self.sender

        }

    