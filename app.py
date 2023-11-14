"""
Authors: Amir Hawkins-Stewart & Zach Margulies

Description: Makes objects of the databse tables, sends and recieves data from the supabase databse.

TODO: Finish the classes, app.routes to send and receive from site 
"""

from flask import Flask, request, session, jsonify, make_response, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from flask_marshmallow import Marshmallow
from supabase import Client #import supabase.py not supabase
import datetime
from datetime import timedelta, datetime
import time

client_key ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTU0MDcxNjcsImV4cCI6MjAxMDk4MzE2N30.UNZJCMI1NxpSyFr8bBooIIGPqTbDe3N-_YV9ZHbE_1g"
secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NTQwNzE2NywiZXhwIjoyMDEwOTgzMTY3fQ.5IP6Kh6jI3mL_3poMSKcjE_cANIjhqvGHJVjK5RNVMw"
url = "https://qwydklzwvbrgvdomhxjb.supabase.co"
client = Client(url, client_key)
client_admin = Client(url, secret_key)

app = Flask(__name__)
CORS(app)
app.secret_key = secret_key #Secret key needed for sessions to get the encrypted data
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
app.permanent_session_lifetime = timedelta(hours = 1) #How long the session data will be saved for

db = SQLAlchemy(app)
ma = Marshmallow(app)
FAILED_USER_IN = {"Failed": "User not signed in"}


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
    user.user.app_metadata['campus_id'] = 'KD89'
    """
    email = None
    admin = False
    plan_ids = []

    #Makes a user from the session if user given
    def __init__(self, new_email=None, admin=False):
        if new_email:
            self.email = new_email
            self.admin = admin

    #Signs up a new user
    def signup(self, password, admin=False):
        max_retries = 3
        retry_count = 0

        #Tries 3 times to signup a user and prints the error for each failure in 10sec intervals
        while retry_count < max_retries:
            try:
                in_public = public_user_info.query.filter(self.email == public_user_info.email).first()

                #If user not in session signs them up and fills class variables
                if not in_public:
                    new_user = client.auth.sign_up({
                        "email": self.email,
                        "password": password,
                        "user_metadata":{
                                "admin": admin
                            }
                        })
                    self.user_obj = new_user
                    self.user_id = new_user.user.id
                    self.admin = new_user.user.user_metadata.get('admin')
                    return new_user
            except Exception as e:
                print(f"Authentication error: {e} for {self.email}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(10)
        return None
    
    #Returns the id on success and none on failure
    def signin(self, password):
        try:
            curr_usr = client.auth.sign_in_with_password({"email": self.email, "password": password})
            self.admin = curr_usr.user.user_metadata.get('admin')
        except Exception as e:
            print(f"Authentication error: {e} for {self.email}")
            return None
        self.update_user_plan_ids()
        return True


    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()

    def get_user_id(self):
        usr_id = public_user_info.get_user_id(self.email)
        return usr_id

    def update_user_plan_ids(self):
        usr_id = self.get_user_id()
        plan_objs = plan.query.filter(usr_id == plan.user_id)
        for obj in plan_objs:
            self.plan_ids.append(obj.plan_id)

    #User views all of their plans
    def get_plans(self):
        user_id = self.get_user_id()
        plan_obj = plan.query.filter(plan.user_id == user_id)
        usr_plans = []
        
        #gets the list of <plan id>
        for obj in plan_obj:
            usr_plans.append(obj)
        if usr_plans:
            return usr_plans
        return None


#TODO: Finish definitions
class public_user_info(db.Model):
    public_user_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)
    email = db.Column(db.String)
    campus_id = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    def __init__(self, new_email, new_campus_id=None, new_f_name=None, new_l_name=None):
        if new_email:
            self.email = new_email
            self.campus_id = new_campus_id
            self.first_name = new_f_name
            self.last_name = new_l_name

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_user_id(email):
        user = public_user_info.query.filter(public_user_info.email == email).first()
        user_id = user.user_id
        return user_id
    
    def get_all_users():
        all_users = public_user_info.query.all()
        return all_users

    def update_campus_id(self, new_c_id):
        pass

    def update_name(self,new_f_name=None, new_l_name=None):
        pass

    def update_email(self):
        pass


"""
Users plan where they will store there courses
plan_id (PrimaryKey) - unique id of plan in database
user_id (ForeignKey) - unique id of User whos plan it is
plan_num - User specific incrementing plan number starting at: 0
plan_name - renamable name of the users plan w/ incrementing default name: default plan 0
created_at - time of plan creation
"""
class plan(db.Model):
    plan_id = db.Column( db.Integer, primary_key=True)

    user_id = db.Column(db.String)

    plan_num = db.Column(db.Integer)
    plan_name = db.Column(db.String(100))
    created_at = db.Column(db.Time)

    def __init__(self, new_plan_id=None):
        if new_plan_id:
            self.plan_id = new_plan_id

    """
    Makes a plan for the user
    """
    def make_plan(self, user_id ,num=0, name="default plan 0"):
        if user_id:
            self.user_id = user_id

            #Get last id in list if any
            last_id = plan.query.order_by(plan.plan_id.desc()).first() 
            last_num = plan.query.filter(plan.user_id == self.user_id).order_by(plan.plan_num.desc()).first()

            #Increments databse plan id if not empty or makes the first plan w/ id 1
            if last_id:
                self.plan_id = last_id.plan_id + 1
            else:
                self.plan_id = 1

            if last_num:
                self.plan_num = last_num.plan_num + 1
                self.plan_name = f"default plan {last_num.plan_num+1}"

            else:
                self.plan_num = num
                self.plan_name = name

            self.created_at = datetime.now()

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()


    """"
    Views current plan
    Gets users plan by going through taken
    makes a list of all the courses that match plan id
    returns the list of courses from taken table if their is a plan
    returns None if no plan
    """
    def get_taken_courses(self):
        taken_plan_objs = taken.query.filter(self.plan_id == taken.plan_id)

        if taken_plan_objs:
            return taken_plan_objs
        return None
    
    """
    View the course objects of the current plan
    returns the list of courses from the course table if plan exists
    returns None if no plan
    """
    def get_courses(self):
        taken_crs_ids = []
        taken_plan_objs = taken.query.filter(self.plan_id == taken.plan_id)

        if taken_plan_objs:
            #Get the course ids for matched plan
            for taken_obj in taken_plan_objs:
                taken_crs_ids.append(taken_obj.course_id)

            courses = []
            for crs_id in taken_crs_ids:
                crs_obj = course.query.get(crs_id)
                courses.append(crs_obj)
            return courses
        return None

class PlanSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("plan_id", "user_id", "plan_num", "plan_name")

plan_schema = PlanSchema()
plans_schema = PlanSchema(many=True)


"""
The users degree with name of degree and type of degree
Column:
degree_id (PrimaryKey) - unique id of degree in database
deg_name - name of degree
deg_type - shorter acronym of degree name
"""
class degree(db.Model):
    degree_id = db.Column(db.Integer, primary_key=True)
    deg_name = db.Column(db.String(100))
    deg_type = db.Column(db.String(100))

    def __init__(self, name, type):
        last_id = degree.query.order_by(degree.degree_id.desc()).first()

        if last_id:
            self.degree_id = last_id.degree_id + 1
        else:
            self.degree_id = 1

        self.deg_name = name
        self.deg_type = type

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()


"""
The requirements for the Degree containing its type and subtype
Columns:
requirement_id (PrimaryKey)- Unique id of requirement in database
degree_id (ForeignKey) - Unique id of users degree in database
requirement_type - #TODO
requirement_subtype - #TODO
"""
class requirement(db.Model):
    requirement_id = db.Column(db.Integer, primary_key=True)

    degree_id = db.Column(db.Integer, db.ForeignKey('degree.degree_id'))
    degree = db.relationship('degree', primaryjoin='requirement.degree_id == degree.degree_id', backref=db.backref('degree', lazy='dynamic'))

    requirement_type = db.Column(db.String(100))
    requirement_subtype = db.Column(db.String(100))

    def __init__(self, type, subtype):
        last_id = requirement.query.order_by(requirement.requirement_id.desc()).first()

        if last_id:
            self.requirement_id = last_id.requirement_id + 1
        else:
            self.requirement_id = 1

        self.type = type
        self.subtype = subtype

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()


"""
Courses needed before taking course
Columns:
crs_id (ForeignKey) - Unique id of the course user wants to take
prereq_courses - Courses user needs to take before the wanted course
grade_required - Grade needed for prereq course
"""
class prereq(db.Model):
    prereq_id = db.Column(db.Integer, primary_key=True)

    crs_id = db.Column('course_id', db.Integer, db.ForeignKey('course.course_id'))
    course = db.relationship('course', primaryjoin='prereq.crs_id == course.course_id', backref=db.backref('course', lazy='dynamic'))

    prereq_courses = db.Column(db.ARRAY(db.Integer))
    grade_required = db.Column(db.Integer)

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()
    

"""
The course table with its sub tables of offered courses and course requirements
Columns:
course_id (PrimaryKey)- Unique id of the course in database 
subject_id (ForeignKey)- Unique id of subject in database
course_title - Title of the course
course_num - Course numerical level ex. 201
credits - A courses credits given
Sub tables:
crs_offered - Tracks when a course is offered
crs_required - Tracks what a course needs to be taken
"""
#TODO: add definitions to modify, get, and check the course table and its child tables
class course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'))
    subject = db.relationship('subject', primaryjoin='course.subject_id == subject.subject_id', backref=db.backref('subject', lazy='dynamic'))

    course_title = db.Column(db.String(100))
    course_num = db.Column(db.Integer)
    credits = db.Column(db.Integer)


    crs_offered = db.Table('course_offered',
    db.Column('offered_id', db.Integer, primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('semester_id', db.Integer, db.ForeignKey('semester.semester_id')),
    db.Column('frequency', db.Integer) )

    crs_required = db.Table('courses_required',
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirement.requirement_id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('course_options', db.ARRAY(db.Integer)))

    def __init__(self, title=None, subject_id=None, crs_num=None, credits=None):
        
        if title and crs_num and credits and subject_id:
            self.course_title = title
            self.course_num = crs_num
            self.credits = credits
            self.subject_id = subject_id
                

            last_id = course.query.order_by(course.course_id.desc()).first()
            if last_id:
                self.course_id = last_id.course_id + 1
            else:
                self.course_id = 1



    def add_course(self, id, subject_id, title, num, credits):
        self.course_id = id
        self.subject_id = subject_id
        self.crs_title = title
        self.crs_num = num
        self.credits = credits

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()

    def add_prereq(self, req):
        self.prereq = req
        db.session.commit()

    def get_courses_offered(self):
        stmt = db.select(self.crs_offered).where(
            db.and_(
                self.crs_offered.c.course_id != None
            )
        )
        result = db.session.execute(stmt).fetchall()
        return result

"""
Defines course output for Admins
"""
class AdminCourseSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("course_id", "subject_id", "course_title","course_num","credits")

admin_course_schema = AdminCourseSchema()
admin_courses_schema = AdminCourseSchema(many=True)

#Defines course output for Users
class UserCourseSchema(ma.Schema):
    subject_code = fields.Function(lambda obj: obj.subject.sub_code if obj.subject else None)
    class Meta:
        fields = ("course_id", "subject_code", "course_title", "course_num", "credits")

user_courses_schema = UserCourseSchema(many = True)


"""
UMBC subject fields offered to be used for a course
Columns:
subject_id (PrimaryKey)- Unique id of the subject in database 
sub_code - The contraction of the subject name ex. CMSC
sub_name - The name of the subject ex. Computer Science
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

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()


