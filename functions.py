from flask import jsonify
from flask_mail import Mail, Message
mail = Mail()
def sendMail(subject, to_email, html):
    msg = Message(subject, sender=['yana', 'fineukraine94@gmail.com'], recipients=[to_email])
    msg.html = html
    mail.send(msg)
    return jsonify({"msg": "Email send successfully"}), 200

def allowed_files(filename,ALLOWED_EXTENSIONS):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS







# from flask import Blueprint, request, jsonify, Flask, render_template
# from models import db, User
# from flask_mail import Mail, Message
# from flask_bcrypt import Bcrypt
# from libs.functions import sendMail
# from flask_jwt_extended import (
#     create_access_token,
# )
# from itsdangerous import URLSafeSerializer
# from itsdangerous import URLSafeTimedSerializer
# bcrypt = Bcrypt()
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'my_precious'
# app.config['SECURITY_PASSWORD_SALT'] = 'my_precious_two'
# route_forgetpassusers = Blueprint('route_forgetpassusers', __name__)


# def generate_confirmation_token(email):
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])
# def confirm_token(token, expiration=86400):
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     try:
#         email = serializer.loads(
#             token,
#             salt=app.config['SECURITY_PASSWORD_SALT'],
#             max_age=expiration
#         )
#     except:
#         return False
#     return email
# @route_forgetpassusers.route('/change-password', methods=['POST'])
# def change_password():
#         email = request.json.get('email', None)
#         if not email or email == '':
#             return None
#         user = User()
#         user.email = email
#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return jsonify({"msg": "This email is not registered"}), 404
#         token = generate_confirmation_token(user.email)
#         confirm_url = 'http://localhost:3000/confirmation/' + token
#         html = render_template('email_confirmation.html', confirm_url=confirm_url)
#         subject = "Por favor, Confirmar su email."
#         sendMail("Por favor, Confirmar su email.", user.email, html)
#         return jsonify({"success": "Email send successfully"}), 200
        
# @route_forgetpassusers.route('/change-password-confirm/<token>', methods=['POST'])
# def change_password_confirm(token):
#     password_hash = request.json.get('password_hash', None)
#     if not password_hash or password_hash == '':
#         return jsonify({"msg": "You need to write your password"}), 422
#     try:
#         email = confirm_token(token)
#     except:
#         return jsonify({"msg": "El enlace de confirmacion es invalido o ha expirado."}), 401
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         return jsonify({"msg": "This email is not registered"}), 404
#     user.password_hash = bcrypt.generate_password_hash(password_hash)
#     db.session.commit()
#     return jsonify({"msg": "password changed"}), 200