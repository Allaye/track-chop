from datetime import datetime
from flask import Blueprint, render_template, request, url_for, redirect
from foodtracker.extensions import db
from foodtracker.models import Food, Log
main = Blueprint('main', __name__)


@main.route('/')
def index():
    logs = Log.query.order_by(Log.date.desc()).all()

    log_dates = []

    for log in logs:
        proteins = 0
        carbs = 0
        fats = 0
        calories = 0

        for food in log.foods:
            proteins += food.proteins
            carbs += food.carbs
            fats += food.carbs
            calories += food.calories
        log_dates.append({
            'log_date': log,
            'proteins': proteins,
            'carbs': carbs,
            'fats': fats,
            'calories': calories
        })

    return render_template('index.html', log_dates=log_dates)


@main.route('/create_log', methods=['POST'])
def create_log():
    date = request.form['date']
    log = Log(date=datetime.strptime(date, '%Y-%m-%d'))
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('main.view', log_id=log.id))


@main.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST' and request.form['food-id']:
        food_id = request.form['food-id']
        food = Food.query.get(food_id)
        food.name = request.form['food-name']
        food.proteins = request.form['protein']
        food.fats = request.form['fat']
        food.carbs = request.form['carbohydrates']
        db.session.commit()
    elif request.method == 'POST':
        food = request.form['food-name']
        protein = request.form['protein']
        fat = request.form['fat']
        carbo = request.form['carbohydrates']
        new_food = Food(name=food, proteins=protein, fats=fat, carbs=carbo)
        db.session.add(new_food)
        db.session.commit()
        return redirect(url_for('main.add'))
    foods = Food.query.all()
    return render_template('add.html', foods=foods, food=None)


@main.route('/delete_food/<int:id>')
def delete_food(id):
    food = Food.query.get(id)
    db.session.delete(food)
    db.session.commit()
    return redirect(url_for('main.add'))


@main.route('/edit_food/<int:id>', methods=['POST', 'GET'])
def edit_food(id):
    food = Food.query.get(id)
    foods = Food.query.all()
    return render_template('add.html', food=food, foods=foods)


@main.route('/view/<int:log_id>')
def view(log_id):
    log = Log.query.get_or_404(log_id)
    foods = Food.query.all()
    totals = {
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'calories': 0
    }
    for food in log.foods:
        totals['protein'] += food.proteins
        totals['carbs'] += food.carbs
        totals['fat'] += food.fats
        totals['calories'] += food.calories
    return render_template('view.html', foods=foods, log=log, totals=totals)


@main.route('/add_food_to_log/<int:log_id>', methods=['POST'])
def add_food_to_log(log_id):
    log = Log.query.get_or_404(log_id)
    selected_food = request.form.get('food-select')
    food = Food.query.get(int(selected_food))
    log.foods.append(food)
    db.session.commit()
    return redirect(url_for('main.view', log_id=log_id))


@main.route('/remove_food_from_log/<int:log_id>/<int:food_id>')
def remove_food_from_log(log_id, food_id):
    log = Log.query.get_or_404(log_id)
    food = Food.query.get_or_404(food_id)

    log.foods.remove(food)
    db.session.commit()

    return redirect(url_for('main.view', log_id=log_id, food_id=food_id))