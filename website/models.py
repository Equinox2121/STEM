from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime

# All users get logged to this database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    graduation_year = db.Column(db.String(4))
    student_phone = db.Column(db.String(10))
    parent_email = db.Column(db.String(100))
    parent_phone = db.Column(db.String(10))
    student_email = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(4096)) # Hashed password
    # Link users to their hidden account information
    user_data = db.relationship('Misc')
    # Link users to their table information
    user_table = db.relationship('Table')
    # Link users to their table information
    report_form = db.relationship('Report')

# Hidden information for each user is stored here
class Misc(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    account_creation_date = db.Column(db.String)
    password_placeholder = db.Column(db.String)
    most_recent_login = db.Column(db.String)
    account_login_count = db.Column(db.Integer)
    program_choice = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Associate many notes with one specific user

# Information in the table (1 user to many) - Service Log
class Table(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    service_date = db.Column(db.String(32))
    organization = db.Column(db.String(256))
    brief_description = db.Column(db.String(512))
    hours_earned = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Associate many notes with one specific user
    # Link users to their report form information information
    report_form = db.relationship('Report')

# Information in the Report Form
class Report(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    contact_person = db.Column(db.String(256))
    contact_person_info = db.Column(db.String(512))
    reflection1 = db.Column(db.String(4096))
    reflection2 = db.Column(db.String(4096))
    reflection3 = db.Column(db.String(4096))
    table_id = db.Column(db.Integer, db.ForeignKey('table.id')) # Associate the report form with one specific table num
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Associate many notes with one specific user