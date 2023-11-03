"""
Author: Amir Hawkins-Stewart & Zach Margulies

Description: Currently class definitions for the planUMBC tables in supabase

TODO: Finish the classes, app.routes to send and receive from site 
"""

from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import supabase #import supabase.py not supabase
import time
from flask_marshmallow import Marshmallow
from flask_cors import CORS


url = "https://qwydklzwvbrgvdomhxjb.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTU0MDcxNjcsImV4cCI6MjAxMDk4MzE2N30.UNZJCMI1NxpSyFr8bBooIIGPqTbDe3N-_YV9ZHbE_1g"
client = supabase.create_client(url, key)

app = Flask(__name__)
CORS(app)

app.secret_key = "planUMBCkey" #Secret key needed for sessions to get the encrypted data
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
app.permanent_session_lifetime = timedelta(minutes = 5) #How long the session data will be saved for

db = SQLAlchemy(app)
ma = Marshmallow(app)

"""
The User will have an id, name, 'user'
ForeignKeys:
 The plan the user has made or has
 The users current degree
"""

"""class Course(db.Model):
    __tablename__ = 'course'  # Specify the table name

    # Define the columns of the 'course' table
    course_id = db.Column('course_id', db.Integer, primary_key = True)
    subject_id = db.Column('subject_id', db.Integer,nullable = False)
    course_title = db.Column('course_title', db.String(100), nullable = True)
    course_num = db.Column('course_num', db.Integer,nullable = True)
    credits = db.Column('credits', db.Integer,nullable = True)

    # Add more columns here as needed

    def __init__(self,course_title):
        self.course_title = course_title
        self.subject_id = subject_id
        self.course_num = course_num
        self.credits = credits


    def __repr__(self):
        return f"Course_ID: {self.course_id} ({self.subject_id}), Course: {self.course_num} - {self.course_title} ({self.credits})"""

#TODO: Make def for adding plan_id and deg_id to the class variables from user obj in database
class users():
    #Example of how to interact with items from user_obj
    #self.user_id = user_obj['id'] This can get the id, email
    #custom_data = user_obj.get('app_metadata', {}) This gets the plan_id, degree_id, campus_id
    user_obj = None
    user_id = None
    user_campus_id = None
    plan_id = None
    deg_id = None
    admin = False

    #Signs up a new user
    def signup(self, email, password):
        max_retries = 3
        retry_count = 0
        user = None
        while retry_count < max_retries:
            try:
                in_auth = client.auth.get_user("email" == email)
            
                if not in_auth:
                    user = client.auth.sign_up({
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
                    self.user_id = user.user.id
                    return True
            except Exception as e:
                print(f"Authentication error: {e} for {email}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(10)
        return False
    
    def signin(self, email, password):
        try:
            curr_usr = client.auth.sign_in_with_password({"email": email, "password": password})
        except Exception as e:
            print(f"Authentication error: {e} for {email}")
            return None
        
        return curr_usr

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

    user_id = db.Column(db.Integer)

    plan_num = db.Column(db.Integer)
    plan_name = db.Column(db.String(100))
    created_at = db.Column(db.Time)#need to test

    #Makes a plan for the user
    def __init__(self, num=1, name="default plan 0"):
        curr_user = client.auth.get_user()
        self.user_id = curr_user.user.id

        last_id = plan.query.order_by(plan.plan_id.desc()).first() #Get last id in list if any
        last_num = plan.query.filter(plan.user_id == self.user_id).order_by(plan.plan_num.desc()).first()

       #Testing view output
        if last_id:
            self.plan_id = last_id.plan_id + 1
        else:
            self.plan_id = 1

        if last_num:
            self.plan_num = last_num.plan_num + 1
            self.plan_name = f"default plan {self.plan_num}"
        else:
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
    subject_id = db.Column('subject_id', db.Integer, db.ForeignKey('subject.subject_id'))
    subject = db.relationship('subject', primaryjoin='course.subject_id == subject.subject_id', backref=db.backref('subject', lazy='dynamic'))
    
    crs_title = db.Column('course_title',db.String(100))
    crs_num = db.Column('course_num',db.Integer)
    credits = db.Column(db.Integer)

    crs_required = db.Table('courses_required',
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirement.requirement_id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('course_options', db.Integer))

    crs_offered = db.Table('course_offered',
    db.Column('offered_id', db.Integer, primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('semester_id', db.Integer, db.ForeignKey('semester.semester_id')),
    db.Column('frequency', db.Integer) )

    def __init__(self, id, subject_id, title, num, credits):
        self.course_id = id
        self.subject_id = subject_id
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


# Defines your course output
class CourseSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("course_id", "subject_id", "crs_title","crs_num","credits")

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

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

"""
Takes the planned course and assigns it to the plan with the semester of the plan and the chosen requirement type from the course
"""
#TODO: add def __init__, add_commit, delete, requirment_choice
class taken(db.Model):
    taken_id = db.Column(db.Integer, primary_key=True)

    plan_id = db.Column(db.String(100), db.ForeignKey('plan.plan_id'))
    plan = db.relationship('plan', primaryjoin='taken.plan_id == plan.plan_id', backref=db.backref('plan', lazy='dynamic'))

    course_id = db.Column(db.String(100), db.ForeignKey('course.course_id'))
    course = db.relationship('course', primaryjoin='taken.course_id == course.course_id', backref=db.backref('course_taken', lazy='dynamic'))

    requirement_id = db.Column(db.String(100), db.ForeignKey('requirement.requirement_id'))
    requirement = db.relationship('requirement', primaryjoin='taken.requirement_id == requirement.requirement_id', backref=db.backref('requirement_taken', lazy='dynamic'))

    semester_id = db.Column(db.String(100), db.ForeignKey('semester.semester_id'))
    semester = db.relationship('semester', primaryjoin='taken.semester_id == semester.semester_id', backref=db.backref('semester', lazy='dynamic'))

    grade = db.Column(db.Integer)

    def __init__(self, pln_id, crs_id, req_id, sem_id, new_grade=None):
        self.plan_id = pln_id
        self.course_id = crs_id
        self.requirement_id = req_id
        self.semester_id = sem_id
        self.grade = new_grade

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

#Flask Routes
@app.route('/')
def hello():
    return "Hello"


@app.route('/admin')
def admin():
    """Enters main admin page for admin functionality

    Returns:
        string: A welcome message
    """
    return "Welcome to the Admin page"


# endpoint for getting one courses
@app.route('/admin/courses/<course_id>', methods = ['GET'])
def get_course(course_id):
    my_course = course.query.get(course_id)
    return course_schema.jsonify(my_course) 


# endpoint for getting all course
@app.route('/admin/courses', methods = ['GET'])
def get_all_courses():
    all_courses = course.query.order_by(course.course_id.asc()).all()
    courses_dump = courses_schema.dump(all_courses)
    return jsonify(courses_dump)


# endpoint for creating a course
@app.route('/admin/courses/create_course', methods = ['POST'])
def create_course():
    new_course = course(request.json['course_title'])
    new_course.add_commit()
    return jsonify ({"success": "Success Post"})


"""
Sign in the user
Inputs:
user email
user password
"""
#TODO: add safety checks
@app.route("/user-signin", methods=["POST", "GET"])
def user_signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        curr_user = users()
        in_auth = curr_user.signin(email, password)
        if in_auth == None:
            return "Failed to sign in user"
        
        session["user_id"] = curr_user.user_id
        return "Successfully signed in user"


if __name__ == '__main__':
    app.run(debug=True)
      
