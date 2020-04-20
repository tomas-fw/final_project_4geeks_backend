@app.route('/register/profesional/trainer', methods=['POST']) ##REGISTER PERSONAL TRAINERS
def trainer_register():
    # if not request.is_json:
    #     return jsonify({"msg":"Missing JSON request"}),400
    
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
    

    trainer = Profesional.query.filter_by(email =email).first()
    if trainer:
        return jsonify({"msg":'email already register'}),400
    
    file = request.files['photo']
    if file and file.filename!= '' and allowed_files(file.filename, ALLOWED_EXTENSIONS_IMAGES):
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar'), filename))
    else:
        return jsonify({"msg":"file is not allowed"}), 400

    trainer = Profesional()
    trainer.email = email
    trainer.password = bcrypt.generate_password_hash(password)
    trainer.name = name
    trainer.lastname = lastname
    trainer.role_id = 3
    

    db.session.add(trainer)
    db.session.commit()

    access_token = create_access_token(identity = trainer.email)
    data={
        'access_token': access_token,
        'trainer': trainer.serialize()
    }
    return jsonify(data), 200
    

@app.route('/register/profesional/nutritionist', methods=['POST']) ## REGISTER NUTRITIONIST
def nutri_register():
    # if not request.is_json:
    #     return jsonify({"msg":"Missing JSON request"}),400
    
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
    

    nutri = Profesional.query.filter_by(email ='email').first()
    if nutri:
        return jsonify({"msg":'email already register'}),400
    
    file = request.files['photo']
    if file and file.filename != '' and allowed_files(file.filename, ALLOWED_EXTENSIONS_IMAGES):
        filename = secure_filename(file.filename)
        file.save(os.path.join(os.path.join(app.config['UPLOAD_FOLDER'], 'images/avatar'), filename))
    else:
        return jsonify({'msg':'file not allowed'}), 400


    nutri = Profesional()
    nutri.email = email
    nutri.password = bcrypt.generate_password_hash(password)
    nutri.name = name
    nutri.lastname = lastname
    nutri.role_id = 2

    db.session.add(nutri)
    db.session.commit()

    access_token = create_access_token(identity=nutri.email)
    data={
        'access_token': access_token,
        'nutri': nutri.serialize()
    }
    return jsonify(data), 200
    
for client in clients:  ###this for loop returns info about the clients but not their plans
            obj ={
                "id": client.id,
                "email": client.email,
                "name":client.name,
                "last_name": client.lastname,
                "is_active":client.active,
                "planes":len(client.planes_id)
            }
            all_clients.append(obj)



### ASK LUIS HOW TO USE MAP TO LOOP LIST INSIDE LIST ####
# _client = Client.query.filter_by(id=client_id).all()
# client = list(map(lambda client: client.serialize(), _client))
# return jsonify(client), 200               