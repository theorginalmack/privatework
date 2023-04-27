from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import re
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/db_name'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    business_owner = db.Column(db.String(80), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    requestor_name = db.Column(db.String(80), nullable=False)
    requestor_email = db.Column(db.String(120), nullable=False)
    requestor_phone = db.Column(db.String(20), nullable=False)
    manager_name = db.Column(db.String(80), nullable=False)
    manager_email = db.Column(db.String(120), nullable=False)
    manager_phone = db.Column(db.String(20), nullable=False)
    director_name = db.Column(db.String(80), nullable=False)
    director_email = db.Column(db.String(120), nullable=False)
    director_phone = db.Column(db.String(20), nullable=False)


def validate_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_name(name):
    return len(name) > 0


def validate_email(email):
    email_regex = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    return bool(email_regex.match(email))


def validate_phone(phone):
    phone_regex = re.compile(r'^\+?[\d\s\(\)-]{7,}$')
    return bool(phone_regex.match(phone))


def validate_form_data(request):
    errors = []

    # Environment selection
    if not request.form.get("FCSO") and not request.form.get("NSM"):
        errors.append("Please select at least one environment.")

    # MAC Environment selection
    if not request.form.get("MAC_FCSO") and not request.form.get("MAC_NSM"):
        errors.append("Please select at least one MAC environment.")

    # Discovery date
    if not request.form.get("date"):
        errors.append("Please enter the discovery date.")

    # CVE severity level
    severity_levels = ["critical", "high", "moderate", "low", "non_security"]
    if not any(request.form.get(level) for level in severity_levels):
        errors.append("Please select at least one CVE severity level.")

    # FQDN and IP address fields
    fqdns = request.form.getlist("fqdn[]")
    ip_addresses = request.form.getlist("ip_address[]")

    if not all(fqdns) or not all(ip_addresses):
        errors.append("Please fill out all FQDN and IP address fields.")

    # Request detail
    if not request.form.get("risks"):
        errors.append("Please provide request details.")

    return errors


def validate_rca_category(reasons):
    return 1 <= len(reasons) <= 5


def validate_business_justification(business_justification):
    return len(business_justification) > 0


def validate_risks(risks):
    return len(risks) > 0


def validate_mitigating_controls(mitigating_controls):
    return len(mitigating_controls) > 0


def validate_resources_required(resources_required):
    return len(resources_required) > 0


def validate_milestones(milestone_tasks, planned_completions, poc_completings):
    if len(milestone_tasks) == len(planned_completions) == len(poc_completings):
        for milestone_task, planned_completion, poc_completing in zip(milestone_tasks, planned_completions, poc_completings):
            if not (milestone_task and validate_date(planned_completion) and poc_completing):
                return False
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Previous form fields
        date = request.form['date']
        business_owner = request.form['name']
        department = request.form['department']
        requestor_name = request.form['requestor_name']
        requestor_email = request.form['email']
        requestor_phone = request.form['phone']
        manager_name = request.form['manager_name']
        manager_email = request.form['manager_email']
        manager_phone = request.form['manager_phone']
        director_name = request.form['director_name']
        director_email = request.form['director_email']
        director_phone = request.form['director_phone']

        # New form fields
        reasons = request.form.getlist('reasons[]')
        business_justification = request.form['businessJustification']
        risks = request.form['risks']
        mitigating_controls = request.form['mitigatingControls']
        compliance_date = request.form['complianceDate']
        resources_required = request.form['resourcesRequired']
        milestone_tasks = request.form.getlist('milestone_task[]')
        planned_completions = request.form.getlist('planned_completion[]')
        poc_completings = request.form.getlist('poc_completing[]')

        if (
            validate_date(date) and
            validate_name(business_owner) and
            validate_name(department) and
            validate_name(requestor_name) and
            validate_email(requestor_email) and
            validate_phone(requestor_phone) and
            validate_name(manager_name) and
            validate_email(manager_email) and
            validate_phone(manager_phone) and
            validate_name(director_name) and
            validate_email(director_email) and
            validate_phone(director_phone) and
            validate_rca_category(reasons) and
            validate_business_justification(business_justification) and
            validate_risks(risks) and
            validate_mitigating_controls(mitigating_controls) and
            validate_date(compliance_date) and
            validate_resources_required(resources_required) and
            validate_milestones(
                milestone_tasks, planned_completions, poc_completings)
        ):
            submission = Submission(
                date=date,
                business_owner=business_owner,
                department=department,
                requestor_name=requestor_name,
                requestor_email=requestor_email,
                requestor_phone=requestor_phone,
                manager_name=manager_name,
                manager_email=manager_email,
                manager_phone=manager_phone,
                director_name=director_name,
                director_email=director_email,
                director_phone=director_phone)

            db.session.add(submission)
            db.session.commit()

            flash('Form submitted successfully!', 'success')
            return redirect(url_for('index'))

        else:
            errors = validate_form_data(request)
            for error in errors:
                flash(error, 'danger')

    else:
        flash('Please enter valid information in all fields.', 'danger')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
