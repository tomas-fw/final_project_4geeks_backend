from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


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
######static\images\avatar\default_profile.png
# PROFESIONALES (Personal trainer y nutricionista)
class Nutritionist(db.Model):
    __tablename__ = 'nutritionist'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    planes_id = db.relationship('Planes', backref = 'nutritionist_detail', lazy=True)
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
####### CONVERSAR SI ESTO VA O NO
#  Plan de cada cliente q tiene nut y pt en cada plan para q quede como historial 
class Planes(db.Model):
    __tablename__ = 'planes'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    nutritionist_id = db.Column(db.Integer, db.ForeignKey('nutritionist.id'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id',), nullable=False)
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
            "client_id": self.client_id,
            'client_name':self.client_detail.name,
            "nutritionist_id": self.nutritionist_id,
            'nutritionist_name':self.nutritionist.name,
            "trainer_id": self.trainer_id,
            'trainer_name':self.trainer.name,
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
    


# class Schedule(db.Model):
#     __tablename__ = 'schedule'
#     id = db.Column(db.Integer, primary_key=True)
#     schedule_planes_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=False)
#     schedule_plan_details = db.relationship('Planes')
#     dia_1 = db.Column(db.String(100), nullable=True)
#     dia_2 = db.Column(db.String(100), nullable=True)
#     dia_3 = db.Column(db.String(100), nullable=True)
#     dia_4 = db.Column(db.String(100), nullable=True)
#     dia_5 = db.Column(db.String(100), nullable=True)
#     dia_6 = db.Column(db.String(100), nullable=True)
#     dia_7 = db.Column(db.String(100), nullable=True)

#     def serialize(self):
#         return{
#             'id': self.id,
#             'plan_id': self.schedule_planes_id,
#             'client_id':self.plan_detail.client_id,
#             'nutritionist_id':self.plan_detail.nutritionist_id,
#             'trainer_id':self.schedule_plan_details.trainer_id,
#             'dia 1': self.dia_1,
#             'dia 2': self.dia_2,
#             'dia 3': self.dia_3,
#             'dia 4': self.dia_4,
#             'dia 5': self.dia_5,
#             'dia 6': self.dia_6,
#             'dia 7': self.dia_7
#         }
    