"""
Semester is the term and year used for when a course is offered and making a plan
Columns:
semester_id (PrimaryKey) - Unique id of the semester in database
term - The term
year - The year
"""
class semester(db.Model):
    semester_id = db.Column(primary_key=True)
    term = db.Column(db.String(100))
    year = db.Column(db.Integer)
    current_year = None
    current_term = None
    last_year = None

    def __init__(self, term=None, year=None):
        if term and year:
            last_id = semester.query.order_by(semester.semester_id.desc()).first()

            if last_id:
                self.semester_id = last_id.semester_id + 1
            else:
                self.semester_id = 1

            self.term = term
            self.year = year

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()

    """
    Gets the approximate term of the current year
    """
    def update_year_term(self):
        curr_date = datetime.now()
        curr_month = curr_date.month

        self.current_year = curr_date.year

        if curr_month in range(1,5): #Jan 29 to May 14
            self.current_term = "Spring"
        elif curr_month in range(5,8): #May 30 to Aug 18
            self.current_term = "Summer"
        elif curr_month in range(8,12): #Aug 30 to Dec 12
            self.current_term = "Fall"
        else:
            self.current_term = "Winter"

    """
    Gets all objects for a specific term
    Fall, Winter, Spring, Summer
    Input: a list of courses in a plan
    Return: if input given 
    """
    def get_fall_objs(self, list_courses=None, curr=True):
        if list_courses:
            pass
        elif not curr:
            fall_objs = []
            semesters = self.get_old_year_objs()
            for sem in semesters:
                if sem.term == "Fall":
                    fall_objs.append(sem)
            return fall_objs
        else:
            fall_objs = []
            semesters = self.get_year_order_objs()
            for sem in semesters:
                if sem.term == "Fall":
                    fall_objs.append(sem)
            return fall_objs

    def get_winter_objs(self, list_courses=None):
        if list_courses:
            pass
        semesters = self.get_year_order_objs()
        winter_objs = []
        for sem in semesters:
            if sem.term == "Winter":
                winter_objs.append(sem)
        return winter_objs

    def get_spring_objs(self, list_courses=None):
        if list_courses:
            pass
        spring_objs = []
        semesters = self.get_year_order_objs()
        for sem in semesters:
            if sem.term == "Spring":
                spring_objs.append(sem)
        return spring_objs

    def get_summer_objs(self, list_courses=None):
        if list_courses:
            pass
        summer_objs = []
        semesters = self.get_year_order_objs()
        summer_objs = []
        for sem in semesters:
            if sem.term == "Summer":
                summer_objs.append(sem)
        return summer_objs

    """
    Gets relevant semesters based on current year and approximate term
    """
    def get_year_order_objs(self):
        self.update_year_term()
        curr_year = self.current_year
        curr_term = self.current_term
        all_semesters = semester.query.all()
        order_objs = []
        reached_term = False
        for obj in all_semesters:
            if reached_term:
                order_objs.append(obj)
                self.last_year = obj.year
            elif obj.year == curr_year and obj.term == curr_term and not reached_term:
                reached_term = True
                order_objs.append(obj)
                self.last_year = obj.year
        return order_objs
    
    """
    Gets all semesters before current year
    Used for checking if a course will be offered
    """
    def get_old_year_objs(self):
        self.update_year_term()
        curr_year = self.current_year
        curr_term = self.current_term
        all_semesters = semester.query.all()
        order_objs = []
        before_term = True
        for obj in all_semesters:
            if before_term:
                order_objs.append(obj)
            elif obj.year == curr_year and obj.term == curr_term and not before_term:
                before_term = False
                order_objs.append(obj)
        return order_objs
    

