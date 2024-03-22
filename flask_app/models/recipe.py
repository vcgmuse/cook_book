from flask import request, redirect, session, flash
from flask_app import app, bcrypt
from flask_app.config.mysqlconnection import connectToMySQL
import re


class Recipe:
    DB = "recipes_to_users"

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.under = data['under']
        self.description = data['description']
        self.instruction = data['instruction']
        self.date_made = data['date_made']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user_id = data['user_id']
        # This will be a user object instead of just a user id
        self.user = None
        
    @classmethod
    def save(cls, data):
        query = '''
        insert into recipes(name, under, description, instruction, date_made, created_at, updated_at, user_id)
        values (%(name)s, %(under)s, %(description)s, %(instruction)s, %(date_made)s, now(), now(), %(user_id)s);
        '''
        return connectToMySQL(cls.DB).query_db(query, data)
    @classmethod
    def delete(cls, data):
        recipe = Recipe.get_by_id(data['id'])
        if recipe.user.id == session['user_id']:
            query = '''
            delete from recipes where recipes.id = %(id)s;
            '''
            return connectToMySQL(cls.DB).query_db(query, data)
        else:
            return redirect('/logout')
    @classmethod
    def update(cls, data):
        if session['user_id'] == data['user_id']:
            query = '''
            update recipes
            set 
            name = %(name)s, 
            under = %(under)s, 
            description = %(description)s, 
            instruction = %(instruction)s, 
            date_made = %(date_made)s,
            updated_at = now();
            '''
        else:
            return False
        return connectToMySQL(cls.DB).query_db(query, data)
    
    @classmethod
    def get_all(cls):
        from flask_app.models.user import User
        query = '''
        select * 
        from recipes
        join users on users.id = recipes.user_id;
        '''
        results = connectToMySQL(cls.DB).query_db(query)
        recipes_by_users = []
        for row in results:
            recipe = cls(row)
            user = User({
                **row,
                "id": row['users.id'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            })
            recipe.user = user
            recipes_by_users.append(recipe)
        return recipes_by_users            
        
    @classmethod
    def get_by_user_id(cls, user_id):
        query = '''
        select * 
        from recipes
        join users on users.id = recipes.user_id
        where users.id = %(user_id)s;
        '''
        data = {"user_id":user_id}
        results = connectToMySQL(cls.DB).query_db(query, data)
        if not results:
            return False
        else:
            user_data = {
                **results, 
                "user_id": results['users.id'],
                "created_at": results['users.created_at'],
                "updated_at": results['users.updated_at']
                }
            recipe = cls(results[0])
            recipe.user = cls(user_data)
            return recipe
        
    @classmethod
    def get_by_id(cls, recipe_id):
        query = '''
        select *
        from recipes
        join users on users.id = recipes.user_id
        where recipes.id = %(id)s;
        '''
        data = {'id':recipe_id}
        results = connectToMySQL(cls.DB).query_db(query, data)[0]
        if not results:
            return False
        else:
            from flask_app.models.user import User
            user_data = {
                "id": results['users.id'],
                "first_name": results['first_name'],
                "last_name": results['last_name'],
                "email": results['email'],
                "password": "",
                "created_at": results['users.created_at'],
                "updated_at": results['users.updated_at']
                }
            recipe = cls(results)
            recipe.user = User(user_data)
            return recipe
        
    # Needs to validate recipe
    @staticmethod
    def validate_recipe_form(data):
        is_valid = True
        if "under" not in data:
            flash("Yes or No must be selected: ", "error")
            is_valid = False
        for field, value in data.items():
            if not field in session:
                session[field] = value
            else:
                session[field] = value          
            
            if not value:
                flash(f"{field} must not be empty", "error")
                is_valid = False
            
        return is_valid