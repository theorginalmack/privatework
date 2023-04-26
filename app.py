from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)

# Function for Date of submission


def validate_date(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Validate the input for business owner


def validate_name(name):
    if not name:
        return False
    if not name.isalpha():
        return False
    if len(name) > 50:
        return False
    return True

# Function for email


def validate_email(email):
    if len(email) > 7:
        if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return True
    return False

# Function for IP


def validate_ip(ip):
    parts = ip.split('.')
    if len(parts) == 4 and all(x.isdigit() and 0 <= int(x) <= 255 for x in parts):
        return True
    return False

# Function for phone


def validate_phone(phone):
    if len(phone) == 10 and phone.isdigit():
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        if validate_name(name) and validate_email(email):
            submission = Submission(name=name, email=email)
            db.session.add(submission)
            db.session.commit()

            flash('Form submitted successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Please enter a valid name and email.', 'danger')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