class SemesterCourseSchema(ma.Schema):
    class Meta:
        fields = ("term", "year")

semesters_schema = SemesterCourseSchema(many = True)


"""
Takes the planned course and assigns it to the plan with the semester of the plan and the chosen requirement type from the course
Columns:
taken_id (PrimaryKey) - Unique id of taken in database
plan_id (ForeignKey) - Unique id of the plan in database
course_id (ForeignKey) - Unique id of the course in database
requirement_id (ForeignKey) - Unique id of the requirement in database
semester_id (ForeignKey) - Unique id of the semester in database
grade - A courses grade is used to check if a course is taken or not
"""
#TODO: Finish definitions
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

    def __init__(self, taken_obj=None):
        if taken_obj:
            self.taken_id = taken_obj.taken_id
            self.plan_id = taken_obj.plan_id
            self.course_id = taken_obj.course_id
            self.requirement_id = taken_obj.requirement_id
            self.semester_id = taken_obj.semester_id
            self.grade = taken_obj.grade

    #Adds a course to a plan
    def add_course(self, pln_id, crs_id, req_id, sem_id, new_grade=None):
        last_id = taken.query.order_by(taken.taken_id.desc()).first() 

        if last_id:
            self.taken_id = last_id.taken_id + 1
        else:
            self.taken_id = 1

        self.plan_id = pln_id
        self.course_id = crs_id
        self.requirement_id = req_id
        self.semester_id = sem_id
        self.grade = new_grade

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()

    """
    Takes a plan id and searches for all courses in that plan
    Returns: all courses in year order of that plan
    """
    def get_courses_ordered(self, find_plan_id):
        pass

    def get_semester_courses(self, find_sem_id):
        pass

    #to check if course can be take
    def requirement_choice():
        pass


