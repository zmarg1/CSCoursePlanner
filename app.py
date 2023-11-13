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

# DB models
"""
The user object class to interact with the authorization table in supabase
user_obj - Stores the created supabase 'user' object
admin - The users permission level
campus_id - The campus id of the given user
"""
#TODO: Make def for adding plan_id and deg_id to the class variables from user obj in database
class users():
    """
    How to interact with user metadata
    admin = user.user.user_metadata.get('admin')
    user.user.user_metadata['campus_id'] = 'KD89'
    """
    admin = False

    #Makes a user from the session if user given
    def __init__(self, user=None):
        if user:
            self.user_obj = user
            self.admin = user.user.user_metadata.get('admin')

    #Signs up a new user
    def signup(self, email, password, admin=False):
        max_retries = 3
        retry_count = 0

        #Tries 3 times to signup a user and prints the error for each failure in 10sec intervals
        while retry_count < max_retries:
            try:
                in_auth = client.auth.get_user("email" == email)

                #If user not in session signs them up and fills class variables
                if not in_auth:
                    new_user = client.auth.sign_up({
                        "email": email,
                        "password": password,
                        "options":{
                            "data":{
                                "admin": admin
                            }
                        }
                        })
                    self.user_obj = new_user
                    self.user_id = new_user.user.id
                    self.admin = new_user.user.user_metadata.get('admin')
                    return new_user
            except Exception as e:
                print(f"Authentication error: {e} for {email}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(10)
        return None
    
    #Returns the id on success and none on failure
    def signin(self, email, password):
        try:
            curr_usr = client.auth.sign_in_with_password({"email": email, "password": password})
            self.user_obj = curr_usr
            #TODO: Uncomment when supabase emails are working
            """self.admin = curr_usr.user.user_metadata.get('admin')"""
        except Exception as e:
            print(f"Authentication error: {e} for {email}")
            return None
        return True


    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class public_user_info(db.Model):
    user_id = db.Column('user_id',primary_key=True)
    email = db.Column('email',db.String(100))
    campus_id = db.Column('campus_id',db.String(100))
    first_name = db.Column('first_name',db.String(100))
    last_name = db.Column('last_name',db.String(100))

    def __init__(self, id, new_email=None, new_campus_id=None, new_f_name=None, new_l_name=None):
        self.user_id = id
        self.email = new_email
        self.campus_id = new_campus_id
        self.first_name = new_f_name
        self.last_name = new_l_name

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update_campus_id(self, email, new_c_id):
        pass

    def update_name(self, email, new_f_name=None, new_l_name=None):
        pass

    def update_email(self, email=None):
        pass

    def get_all_users():
        all_users = public_user_info.query.all()
        return all_users


# Defines your user output
class PublicUserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("user_id", "email", "campus_id", "first_name","last_name")

public_user_schema = PublicUserSchema()
public_users_schema = PublicUserSchema(many=True)

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
    deg_name = db.Column('degree_name', db.String(100))
    deg_type = db.Column('degree_type', db.String(100))

    def __init__(self, id, name, type):
        #TODO: uncomment if plan last_id works 
        """
        last_id = degree.query.order_by(degree.degree_id.desc()).first() #Should get last id in list if any

        if last_id:
            self.degree_id = last_id[0] + 1
        else:
            self.degree_id = 1
        """
        self.degree_id = id
        self.deg_name = name
        self.deg_type = type

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

# Defines your degree output
class DegreeSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("degree_id", "deg_name", "deg_type")

degree_schema = DegreeSchema()
degrees_schema = DegreeSchema(many=True)

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


    def __init__(self, id, crs_id, prereq_courses, grade_required):
        self.prereq_id = id
        self.crs_id = crs_id
        self.prereq_courses = prereq_courses
        self.grade_required = grade_required


# Defines your prereq output
class PrereqSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("prereq_id","crs_id", "prereq_courses", "grade_required")

prereq_schema = PrereqSchema()
prereqs_schema = PrereqSchema(many=True)


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
    subject_code = db.Column("subject_code", db.String(100))
    subject_name = db.Column("subject_name", db.String(100))

    def __init__(self, id, code, name):
        self.subject_id = id
        self.subject_code = code
        self.subject_name = name

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# Defines your subject output
class SubjectSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("subject_id", "subject_code", "subject_name")

subject_schema = SubjectSchema()
subjects_schema = SubjectSchema(many=True)


"""
Semester class holds the term and year a course is offered if offered
"""
#TODO: add definitions to get term and year
class semester(db.Model):
    semester_id = db.Column(primary_key=True)
    term = db.Column(db.String(100))
    year = db.Column(db.Integer)

    def __init__(self,id, term, year):
        #TODO: uncomment if plan last_id works
        """
        last_id = requirement.query.order_by(semester.semester_id.desc()).first() #Should get last id in list if any

        if last_id:
            self.semester_id = last_id[0] + 1
        else:
            self.semester_id = 1
        """
        self.semester_id = id
        self.term = term
        self.year = year

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


# Defines your semester output
class SemesterSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("semester_id", "term", "year")

semester_schema = SemesterSchema()
semesters_schema = SemesterSchema(many=True)


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
    course_id = request.json['course_id']
    subject_id = request.json['subject_id']
    course_title = request.json['crs_title']
    course_num = request.json['crs_num']
    credits = request.json['credits']

    new_course = course(course_id, subject_id, course_title, course_num, credits)

    db.session.add(new_course)
    db.session.commit()
    return course_schema.jsonify(new_course)

# endpoint for updating a course
@app.route('/admin/courses/update_course/<course_id>', methods = ['PUT'])
def update_course(course_id):
    updated_course = course.query.get(course_id)

    updated_course.subject_id = request.json['subject_id']
    updated_course.crs_title = request.json['crs_title']
    updated_course.crs_num = request.json['crs_num']
    updated_course.credits = request.json['credits']

    db.session.commit()
    return course_schema.jsonify(updated_course)

# endpoint for deleting a course
@app.route('/admin/courses/delete/<course_id>', methods = ['DELETE'])
def delete_course(course_id):
    deleted_course = course.query.get(course_id)

    db.session.delete(deleted_course)
    db.session.commit()
    return course_schema.jsonify(deleted_course)


# endpoint for getting all subjects
@app.route('/admin/subjects', methods = ['GET'])
def get_all_subjects():
    all_subjects = subject.query.order_by(subject.subject_id.asc()).all()
    subjects_dump = subjects_schema.dump(all_subjects)
    return jsonify(subjects_dump)


# endpoint for getting one subject
@app.route('/admin/subjects/<subject_id>', methods = ['GET'])
def get_subject(subject_id):
    my_subject = subject.query.get(subject_id)
    return subject_schema.jsonify(my_subject) 


# endpoint for creating a subject
@app.route('/admin/subjects/create_subject', methods = ['POST'])
def create_subject():
    subject_id = request.json['subject_id']
    subject_code = request.json['subject_code']
    subject_name = request.json['subject_name']
    new_subject = subject(subject_id, subject_code, subject_name)

    db.session.add(new_subject)
    db.session.commit()
    return subject_schema.jsonify(new_subject)


# endpoint for updating a subject
@app.route('/admin/subjects/update_subject/<subject_id>', methods = ['PUT'])
def update_subject(subject_id):
    updated_subject = subject.query.get(subject_id)

    updated_subject.subject_code = request.json['subject_code']
    updated_subject.subject_name = request.json['subject_name']
    
    db.session.commit()
    return subject_schema.jsonify(updated_subject)


# endpoint for deleting a subject
@app.route('/admin/subjects/delete/<subject_id>', methods = ['DELETE'])
def delete_subject(subject_id):
    deleted_subject = subject.query.get(subject_id)

    db.session.delete(deleted_subject)
    db.session.commit()
    return subject_schema.jsonify(deleted_subject)


# endpoint for getting all semesters
@app.route('/admin/semesters', methods = ['GET'])
def get_all_semesters():
    all_semesters = semester.query.order_by(semester.semester_id.asc()).all()
    semesters_dump = semesters_schema.dump(all_semesters)
    return jsonify(semesters_dump)


# endpoint for getting one semester
@app.route('/admin/semesters/<semester_id>', methods = ['GET'])
def get_semester(semester_id):
    my_semester = semester.query.get(semester_id)
    return semester_schema.jsonify(my_semester) 


# endpoint for creating a semester
@app.route('/admin/semesters/create_semester', methods = ['POST'])
def create_semester():
    semester_id = request.json['semester_id']
    term = request.json['term']
    year = request.json['year']
    new_semester = semester(semester_id, term, year)

    db.session.add(new_semester)
    db.session.commit()
    return semester_schema.jsonify(new_semester)


# endpoint for updating a semester
@app.route('/admin/semesters/update_semester/<semester_id>', methods = ['PUT'])
def update_semester(semester_id):
    updated_semester = semester.query.get(semester_id)

    updated_semester.term = request.json['term']
    updated_semester.year = request.json['year']
    
    db.session.commit()
    return semester_schema.jsonify(updated_semester)


# endpoint for deleting a semester
@app.route('/admin/semesters/delete/<semester_id>', methods = ['DELETE'])
def delete_semester(semester_id):
    deleted_semester = semester.query.get(semester_id)
    db.session.delete(deleted_semester)
    db.session.commit()
    return semester_schema.jsonify(deleted_semester)

# Users
# endpoint for getting all public users
@app.route('/admin/users', methods = ['GET'])
def get_all_users():
    all_users = public_user_info.query.order_by(public_user_info.user_id.asc()).all()
    users_dump = public_users_schema.dump(all_users)
    return jsonify(users_dump)


# endpoint for getting one public user
@app.route('/admin/users/<user_id>', methods = ['GET'])
def get_user(user_id):
    my_user = public_user_info.query.get(user_id)
    return public_user_schema.jsonify(my_user) 


# endpoint for creating a user
@app.route('/admin/users/create_user', methods = ['POST'])
def create_user():
    user_id = request.json['user_id']
    email = request.json['email']
    campus_id = request.json['campus_id']
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    new_user = public_user_info(user_id, email, campus_id, first_name, last_name)

    db.session.add(new_user)
    db.session.commit()
    return public_user_schema.jsonify(new_user)


# endpoint for updating a user
@app.route('/admin/users/update_user/<user_id>', methods = ['PUT'])
def update_user(user_id):
    updated_user = public_user_info.query.get(user_id)

    updated_user.email = request.json['email']
    updated_user.campus_id = request.json['campus_id']
    updated_user.first_name = request.json['first_name']
    updated_user.last_name = request.json['last_name']
    
    db.session.commit()
    return public_user_schema.jsonify(updated_user)


# endpoint for deleting a user
@app.route('/admin/users/delete/<user_id>', methods = ['DELETE'])
def delete_user(user_id):
    deleted_user = public_user_info.query.get(user_id)
    db.session.delete(deleted_user)
    db.session.commit()
    return public_user_schema.jsonify(deleted_user)


# Prereq
# endpoint for getting all prereqs
@app.route('/admin/prereqs', methods = ['GET'])
def get_all_prereqs():
    all_prereqs = prereq.query.order_by(prereq.prereq_id.asc()).all()
    prereqs_dump = prereqs_schema.dump(all_prereqs)
    return jsonify(prereqs_dump)


# endpoint for getting one prereq
@app.route('/admin/prereqs/<prereq_id>', methods = ['GET'])
def get_prereq(prereq_id):
    my_prereq = prereq.query.get(prereq_id)
    return prereq_schema.jsonify(my_prereq) 


# endpoint for creating a prereq
@app.route('/admin/prereqs/create_prereq', methods = ['POST'])
def create_prereq():
    prereq_id = request.json['prereq_id']
    crs_id = request.json['crs_id']
    prereq_courses = request.json['prereq_courses']
    grade_required = request.json['grade_required']
    new_prereq = prereq(prereq_id, crs_id, prereq_courses, grade_required)

    db.session.add(new_prereq)
    db.session.commit()
    return prereq_schema.jsonify(new_prereq)


# endpoint for updating a prereq
@app.route('/admin/prereqs/update_prereq/<prereq_id>', methods = ['PUT'])
def update_prereq(prereq_id):
    updated_prereq = prereq.query.get(prereq_id)

    updated_prereq.crs_id = request.json['crs_id']
    updated_prereq.prereq_courses = request.json['prereq_courses']
    updated_prereq.grade_required = request.json['grade_required']
    
    db.session.commit()
    return prereq_schema.jsonify(updated_prereq)


# endpoint for deleting a prereq
@app.route('/admin/prereqs/delete/<prereq_id>', methods = ['DELETE'])
def delete_prereq(prereq_id):
    deleted_prereq = prereq.query.get(prereq_id)
    db.session.delete(deleted_prereq)
    db.session.commit()
    return prereq_schema.jsonify(deleted_prereq)


# Degree
# endpoint for getting all degrees
@app.route('/admin/degrees', methods = ['GET'])
def get_all_degrees():
    all_degrees = degree.query.order_by(degree.degree_id.asc()).all()
    degrees_dump = degrees_schema.dump(all_degrees)
    return jsonify(degrees_dump)


# endpoint for getting one degree
@app.route('/admin/degrees/<degree_id>', methods = ['GET'])
def get_degree(degree_id):
    my_degree = degree.query.get(degree_id)
    return degree_schema.jsonify(my_degree) 


# endpoint for creating a degree
@app.route('/admin/degrees/create_degree', methods = ['POST'])
def create_degree():
    degree_id = request.json['degree_id']
    deg_name = request.json['deg_name']
    deg_type = request.json['deg_type']
    new_degree = degree(degree_id, deg_name, deg_type)

    db.session.add(new_degree)
    db.session.commit()
    return degree_schema.jsonify(new_degree)


# endpoint for updating a degree
@app.route('/admin/degrees/update_degree/<degree_id>', methods = ['PUT'])
def update_degree(degree_id):
    updated_degree = degree.query.get(degree_id)

    updated_degree.degree_id = request.json['degree_id']
    updated_degree.deg_name = request.json['deg_name']
    updated_degree.deg_type = request.json['deg_type']
    
    db.session.commit()
    return degree_schema.jsonify(updated_degree)


# endpoint for deleting a degree
@app.route('/admin/degrees/delete/<degree_id>', methods = ['DELETE'])
def delete_degree(degree_id):
    deleted_degree = degree.query.get(degree_id)
    db.session.delete(deleted_degree)
    db.session.commit()
    return degree_schema.jsonify(deleted_degree)


"""
# Endpoint to delete all records and insert new data
@app.route('/admin/courses_offered/update', methods=['POST'])
def update_course_offered():
    try:
        # Delete all records from the "course_offered" table
        CourseOffered.query.delete()

        # Insert new data into the "course_offered" table
        new_data = request.get_json()
        for row in new_data:
            course = CourseOffered(**row)
            db.session.add(course)

        # Commit the changes
        db.session.commit()

        return jsonify({'message': 'Data updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""

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
      
