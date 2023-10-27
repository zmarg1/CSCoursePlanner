"""
Author: Amir Hawkins-Stewart

Description: Currently class definitions for the planUMBC tables in supabase

TODO: Finish the classes, app.routes to send and receive from site 
"""

from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import supabase #import supabase.py not supabase

url = "https://qwydklzwvbrgvdomhxjb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTU0MDcxNjcsImV4cCI6MjAxMDk4MzE2N30.UNZJCMI1NxpSyFr8bBooIIGPqTbDe3N-_YV9ZHbE_1g"
supabase = supabase.create_client(url, key)

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
#TODO: Make def for adding plan_id and deg_id to the class variables from user obj in database
class user():
    #Example of how to interact with items from user_obj
    #self.user_id = user_obj['id'] This can get the id, email
    #custom_data = user_obj.get('app_metadata', {}) This gets the plan_id, degree_id, campus_id
    user_obj = None
    user_id = None
    user_campus_id = None
    plan_id = None
    deg_id = None
    admin = False

    #TODO:Split into sign up and sign in functions
    #Just signs up a new user
    def __init__(self, email, password):
        try:
            in_auth = supabase.auth.get_user("email" == email)
            print(in_auth)
            if not in_auth:
                user = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options":{
                        "data":{
                            "plan_id": None,
                            "degree_id": None,
                            "campus_id": None
                        }
                    }
                    })
                self.user_obj = user
                self.user_id = user['id']
        except Exception as e:
            print(f"Authentication error: {e} for {email}")

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

"""
plan has an id, 'number', name, and will store the courses for that plan
"""
#TODO: Test to make sure Time, id, ForeignKey work add conditionals for inputs to check they are right
class plan(db.Model):
    plan_id = db.Column( db.Integer, primary_key=True)

    usr_id = db.Column('user_id', db.Integer, db.ForeignKey('auth.user.user_id'))
    user = db.relationship('user', primaryjoin='plan.usr_id == user.user_id', backref=db.backref('user', lazy='dynamic'))

    plan_num = db.Column(db.Integer)
    plan_name = db.Column(db.String(100))
    created_at = db.Column(db.Time)#need to test

    def __init__(self, id, num, name):
        self.plan_id = id
        self.plan_num = num
        self.plan_name = name
        self.created_at = datetime.now()

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

"""
The users degree with name of degree and type of degree
"""
class degree(db.Model):
    degree_id = db.Column(db.Integer, primary_key=True)
    deg_name = db.Column(db.String(100))
    deg_type = db.Column(db.String(100))

    def __init__(self, name, type):
        #TODO: uncomment if plan last_id works
        """
        last_id = degree.query.order_by(degree.degree_id.desc()).first() #Should get last id in list if any

        if last_id:
            self.degree_id = last_id[0] + 1
        else:
            self.degree_id = 1
        """
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

    degree_id = db.Column(db.Integer, db.ForeignKey('degree.degree_id'))
    degree = db.relationship('degree', primaryjoin='requirement.degree_id == degree.degree_id', backref=db.backref('degree', lazy='dynamic'))

    requirement_type = db.Column(db.String(100))
    requirement_subtype = db.Column(db.String(100))

    def __init__(self, type, subtype):
        #TODO: uncomment if plan last_id works
        """
        last_id = requirement.query.order_by(requirement.requirement_id.desc()).first() #Should get last id in list if any

        if last_id:
            self.requirement_id = last_id[0] + 1
        else:
            self.requirement_id = 1
        """
        self.type = type
        self.subtype = subtype

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

#TODO: test ARRAY works
class prereq(db.Model):
    prereq_id = db.Column(db.Integer, primary_key=True)

    crs_id = db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'))
    course = db.relationship('course', primaryjoin='prereq.crs_id == course.course_id', backref=db.backref('course', lazy='dynamic'))

    prereq_courses = db.Column(db.ARRAY(db.Integer))
    grade_required = db.Column(db.Integer)
    

"""
A course with its id, title, number, credits, and its prereq
ForeignKeys: 
subject it belongs to using the subjects code
when it is offered using the term
"""
#TODO: add definitions to modify, get, and check the course table and its child tables
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
    db.Column('frequency', db.Integer) )

    def __init__(self, id, title, num, credits):
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
#TODO: add definitions to get term and year
class semester(db.Model):
    semester_id = db.Column(primary_key=True)
    term = db.Column(db.String(100))
    year = db.Column(db.Integer)

    def __init__(self, term, year):
        #TODO: uncomment if plan last_id works
        """
        last_id = requirement.query.order_by(semester.semester_id.desc()).first() #Should get last id in list if any

        if last_id:
            self.semester_id = last_id[0] + 1
        else:
            self.semester_id = 1
        """
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
        #Main Course table variables
        c_id = request.form["c_id"]
        session["c_id"] = c_id
        c_subj_id = request.form["c_subj_id"]
        session["c_subj_id"] = c_subj_id
        c_title = request.form ["c_title"]
        session["c_tittle"] = c_title
        c_num = request.form["c_num"]
        session["c_num"] = c_num
        c_credits = request.form["c_credits"]
        session["c_credits"] = c_credits

        #Sub table Course required table variables
        crs_req_r_id = request.form["crs_req_r_id"]
        session["crs_req_r_id"] = crs_req_r_id
        crs_req_c_id = request.form["crs_req_c_id"]
        session["crs_req_c_id"] = crs_req_c_id

        #Sub table Course offered table variables
        crs_off_o_id = request.form["crs_off_o_id"]
        session["crs_off_o_id"] = crs_off_o_id
        crs_off_c_id = request.form["crs_off_c_id"]
        session["crs_off_c_id"] = crs_off_c_id
        crs_off_s_id = request.form["crs_off_s_id"]
        session["crs_off_s_id"] = crs_off_s_id
        crs_off_freq = request.form["crs_off_freq"]
        session["crs_off_freq"] = crs_off_freq


        new_crs = course(c_id,c_title, c_num, c_credits)
        new_crs.add_commit()
        return "Course made successfully"
    
@app.route("/prereq", methods=["POST", "GET"])
def test_prereq():
    return "Test"

@app.route("/users", methods=["POST", "GET"])
def users():
    if request.method == "POST":
        email = request.form["email"]
        session["email"] = email
        password = request.form["password"]
        session["password"] = password
        user(email, password)
        return "Successfully added user"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)