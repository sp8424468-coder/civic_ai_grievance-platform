from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    credit_points = db.Column(db.Integer, default=0)


class Complaint(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    department = db.Column(db.String(100))
    priority = db.Column(db.String(50))
    latitude = db.Column(db.String(50))
    longitude = db.Column(db.String(50))
    photo = db.Column(db.String(200))
    status = db.Column(db.String(50))


class Department(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    admin_email = db.Column(db.String(100))
    admin_password = db.Column(db.String(100))


class Employee(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    department = db.Column(db.String(100))
    zone = db.Column(db.String(100))
    status = db.Column(db.String(50))

