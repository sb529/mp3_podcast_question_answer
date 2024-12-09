from app import app, db
from models import User, CalorieLog
from flask import request, redirect, url_for

@app.route('/log', methods=['POST'])
def log_calories():
    user_id = request.form.get('user_id')
    calories = request.form.get('calories')
    log = CalorieLog(user_id=user_id, calories=calories)
    db.session.add(log)
    db.session.commit()
    # Update points and streak here based on business logic
    return redirect(url_for('progress'))