"""
Flask Routes
"""
@app.route('/')
def hello():
    return "Hello"


"""
Enters main admin page for admin functionality
Returns:
string: A welcome message
"""
@app.route('/admin')
def admin():
    return "Welcome to the Admin page"


"""
Endpoint for getting one courses
"""
@app.route('/admin/courses/<course_id>', methods = ['GET'])
def admin_get_course(course_id):
    if "user_email" in session:
        if session["admin"]:
            my_course = course.query.get(course_id)
            return admin_course_schema.jsonify(my_course)
        return jsonify({"Failed": "User is not admin"})
    
    return jsonify({"Failed": "User not signed in"}) 


"""
Endpoint for getting all course
"""
@app.route('/admin/view-courses', methods = ['GET'])
def admin_get_all_courses():
    if "user_email" in session:
        if session["admin"]:
            all_courses = course.query.order_by(course.course_id.asc()).all()
            courses_dump = admin_courses_schema.dump(all_courses)
            return jsonify(courses_dump)
        return jsonify({"Failed": "User is not admin"})
    return jsonify({"Failed": "User not signed in"}) 


"""
Endpoint for creating a course
Inputs:
course_title - Title of course to be added
subject - Id/Code/Name of subject to be added
crs_num - Course numerical level
credits - Credits course is worth
"""
@app.route('/admin/courses/create_course', methods = ['POST'])
def admin_create_course():
    if "user_email" in session:
        if session["admin"]:
            crs_title = request.json['course_title']
            _subject = request.json['subject']
            crs_num = request.json['crs_num']
            credits = request.json['credits']

            is_code = None
            is_id = None
            is_name = None
            #Checks if subject input is an int or a string
            if isinstance(_subject, int):
                is_id = subject.query.filter(subject.subject_id == _subject).first()
            if isinstance(_subject, str):
                is_code = subject.query.filter(subject.sub_code == _subject).order_by().first()
                is_name = subject.query.filter(subject.sub_name == _subject).order_by().first()

            if is_id:
                new_course = course(crs_title, _subject, crs_num, credits)
                new_course.add_commit()
            elif is_code:
                new_course = course(crs_title, is_code.subject_id, crs_num, credits)
                new_course.add_commit()
            elif is_name:
                new_course = course(crs_title, is_name.subject_id, crs_num, credits)
                new_course.add_commit()
            else:
                return jsonify ({"fail": "Failed Post"})
    
            return admin_course_schema.jsonify(new_course)
        
        return jsonify({"Failed": "User is not admin"})
        
    return jsonify({"Failed": "User not signed in"}) 


