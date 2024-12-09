from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calories.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    points = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)

class CalorieLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def home():
    users = User.query.all()
    return render_template('home.html', users=users)

@app.route('/log', methods=['POST'])
def log_calories():
    user_id = request.form.get('user_id')
    calories = int(request.form.get('calories'))

    # Log the calories
    log = CalorieLog(user_id=user_id, calories=calories)
    db.session.add(log)

    # Update user points and streak
    user = User.query.get(user_id)
    user.points += 10  # Add 10 points per log
    user.streak += 1
    db.session.commit()

    return redirect(url_for('progress', user_id=user_id))

@app.route('/progress/<int:user_id>')
def progress(user_id):
    user = User.query.get(user_id)
    logs = CalorieLog.query.filter_by(user_id=user_id).all()
    return render_template('progress.html', user=user, logs=logs)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
