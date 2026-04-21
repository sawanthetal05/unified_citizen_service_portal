from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Grievance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="Pending")

class LegalCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    case_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="Under Review")