# endpoint for updating a course
@app.route('/admin/courses/update_course/<course_id>', methods = ['PUT'])
def update_course(course_id):
    if "user_email" in session:
        if session["admin"]:
            updated_course = course.query.get(course_id)

            updated_course.subject_id = request.json['subject_id']
            updated_course.crs_title = request.json['crs_title']
            updated_course.crs_num = request.json['crs_num']
            updated_course.credits = request.json['credits']

            db.session.commit()
            return admin_course_schema.jsonify(updated_course)
        
        return jsonify({"Failed": "User is not admin"})
    
    return jsonify({"Failed": "User not signed in"})


# endpoint for updating a course
@app.route('/admin/courses/delete/<course_id>', methods = ['DELETE'])
def delete_course(course_id):
    if "user_email" in session:
        if session["admin"]:
            deleted_course = course.query.get(course_id)

            db.session.delete(deleted_course)
            db.session.commit()
            return admin_course_schema.jsonify(deleted_course)
            
        return jsonify({"Failed": "User is not admin"})
        
    return jsonify({"Failed": "User not signed in"})


"""
Signs up the user
Inputs:
email - New users email
password - New users password
"""
#TODO: Setup for Clerk
@app.route("/user/signup", methods=["POST"])
def user_signup():
    email = request.form["email"]
    password = request.form["password"]

    if email and password:
        cur_user = users(email)
        result = cur_user.signup(password)
        if result:
            new_user = public_user_info(email)
            new_user.add_commit()
            return "Successfully signed up user"
        
        return "Failed to sign up user"
    return "Failed necessary fields are empty"


