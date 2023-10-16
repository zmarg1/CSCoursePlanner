"""
Author: Amir Hawkins-Stewart

Description: Currently class definitions for the planUMBC tables in supabase

TODO: Finish the classes, app.routes to send and receive from site 
"""

from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "planUMBCkey" #Secret key needed for sessions to get the encrypted data
"""TODO: Uncomment to edit database
app.config['SQLALCHEMY_DATABASE_URI'] = postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres
"""
app.permanent_session_lifetime = timedelta(minutes = 5) #How long the session data will be saved for

db = SQLAlchemy(app)

"""
The User will have an id, name, 'user'
ForeignKeys:
 The plan the user has made or has
 The users current degree

 TODO: Need to edit to sen to auth and not public
"""
class user(db.Model):
    _id = db.Column("user_id", db.Integer, primary_key=True)
    usr_name = db.Column(db.String(100))

    plan_id = db.Column('student_plan_id', db.Integer, db.ForeignKey('plan.plan_id'))
    plan = db.relationship('plan', primaryjoin='user.plan_id == plan._id', backref=db.backref('plan', lazy='dynamic'))

    deg_id = db.Column('student_degree', db.String(100), db.ForeignKey('degree.deg_id'))
    degree = db.relationship('degree', primaryjoin='user.deg_id == degree.deg_id', backref=db.backref('degree', lazy='dynamic'))

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

"""
plan has an id, 'number', name, and will store the courses for that plan
"""
class plan(db.Model):
    _id = db.Column("plan_id", db.Integer, primary_key=True)
    plan_num = db.Column(db.Integer)
    plan_name = db.Column(db.String(100))
    created_at = db.Column(db.Time)#might work

    usr_id = db.Column('user_id', db.Integer, db.ForeignKey('user._id'))
    user = db.relationship('user', primaryjoin='plan.usr_id == user._id', backref=db.backref('user', lazy='dynamic'))

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
class degree(db.Model):
    _id = db.Column(db.Integer, primarykey=True)
    deg_name = db.Column(db.String(100))
    deg_type = db.Column(db.String(100))

    deg_req = db.Column('degree_requirement', db.String(100), db.ForeignKey('requirement.type'))
    requirment = db.relationship('requirement', primaryjoin='degree.deg_req == requirement.type', backref=db.backref('degree', lazy='dynamic'))

    deg_sub_req = db.Column('degree_requirement_subtype', db.String(100), db.ForeignKey('requirement.subtype'))
    requirment = db.relationship('requirement', primaryjoin='degree.deg_sub_req == requirement.subtype', backref=db.backref('degree', lazy='dynamic'))

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
class requirement(db.Model):
    _id = db.Column('requirement_id', db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    subtype = db.Column(db.String(100))

    degree_id = db.Column(db.Integer, db.ForeignKey('degree._id'))
    degree = db.relationship('degree', primaryjoin='requirement.degree_id == degree._id', backref=db.backref('degree', lazy='dynamic'))

    def __init__(self, type, subtype):
        self.type = type
        self.subtype = subtype

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class prereq(db.Model):
    _id = db.Column('prereq_id', db.Integer, primary_key=True)
    prereq_courses = db.Column()

    crs_id = db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'))
    course = db.relatioinship('course', primaryjoin='prereq.crs_id == course._id', backref=db.backref('course', lazy='dynamic'))

"""
A course with its id, title, number, credits, and its prereq
ForeignKeys: 
subject it belongs to using the subjects code
when it is offered using the term
"""
class course(db.Model):
    _id = db.Column("course_id", db.Integer, primary_key=True)
    crs_title = db.Column('course_title',db.String(100))
    crs_num = db.Column('course_num',db.Integer)
    credits = db.Column(db.Integer)
    prereq = None

    #TODO: Check to make sure its connecting correctly
    subj_id = db.Column('course_subject_id', db.Integer, db.ForeignKey('subject.subject_id'))
    subject = db.relationship('subject', primaryjoin='course.subj_id == subject.sub_id', backref=db.backref('subject', lazy='dynamic'))

    sem_offered = db.Column('term_offered', db.String(100), db.ForeignKey('semester.term'))
    semester = db.relationship('semester', primaryjoin='course.sem_offered == semester.term', backref=db.backref('semester', lazy='dynamic'))

    crs_required = db.Table('courses_required',
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirement.requirement_id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')))

    crs_offered = db.Table('course_offered',
    db.Column('offered_id', db.Integer, primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('semester_id', db.Integer, db.ForeignKey('semester.semester_id')),
    db.Column('is_offered', db.Bool) )

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
Subject of the course containing the subject id, code, and name
"""
class subject(db.Model):
    sub_id = db.Column('subject_id', db.Integer, primary_key=True)
    sub_code = db.Column("subject_code", db.Integer)
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
class semester(db.Model):
    _id = db.Column('semester_id', primary_key=True)
    term = db.Column(db.String(100))
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

class taken(db.Model):
    _id = db.Column('taken_id', db.Integer, primary_key=True)

    plan_id = db.Column(db.String(100), db.ForeignKey('plan._id'))
    plan = db.relationship('plan', primaryjoin='taken.plan_id == plan._id', backref=db.backref('plan', lazy='dynamic'))

    course_id = db.Column(db.String(100), db.ForeignKey('course._id'))
    course = db.relationship('course', primaryjoin='taken.course_id == course._id', backref=db.backref('course', lazy='dynamic'))

    req_id = db.Column('requirement_id', db.String(100), db.ForeignKey('requirement._id'))
    requirement = db.relationship('requirement', primaryjoin='taken.req_id == requirement._id', backref=db.backref('requirement', lazy='dynamic'))

    sem_id = db.Column('semester_id', db.String(100), db.ForeignKey('semester._id'))
    semester = db.relationship('semester', primaryjoin='taken.sem_id == semester._id', backref=db.backref('semester', lazy='dynamic'))

    grade = db.Column(db.Integer)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)