from flask_app import app, bcrypt
from flask import render_template, redirect, session, request, flash, url_for
from flask_app.models.user import User
from flask_app.models.recipe import Recipe


    
@app.route('/login', methods=['POST'])
def login():
    user = User.get_by_email(request.form['email'])
    if not user:
        flash("Invalid Email/Password", "login_serror")
        return redirect("/")
    if not bcrypt.check_password_hash(user.password, request.form['password']):
        flash("Invalid Email/Password", "login_error")
        return redirect('/')
    session['user_id'] = user.id
    session['first_name'] = user.first_name
    
    
    return redirect("/recipes")
@app.route('/user/logout')
def logout():
    session.clear()
    return redirect('/')
    
@app.route('/register/user', methods=['POST'])
def register():
    if User.validate_registration(request.form) is False:
        return redirect('/')           
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    if not "user_id" in session:
        session['user_id'] = User.save({
        **request.form,
        "password": pw_hash
        })
    return redirect("/recipes")
