from flask import request, redirect, session, flash
from flask_app import app, bcrypt
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.recipe import Recipe
import re

class User:
    DB = "recipes_to_users"
    
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    @classmethod
    def save(cls, data):
        query = '''
        insert into users(first_name, last_name, email, password, created_at, updated_at)
        values (%(first_name)s, %(last_name)s, %(email)s, %(password)s, now(), now());
        '''
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_by_email(cls, email):
        
        query = '''
        select * 
        from users
        where users.email = %(email)s;
        '''
        data = {"email":email}
        results = connectToMySQL(cls.DB).query_db(query, data)
        if not results:
            return False
        else:
            return cls(results[0])
    
    @classmethod
    def get_by_id(cls, id):
        
        query = '''
        select * 
        from users
        where users.id = %(id)s;
        '''
        data = {"id": id}
        results = connectToMySQL(cls.DB).query_db(query, data)[0]
        if not results:
            return False
        else:
            user_data = {
                **results,
                "password": ""
                }
            return cls(user_data)
    
    @staticmethod
    def validate_registration(data):
        is_valid = True
        for field, value in data.items():
            if not field in session and field != "password":
                session[field] = value
            elif field != "password":
                session[field] = value                
            if field == "first_name" or field == "last_name":
                if not value.isalpha():
                    flash(f"{field} must only be letters", 'error')
                    is_valid = False
                if len(value) < 2:
                    flash(f"{field} minimal 2 characters ")
                    is_valid =False
            if len(value) < 1:
                flash(f"{field} must not be empty")
                is_valid = False
            if field =="email":
                if User.get_by_email(data['email']):
                    flash("Email Taken: ", "error")
                    is_valid = False
            if field == "password":
                PASSWORD_REGEX = re.compile(r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[a-zA-Z\d@$!%*?&]{8,}$')
                if PASSWORD_REGEX.match(value) is None:
                    flash("Ivalid Password Format: ", "error")
                    is_valid = False
        if request.form['password'] != request.form['confirm_password']:
            flash(f"Passwords do not match!", 'error')
            is_valid = False
        return is_valid