"""
Sign in the user
Inputs:
user email
user password
"""
#TODO: Setup for Clerk
@app.route("/user/signin", methods=["POST"])
def user_signin():
    email = request.form["email"]
    password = request.form["password"]
    
    check_user = client.auth.get_user()

    if email and password and "user_email" not in session and not check_user:
        curr_user = users(email)
        in_auth = curr_user.signin(password)
        if in_auth:
            curr_user.update_user_plan_ids()
            session["user_email"] = curr_user.email
            session["admin"] = curr_user.admin
            session["plan_ids"] = curr_user.plan_ids
            return jsonify({"Success": "Successfully signed in user"})
    elif "user_email" in session or check_user:
        return jsonify({"Failed": "User already signed in"})
    else:
        return jsonify({"Failed": "Failed neccessary fields left empty"})
   
    return "Failed to sign in user"


@app.route("/user/set-session", methods=["POST"])
def set_session():
    session["user_email"] = request.json["user_email"]
    email = session["user_email"]
    print("Session contents ", session)
    return jsonify(email)

"""
Signs out user from supabase and removes them from the session
"""
#TODO: Setup for Clerk
@app.route("/user/signout", methods=["SIGNOUT"])
def user_signout():
    is_user = client.auth.get_user()
    if is_user:
        user_email = is_user.user.email
        client.auth.sign_out()
        session.pop("user_email")
        session.pop("plan_ids")
        return f"Succesfully signed out {user_email}"
    if "user_email" in session:
        session.pop("user_email")
        session.pop("plan_ids")
    
    return "Failed no user signed in"


@app.route("/user/update-campus-id", methods=["POST", "GET"])
def update_campus_id():
    if "user_email" in session:
        new_c_id = request.form["campus_id"]
        usr_email = session["user_email"]
        curr_user = public_user_info(usr_email)
        curr_user.update_campus_id(new_c_id)
        curr_user.add_commit()
        return jsonify({"Success": "Successful campus id change"})
    
    client.auth.sign_out()
    return jsonify(FAILED_USER_IN)


"""
Makes an empty plan for the user
"""
@app.route("/user/plan/make-plan", methods=["PUT"])
def user_make_plan():
    if "user_email" in session:
        curr_user = users(session["user_email"])
        usr_id = curr_user.get_user_id()
        new_plan = plan()
        new_plan.make_plan(usr_id)
        if new_plan:
            new_plan.add_commit()
            session["curr_plan_id"] = new_plan.plan_id
            session["plan_ids"].append(new_plan.plan_id)
            return jsonify({"Success": "Successfully made plan"})
    client.auth.sign_out()
    return jsonify(FAILED_USER_IN)


@app.route("/user/plan/select-plan", methods={"PUT"})
def user_select_plan():
    if request.method == "PUT" and "user_email" in session and "plan_id" in request.json:
        chosen_plan_id = request.json["plan_id"]
        session["curr_plan_id"] = chosen_plan_id
        return jsonify({"Success": "Session current plan updated"})

    elif "user_email" not in session:
        return jsonify(FAILED_USER_IN)
    
    elif "plan_id" not in request.json:
        return jsonify({"Failed": "Missing \"plan_id\" field in json"})
    
    else:
        return jsonify({"Failed": "Wrong method used"})


"""
Deletes the users chosen plan
"""
@app.route("/user/plan/delete-plan", methods=["DELETE"])
def user_delete_plan():
    if "user_email" in session and "plan_id" in request.json and request.method == "DELETE":
        chosen_plan_id = request.json["plan_id"]
        curr_user = users(session["user_email"])

        if chosen_plan_id:
            usr_id = curr_user.get_user_id()
            to_delete = plan.query.filter(plan.plan_id == chosen_plan_id, plan.user_id == usr_id).first()

            if to_delete:
                plan_name = to_delete.plan_name
                chosen_plan = plan(to_delete.plan_id)
                plan_courses = chosen_plan.get_taken_courses()
                for taken_crs in plan_courses:
                    user_delete_course(taken_crs.course_id, chosen_plan_id)
                to_delete.delete_commit()
                return jsonify({"Success": f"Successfully deleted {plan_name}"})
            
            return jsonify({"Failed": "Current user can't delete this plan or plan not found"})
        
        return jsonify({"Failed": "No plan id given"})
    
    elif "user_email" not in session:
        client.auth.sign_out()
        return jsonify(FAILED_USER_IN)
    
    elif "plan_id" not in request.json:
        return jsonify({"Failed": "Missing \"plan_id\" field in json"})
    
    else:
        return jsonify({"Failed": "User not signed in"})


