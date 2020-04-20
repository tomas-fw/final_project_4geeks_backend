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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id',ondelete='SET NULL'), nullable=False )
    planes_id = db.relationship('Planes', backref ='client_detail', lazy = True )
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    # objective = db.relationship('Objective', backref ='client_detail', lazy=True)
    # age = db.Column(db.Integer, nullable=True)
    photo = db.Column(db.String(100), nullable=False, default='./static/images/avatar/default_profile.png')
    role = db.relationship('Role')
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    active = db.Column(db.Boolean, nullable = False, default = True)

##### formulario nutricionista ingreso cliente ######
##### formulario personal trainer ingreso cliente ######
    def serialize(self):
        return {
            "client_id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "email": self.email,
            "photo": self.photo,
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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id',ondelete='SET NULL'), nullable=False)
    planes_id = db.relationship('Planes', backref = 'nutritionist_detail', lazy=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False, default='./static/images/avatar/default_profile.png')
    specialties = db.Column(db.String(100), nullable=True)
    education = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    lastWork = db.Column(db.String(100), nullable=True)
    lastWorkyears = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    role = db.relationship(Role)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    active = db.Column(db.Boolean, nullable = False, default = False)


    def serialize(self):
        return {
            "nutritionist_id": self.id,
            "active":self.active,
            "email": self.email,
            "name": self.name,
            "lastname": self.lastname,
            "photo": self.photo,
            "specialties": self.specialties,
            "education": self.education,
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
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id',ondelete='SET NULL'), nullable=False)
    planes_id = db.relationship('Planes', backref = 'trainer_detail', lazy=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(100), nullable=False, default='./static/images/avatar/default_profile.png')
    specialties = db.Column(db.String(100), nullable=True)
    education = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    lastWork = db.Column(db.String(100), nullable=True)
    lastWorkyears = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    role = db.relationship(Role)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow )
    active = db.Column(db.Boolean, nullable = False, default = False)


    def serialize(self):
        return {
            "trainer_id": self.id,
            "active":self.active,
            "email": self.email,
            "name": self.name,
            "lastname": self.lastname,
            "photo": self.photo,
            "specialties": self.specialties,
            "education": self.education,
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
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='SET NULL'), nullable=False)
    nutritionist_id = db.Column(db.Integer, db.ForeignKey('nutritionist.id',ondelete='SET NULL'), nullable=False)
    trainer_id = db.Column(db.Integer, db.ForeignKey('trainer.id',ondelete='SET NULL'), nullable=False)
    client = db.relationship('Client')
    nutritionist = db.relationship('Nutritionist')
    trainer = db.relationship('Trainer')
    objective = db.Column(db.String(250), nullable=False)
    comment = db.Column(db.Text, nullable = True)
    date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    active = db.Column(db.Boolean, nullable = False, default = True)

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
            "active": self.active

        }

# class Objective(db.Model):
#     __tablename__= 'objective'
#     id = db.Column(db.Integer, primary_key=True)
#     objective = db.Column(db.Text, nullable=False)
#     observation = db.Column(db.Text, nullable = True)
#     age = db.Column(db.Integer, nullable=True)
#     date_created = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
#     client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable = False)
