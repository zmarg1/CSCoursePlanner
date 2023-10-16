"""
Author: Amir Hawkins-Stewart

Description: Currently class definitions for the planUMBC tables in supabase

TODO: Look at Supabase to see what exactly the tables look like, app.routes to send and receive from site, finish definitions
"""

from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "planUMBCkey" #Secret key needed for sessions to get the encrypted data
"""Uncomment to edit database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
"""
app.permanent_session_lifetime = timedelta(minutes = 5) #How long the session data will be saved for

db = SQLAlchemy(app)

"""
The User will have an id, name, 'user'
ForeignKeys:
 The plan the user has made or has
 The users current degree
"""
class User(db.Model):
    _id = db.Column("user_id", db.Integer, primary_key=True)
    usr_name = db.Column(db.String(100))
    user = db.Column(db.String(100))

    plan_id = db.Column('student_plan_id', db.Integer, db.ForeignKey('Plan.plan_id'))
    plan = db.relationship('Plan', primaryjoin='User.plan_id == Plan._id', backref=db.backref('Plan', lazy='dynamic'))

    deg_name = db.Column('student_degree', db.String(100), db.ForeignKey('Degree.deg_name'))
    degree = db.relationship('Degree', primaryjoin='User.deg_name == Degree.deg_name', backref=db.backref('Degree', lazy='dynamic'))

    def __init__(self, id, name, user):
        self._id = id
        self.usr_name = name
        self.user = user

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

#Plan has an id, 'number', name, and will store the courses for that plan
class Plan(db.Model):
    _id = db.Column("plan_id", db.Integer, primary_key=True)
    plan_num = db.Column(db.Integer)
    plan_name = db.Column(db.String(100))

    #TODO: Add courses table? or a list maybe? or make it have a user id and remove the primary key

    def __init__(self, id, num, name):
        self._id = id
        self.plan_num = num
        self.plan_name = name

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
 
"""
The users degree with name and type
ForeignKeys requirement type and subtype
"""
class Degree(db.Model):
    deg_name = db.Column(db.String(100), primarykey=True)
    deg_type = db.Column(db.String(100))

    deg_req = db.Column('degree_requirement', db.String(100), db.ForeignKey('Requirement.type'))
    requirment = db.relationship('Requirement', primaryjoin='Degree.deg_req == Requirement.type', backref=db.backref('Degree', lazy='dynamic'))

    deg_sub_req = db.Column('degree_requirement_subtype', db.String(100), db.ForeignKey('Requirement.subtype'))
    requirment = db.relationship('Requirement', primaryjoin='Degree.deg_sub_req == Requirement.subtype', backref=db.backref('Degree', lazy='dynamic'))

    def __init__(self, name, type):
        self.deg_name = name
        self.deg_type = type

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

"""
The requirements for the Degree containing its type and subtype
"""
class Requirement(db.Model):
    type = db.Column(db.String(100), primarykey=True)
    subtype = db.Column(db.String(100))

    def __init__(self, type, subtype):
        self.type = type
        self.subtype = subtype

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

"""
A course with its id, title, number, credits, and its prereq
ForeignKeys: 
subject it belongs to using the subjects code
when it is offered using the term
"""
class Course(db.Model):
    _id = db.Column("course_id", db.Integer, primary_key=True)
    crs_title = db.Column(db.String(100))
    crs_num = db.Column(db.Integer)
    credits = db.Column(db.Integer)
    prereq = None

    subj_code = db.Column('course_subject_code', db.Integer, db.ForeignKey('Subject.subject_code'))
    subject = db.relationship('Subject', primaryjoin='Course.subj_code == Subject.sub_code', backref=db.backref('Subject', lazy='dynamic'))

    sem_offered = db.Column('term_offered', db.String(100), db.ForeignKey('Semester.term'))
    semester = db.relationship('Semester', primaryjoin='Course.sem_offered == Semester.term', backref=db.backref('Semester', lazy='dynamic'))

    def __init__(self, id, title='NA', num=None, credits=None):
        self._id = id
        self.crs_title = title
        self.crs_num = num
        self.credits = credits

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def add_prereq(self, req):
        self.prereq = req
        db.session.commit()

"""
Subject of the course containing the subject code and name
"""
class Subject(db.Model):
    sub_code = db.Column("subject_code", db.Integer, primary_key=True)
    sub_name = db.Column("subject_name", db.String(100))

    def __init__(self, code, name):
        self.sub_code = code
        self.sub_name = name

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

"""
Semester class holds the term and year a course is offered if offered
"""
class Semester(db.Model):
    term = db.Column(db.String(100), primarykey=True)
    year = db.Column(db.Integer)

    def __init__(self, term, year):
        self.term = term
        self.year = year

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)