"""
Adds a course to users plan using taken
"""
@app.route("/user/plan/add-course-to-plan", methods=["POST"])
def user_add_to_plan():
    if "user_email" in session:
        if request.method == "POST" and "plan_id" in request.json and "crs_id" in request.json and "sem_id" in request.json:
            plan_id = request.json["plan_id"]
            crs_id = request.json["crs_id"]
            req_id = 1
            sem_id = request.json["sem_id"]
            grade = None

            #Checks if correct 
            if plan_id and crs_id and req_id and sem_id:
                in_plan = plan.query.filter(plan.plan_id == plan_id).order_by(plan.plan_id.desc()).first()
                in_course = course.query.filter(course.course_id == crs_id).order_by(course.course_id.desc()).first()
                in_req = requirement.query.filter(requirement.requirement_id == req_id).order_by(requirement.requirement_id.desc()).first()
                in_sem = semester.query.filter(semester.semester_id == sem_id).order_by(semester.semester_id.desc()).first()

                crs_in_taken = taken.query.filter(taken.plan_id == plan_id, taken.course_id == crs_id).order_by(taken.course_id.desc()).first()

                if in_plan and in_course and in_req and in_sem and not crs_in_taken:
                    add_to_plan = taken()
                    add_to_plan.add_course(plan_id, crs_id, req_id, sem_id, grade)
                    add_to_plan.add_commit()

                    return jsonify({"Success": f"Added {in_course.course_title} to {in_plan.plan_name} for {in_sem.term}"})
                elif crs_in_taken:
                    return jsonify({"Failed": "Course already in chosen plan"})
                elif not in_plan:
                    return jsonify({"Failed": "Failed Plan id not in database"})
                elif not in_course:
                    return jsonify({"Failed": "Failed Course id not in database"})
                elif not in_req:
                    return jsonify({"Failed": "Failed Requirement id not in database"})
                else:
                    return jsonify({"Failed": "Failed Semester id not in database"})
    
            return jsonify({"Failed": "Failed a necessary field(s) left empty"})
    
        return jsonify({"Failed": "Forms Missing"})
    client.auth.sign_out()
    return jsonify(FAILED_USER_IN)

#TODO: returns all the fall courses in a distionary {2024: [fall_courses],2025: [fall_courses], ...: [...]}
@app.route("/user/plan/get-all-fall-courses", methods=["GET"])
def get_all_fall():
    if "user_email" in session:
        select_term = request.json["sem_id"]

        if select_term:
            pass

        sem = semester()
        all_fall_objs = sem.get_fall_objs(None, False)
        crs = course()
        courses = crs.get_courses_offered()
        fall_courses = {}
        for sem in all_fall_objs:
            fall_courses[sem.year] = []
            for offr_id, crs_id, sem_id, freq in courses:
                if sem_id == sem.semester_id:
                    fall_courses[sem.year].append(crs_id)
        print("FALL COURSES ", fall_courses)
        return jsonify(fall_courses)
    return jsonify(FAILED_USER_IN)

@app.route("/user/plan/get-all-winter-courses", methods=["GET"])
def get_all_winter():
    pass

@app.route("/user/plan/get-all-spring-courses", methods=["GET"])
def get_all_spring():
    pass

@app.route("/user/plan/get-all-summer-courses", methods=["GET"])
def get_all_summer():
    pass


