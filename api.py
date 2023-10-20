"""
Author: Amir Hawkins-Stewart

Description: Currently class definitions for the planUMBC tables in supabase

TODO: Finish the classes, app.routes to send and receive from site 
"""

from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

"""import os
from supabase import auth, create_client, Client
url: str = os.environ.get("https://qwydklzwvbrgvdomhxjb.supabase.co")
key: str = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTU0MDcxNjcsImV4cCI6MjAxMDk4MzE2N30.UNZJCMI1NxpSyFr8bBooIIGPqTbDe3N-_YV9ZHbE_1g")
supabase: Client = create_client(url, key)"""

app = Flask(__name__)
app.secret_key = "planUMBCkey" #Secret key needed for sessions to get the encrypted data
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
app.permanent_session_lifetime = timedelta(minutes = 5) #How long the session data will be saved for

db = SQLAlchemy(app)

"""
The User will have an id, name, 'user'
ForeignKeys:
 The plan the user has made or has
 The users current degree
"""

"""#TODO: Rework using supabase
class user():
    user_obj = supabase.auth.get_user()
    #user_id = supabase.table('user').select("id").execute()
    #user_email = supabase.table('user').select("email").execute()
    plan_id = None
    deg_id = None

    #Split into sign up and sign in
    def __init__(self, email, password):
        in_database = supabase.table('user').select('*').match({'email': email}).execute()
        if not in_database:
            user = supabase.auth.sign_up({
                "email": email,
                "password": password
                })
            self.user_obj = user
        else:
            data = supabase.auth.sign_in_with_password({"email": email, "password": password}) 
            self.user_email = email

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
"""

"""
plan has an id, 'number', name, and will store the courses for that plan
"""
class plan(db.Model):
    plan_id = db.Column( db.Integer, primary_key=True)
    plan_num = db.Column(db.Integer)
    plan_name = db.Column(db.String(100))
    created_at = db.Column(db.Time)#might work

    #usr_id = db.Column('user_id', db.Integer, db.ForeignKey('user.user_id'))
    #user = db.relationship('user', primaryjoin='plan.usr_id == user.user_id', backref=db.backref('user', lazy='dynamic'))

    def __init__(self, id, num, name):
        self.plan_id = id
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
    degree_id = db.Column(db.Integer, primary_key=True)
    deg_name = db.Column(db.String(100))
    deg_type = db.Column(db.String(100))

    deg_req = db.Column('degree_requirement', db.String(100), db.ForeignKey('requirement.type'))
    requirment = db.relationship('requirement', primaryjoin='degree.deg_req == requirement.type', backref=db.backref('requirement', lazy='dynamic'))

    deg_sub_req = db.Column('degree_requirement_subtype', db.String(100), db.ForeignKey('requirement.subtype'))
    requirment = db.relationship('requirement', primaryjoin='degree.deg_sub_req == requirement.subtype', backref=db.backref('requirement', lazy='dynamic'))

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
    requirement_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    subtype = db.Column(db.String(100))

    degree_id = db.Column(db.Integer, db.ForeignKey('degree.degree_id'))
    degree = db.relationship('degree', primaryjoin='requirement.degree_id == degree.degree_id', backref=db.backref('degree', lazy='dynamic'))

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
    prereq_id = db.Column(db.Integer, primary_key=True)
    prereq_courses = db.Column(db.ARRAY(db.Integer))

    crs_id = db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'))
    course = db.relationship('course', primaryjoin='prereq.crs_id == course.course_id', backref=db.backref('course', lazy='dynamic'))

"""
A course with its id, title, number, credits, and its prereq
ForeignKeys: 
subject it belongs to using the subjects code
when it is offered using the term
"""
class course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer)
    """TODO:After changed to Foreignkey in databse uncomment and delete ^subject_id
    subj_id = db.Column('course_subject_id', db.Integer, db.ForeignKey('subject.subject_id'))
    subject = db.relationship('subject', primaryjoin='course.subj_id == subject.subject_id', backref=db.backref('subject', lazy='dynamic'))
    """
    crs_title = db.Column('course_title',db.String(100))
    crs_num = db.Column('course_num',db.Integer)
    credits = db.Column(db.Integer)

    crs_required = db.Table('courses_required',
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirement.requirement_id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')))

    crs_offered = db.Table('course_offered',
    db.Column('offered_id', db.Integer, primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('semester_id', db.Integer, db.ForeignKey('semester.semester_id')),
    db.Column('is_offered', db.Boolean) )

    def __init__(self, id, title='NA', num=None, credits=None):
        self.course_id = id
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

    #For use with Postman
    def to_json(self):
        return{
            "course_id": self.course_id,
            "subject_id": self.subject_id,
            "course_title": self.crs_title,
            "course_num": self.crs_num,
            "credits": self.credits,
        }

"""
Subject of the course containing the subject id, code, and name
"""
class subject(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True)
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
    semester_id = db.Column(primary_key=True)
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
    taken_id = db.Column(db.Integer, primary_key=True)

    plan_id = db.Column(db.String(100), db.ForeignKey('plan.plan_id'))
    plan = db.relationship('plan', primaryjoin='taken.plan_id == plan.plan_id', backref=db.backref('plan', lazy='dynamic'))

    course_id = db.Column(db.String(100), db.ForeignKey('course.course_id'))
    course = db.relationship('course', primaryjoin='taken.course_id == course.course_id', backref=db.backref('course_taken', lazy='dynamic'))

    req_id = db.Column('requirement_id', db.String(100), db.ForeignKey('requirement.requirement_id'))
    requirement = db.relationship('requirement', primaryjoin='taken.req_id == requirement.requirement_id', backref=db.backref('requirement_taken', lazy='dynamic'))

    sem_id = db.Column('semester_id', db.String(100), db.ForeignKey('semester.semester_id'))
    semester = db.relationship('semester', primaryjoin='taken.sem_id == semester.semester_id', backref=db.backref('semester', lazy='dynamic'))

    grade = db.Column(db.Integer)

@app.route("/test-course", methods=["POST", "GET"])
def test_course():
    if request.method == "POST":
        c_id = request.form["c_id"]
        session["c_id"] = c_id
        c_title = request.form ["c_title"]
        session["c_tittle"] = c_title
        c_num = request.form["c_num"]
        session["c_num"] = c_num
        c_credits = request.form["c_credits"]
        """session["c_credits"] = c_credits
        subj_id = request.form["subj_id"]
        session["subj_id"] = subj_id
        sem_offered = request.form["sem_offered"]
        session["sem_offered"] = sem_offered
        crs_req = request.form["crs_req"]
        session["crs_req"] = crs_req
        crs_offered = request.form["crs_offered"]
        session["crs_offered"] = crs_offered"""

        new_crs = course(c_id,c_title, c_num, c_credits)
        return "Course made successfully"

@app.route("/view")
def view():
    #To test with Postman by returning the json file of the courses
    courses = course.query.all()
    courses_json = [course.to_json() for course in courses]
    return jsonify(courses_json) 
    """To view on UI to the designated template if needed
    return render_template("template.html", courses=Courses.query.all())
    """

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)