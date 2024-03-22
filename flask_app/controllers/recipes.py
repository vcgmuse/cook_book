from flask_app import app, bcrypt
from flask import render_template, redirect, session, request, flash, url_for
from flask_app.models.user import User
from flask_app.models.recipe import Recipe

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recipes')
def recipes():
    if "user_id" not in session:
        return redirect('/')
    user = User.get_by_id(session['user_id'])
    recipes = Recipe.get_all()
    
    if not user:
        flash("Error: User not found or logged out. Please log in again.", "error")
        return redirect('/logout')
    return render_template('recipes.html', user = user, recipes = recipes)

@app.route('/recipes/new')
def recipes_new():
    if "user_id" not in session:
        return redirect('/')
    # user = User.get_by_id(session['user_id'])
    
    return render_template('recipes_new.html')

@app.route('/recipes/new', methods=["POST"])
def recipes_create():
    if "user_id" not in session:
        return redirect('/')
    if not Recipe.validate_recipe_form(request.form):
        return redirect('/recipes/new')
    id = Recipe.save({
        **request.form,
        'user_id':session['user_id']
    })
    return redirect('/recipes')

@app.route('/recipes/edit/<int:recipe_id>')
def recipes_edit(recipe_id):
    if "user_id" not in session:
        return redirect('/')
    recipe = Recipe.get_by_id(recipe_id)
    return render_template('recipes_edit.html', recipe = recipe)

@app.route('/recipes/update/<int:recipe_id>', methods = ['POST'])
def recipes_update(recipe_id):
    if "user_id" not in session:
        return redirect('/')
    if not Recipe.validate_recipe_form(request.form):
        return redirect(f'/recipes/edit/{recipe_id}')
    Recipe.update({
        **request.form,
        'user_id':session['user_id']
        })
    return redirect('/recipes')

@app.route('/recipes/delete/<int:recipe_id>')
def recipes_delete(recipe_id):
    if "user_id" not in session:
        return redirect('/')
    Recipe.delete({"id":recipe_id})
    return redirect('/recipes')

@app.route('/recipes/<int:recipe_id>')
def recipes_view(recipe_id):
    if "user_id" not in session:
        return redirect('/')
    recipe = Recipe.get_by_id(recipe_id)
    return render_template('recipes_view.html', recipe = recipe)
    