@app.route("/user/plan/delete-course-from-plan", methods=["DELETE"])
def user_delete_course(crs_id=None, plan_id=None):
    if request.method == "DELETE" and "course_id" in request.json and "curr_plan_id" in session:
        course_id = request.json["course_id"]
        curr_plan_id = session["curr_plan_id"]

        #Checks if correct 
        if course_id:
            in_taken = taken.query.filter(taken.course_id == course_id, taken.plan_id == curr_plan_id).first()
            crs_obj = course.query.get(in_taken.course_id)
            crs_title = crs_obj.course_id
            in_taken.delete_commit()
            return jsonify({"Success": f"Successfully deleted {crs_title}"})
        
    elif crs_id and plan_id:
        in_taken = taken.query.filter(taken.course_id == crs_id, taken.plan_id == plan_id).first()
        crs_obj = course.query.get(in_taken.course_id)
        crs_title = crs_obj.course_id
        in_taken.delete_commit()
        return jsonify({"Success": f"Successfully deleted {crs_title}"})
                
    elif "curr_plan_id" not in session:
        return jsonify({"Failed": "No plan in session"})  
      
    elif "course_id" not in request.json:
        return jsonify({"Failed": "Missing \"course_id\" field in json"})
    
    else:
        return jsonify({"Failed": "No Form"})


"""
Returns all the courses in the database for a user to see
"""
#TODO: make it show only necessary courses and able to update when required course added to plan
@app.route("/user/view-all-courses", methods=["GET"])
def user_view_all_courses():
    all_courses = course.query.all()
    courses_dump = user_courses_schema.dump(all_courses)
    return jsonify(courses_dump)


"""
Views all relevant semesters starting at current year and approximate term
"""
@app.route("/user/view-all-semesters", methods=["GET"])
def user_view_all_semesters():
    sem = semester()
    all_semesters = sem.get_year_order_objs()
    semester_dump = semesters_schema.dump(all_semesters)
    return jsonify(semester_dump)


"""
Chooses a plan to view
Gets user from session
Views the current users chosen plan
Returns: a json of courses in plan {course title, course number, credits, subject code}
"""
#TODO: make a guest user check
@app.route("/user/plan/view-plan", methods=["GET"])
def user_view_plan(plan_id=None):
    if request.method == "GET" and "curr_plan_id" in session and "user_email" in session and not plan_id:
        curr_plan = plan(session["curr_plan_id"])
        plans_courses = curr_plan.get_courses()
        courses_dump = user_courses_schema.dump(plans_courses)
        return jsonify(courses_dump)
    
    elif plan_id:
        curr_plan = plan(plan_id)
        plans_courses = curr_plan.get_courses()
        courses_dump = user_courses_schema.dump(plans_courses)
        return jsonify(courses_dump)
    
    elif "user_email" not in session:
        client.auth.sign_out()
        return jsonify(FAILED_USER_IN)
    
    elif "curr_plan_id" not in session:
        return jsonify({"Failed": "No plan in session"})
    
    else:
        return jsonify({"Failed": "Wrong method needs \"GET\" method"})


"""
Views all the users plans 
Return: plan obj on success ex. Default plan 0, Default plan 1
"""
@app.route("/user/plan/view-all-plans/<user_email>", methods=["GET"])
def view_all_plans(user_email):
    if user_email:
        user = users(user_email)
        usr_plans = user.get_plans()
        if usr_plans is not None:
            plans_dump = plans_schema.dump(usr_plans)
            return jsonify(plans_dump)
        else:
            return jsonify({"Failed": "User has no plans"})
    return jsonify({"Failed": "User not signed in"})


"""
Used to update any current users data when user object definitions are changed
"""
def update_all_users(all=True, usr_id=None):
    if all:
        su = client_admin.auth.admin.list_users()
        for user in su:
            update_data = {
                "user_metadata":{
                    "admin": False
                }
            }
            client_admin.auth.admin.update_user_by_id(user.id, update_data)
    else:
        su = client_admin.auth.admin.get_user_by_id(usr_id)
        update_data = {
            "user_metadata":{
                "admin": True
                }
        }
        client_admin.auth.admin.update_user_by_id(usr_id, update_data)


"""
Adds the auth table supabase user to the public table
"""
#TODO: Check if needed
@app.route("/dev/add-to-public", methods=["POST"])
def add_to_public():
    if request.method == "POST" and "email" in request.json:
        email = request.json["email"]
        in_table = public_user_info.query.filter(email == public_user_info.email).first()
        if not in_table:
            new_user = public_user_info(email)
            new_user.add_commit()
            return jsonify ({"Success": "Added to public user table"})
        return jsonify ({"Failed": "Email already in table"})
    
    return jsonify ({"Failed": "No Form"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
