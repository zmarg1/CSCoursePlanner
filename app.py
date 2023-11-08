"""
Authors: Amir Hawkins-Stewart & Zach Margulies

Description: Makes objects of the databse tables, sends and recieves data from the supabase databse.

TODO: Finish the classes, app.routes to send and receive from site 
"""
import keys
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from flask_marshmallow import Marshmallow
from supabase import Client #import supabase.py not supabase
import datetime
from datetime import timedelta, datetime
import time

url = "https://qwydklzwvbrgvdomhxjb.supabase.co"
client = Client(url, keys.client_key)
client_admin = Client(url, keys.secret_key)

app = Flask(__name__)
app.secret_key = keys.secret_key #Secret key needed for sessions to get the encrypted data
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
app.permanent_session_lifetime = timedelta(hours = 1) #How long the session data will be saved for

db = SQLAlchemy(app)
cor = CORS(app)
ma = Marshmallow(app)


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
    fall_ids = []
    winter_ids = []
    spring_ids = []
    summer_ids = []

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

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def get_user_id(self):
        usr_list = client_admin.auth.admin.list_users()
        usr_id = None
        for usr in usr_list:
            if self.email == usr.email:
                usr_id = usr.id
        return usr_id

    def update_user_plan_ids(self):
        usr_id = self.get_user_id()
        plan_objs = plan.query.filter(usr_id == plan.user_id)
        for obj in plan_objs:
            self.plan_ids.append(obj.plan_id)

    #TODO: Make it get the course ids from the plan
    def update_term_ids(self):
        sem = semester()
        fall_ids = sem.get_fall_ids()
        winter_ids = sem.get_winter_ids()
        spring_ids = sem.get_spring_ids()

        for id in self.plan_ids:
            if id in fall_ids:
                self.fall_ids.append(id)
            elif id in winter_ids:
                self.winter_ids.append(id)
            elif id in spring_ids:
                self.spring_ids.append(id)
            else:
                self.summer_ids.append(id)

    """"
    User views current plan
    Gets users plan 
    uses plan id to go through taken
    makes a list of all the courses that match plan id
    returns the list of courses if their is a plan
    returns None if no plans
    """
    def view_plan(self, plan_id):
        taken_crs_ids = []
        taken_plan_objs = taken.query.filter(plan_id == taken.plan_id)

        if taken_plan_objs:
            #Get the course ids for matched plan
            for taken_obj in taken_plan_objs:
                taken_crs_ids.append(taken_obj.course_id)

            crs_objs = []
            #Gets the course objects using the ids from taken
            for crs_id in taken_crs_ids:
                crs_obj = course.query.filter(crs_id == course.course_id).first()
                crs_objs.append(crs_obj)
            return crs_objs
        return None

    #User views all of their plans
    def get_plans(self):
        user_id = self.get_user_id
        plan_obj = plan.query.filter(plan.user_id == user_id)
        plan_ids = []
        
        #gets the list of <plan id>
        for obj in plan_obj:
            plan_ids.append(obj.plan_id)
        return plan_ids


#TODO: Finish definitions
class public_user_info(db.Model):
    email = db.Column(db.String, primary_key=True)
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

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_user(email):
        user = public_user_info.query.filter("email" == email).first()
        return user
    
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

    user_id = db.Column(db.Integer)

    plan_num = db.Column(db.Integer)
    plan_name = db.Column(db.String(100))
    created_at = db.Column(db.Time)

    #Makes a plan for the user
    def __init__(self, user_id ,num=0, name="default plan 0"):
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

    def delete(self):
        db.session.delete(self)
        db.session.commit()


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

    def delete(self):
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

    def delete(self):
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

    def __init__(self, title, subject_id, crs_num, credits):
        
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

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def add_prereq(self, req):
        self.prereq = req
        db.session.commit()

"""
Defines course output for Admins
"""
class CourseSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("course_id", "subject_id", "course_title","course_num","credits")

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)


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

    def delete(self):
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

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    """
    Gets the approximate term of the year
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

    def get_fall_ids(self):
        fall_ids = []
        fall_objs = semester.query.filter(semester.term == "Fall")
        for obj in fall_objs:
            fall_ids.append(obj.semester_id)
        return fall_ids

    def get_winter_ids(self):
        winter_ids = []
        winter_objs = semester.query.filter(semester.term == "Winter")
        for obj in winter_objs:
            winter_ids.append(obj.semester_id)
        return winter_ids

    def get_spring_ids(self):
        spring_ids = []
        spring_objs = semester.query.filter(semester.term == "Spring")
        for obj in spring_objs:
            spring_ids.append(obj.semester_id)
        return spring_ids

    def get_summer_ids(self):
        summer_ids = []
        summer_objs = semester.query.filter(semester.term == "Summer")
        for obj in summer_objs:
            summer_ids.append(obj.semester_id)
        return summer_ids

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
            if obj.year == curr_year and obj.term == curr_term and not reached_term:
                reached_term = True
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

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    """
    Takes a plan id and searches for all courses in that plan
    Returns: all courses in year order of that plan
    """
    def get_plan_courses(self, find_plan_id):
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
            return course_schema.jsonify(my_course)
        return jsonify({"Failed": "User is not admin"})
    
    return jsonify({"Failed": "User not signed in"}) 


"""
Endpoint for getting all course
"""
@app.route('/admin/courses', methods = ['GET'])
def admin_get_all_courses():
    if "user_email" in session:
        if session["admin"]:
            all_courses = course.query.order_by(course.course_id.asc()).all()
            courses_dump = courses_schema.dump(all_courses)
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
    
            return course_schema.jsonify(new_course)
        
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
            return course_schema.jsonify(updated_course)
        
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
            return course_schema.jsonify(deleted_course)
            
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
            curr_user.update_term_ids()
            session["user_email"] = curr_user.email
            session["admin"] = curr_user.admin
            session["plan_ids"] = curr_user.plan_ids
            session["fall_ids"] = curr_user.fall_ids
            session["winter_ids"] = curr_user.winter_ids
            session["spring_ids"] = curr_user.spring_ids
            session["summer_ids"] = curr_user.summer_ids
            return jsonify({"Success": "Successfully signed in user"})
    elif "user_email" in session or check_user:
        return jsonify({"Failed": "User already signed in"})
    else:
        return jsonify({"Failed": "Failed neccessary fields left empty"})
   
    return "Failed to sign in user"


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


#TODO: Change to use definitions
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
    return jsonify({"Failed": "Failed to update campus id"})


"""
Makes an empty plan for the user
"""
@app.route("/user/plan/make-plan", methods=["PUT"])
def user_make_plan():
    if "user_email" in session:
        curr_user = users(session["user_email"])
        usr_id = curr_user.get_user_id()
        new_plan = plan(usr_id)
        if new_plan:
            new_plan.add_commit()
            session["curr_plan_id"] = new_plan.plan_id
            session["plan_ids"].append(new_plan.plan_id)
            return jsonify({"Success": "Successfully made plan"})
    client.auth.sign_out()
    return jsonify({"Failed": "Failed need to sing in first"})


#TODO: when user selects plan make it the sessions plan
@app.route("/user/plan/select-plan", methods={"POST"})
def user_select_plan():
    if request.method == "POST" and "user_email" in session and "plan_id" in request.json:
        chosen_plan_id = request.json["plan_id"]
        session["curr_plan_id"] = chosen_plan_id
        return jsonify({"Success": "Session current plan updated"})

    elif "user_email" not in session:
        return jsonify({"Failed": "User not signed in"})
    
    elif "plan_id" not in request.json:
        return jsonify({"Failed": "Missing \"plan_id\" field in json"})
    
    else:
        return jsonify({"Failed": "Wrong method used"})


"""
Deletes the users chosen plan
"""
#TODO: Need to complete it
@app.route("/user/plan/delete-plan", methods=["DELETE"])
def user_delete_plan():
    if "user_email" in session and "plan_id" in request.json and request.method == "DELETE":
        chosen_plan_id = request.json["plan_id"]
        curr_user = users(session["user_email"])

        if chosen_plan_id:
            usr_id = curr_user.get_user_id()
            to_delete = plan.query.filter(plan.plan_id == chosen_plan_id, plan.user_id == usr_id).first()
            
            return jsonify({"Success": f"Successfully deleted {to_delete.plan_name}"})
            
        return jsonify({"Failed": "Failed to delete plan"})
        
        return jsonify({"Failed": "No plan id given"})
    
    elif "user_email" not in session:
        client.auth.sign_out()
        return jsonify({"Failed": "User not signed in"})
    
    elif "plan_id" not in request.json:
        return jsonify({"Failed": "Missing \"plan_id\" field in json"})
    
    else:
        return jsonify({"Failed": "User not signed in"})


"""
Adds a course to users plan using taken
"""
#TODO: Go over again to make sure session data works
@app.route("/user/plan/add-course-to-plan", methods=["POST"])
def user_add_to_plan():
    if "user_email" in session:
        if request.method == "POST" and "plan_id" in request.json and "crs_id" in request.json and "req_id" in request.json and "sem_id" in request.json:
            plan_id = request.json["plan_id"]
            crs_id = request.json["crs_id"]
            req_id = request.json["req_id"]
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
                    if in_sem.term == "Fall":
                        session["fall_ids"].append(sem_id)
                    elif in_sem.term == "Winter":
                        session["winter_ids"].append(sem_id)
                    elif in_sem.term == "Spring":
                        session["spring_ids"].append(sem_id)
                    else:
                        session["summer_ids"].append(sem_id)

                    return jsonify({"Success": f"Successfully added {in_course.course_title} to {in_plan.plan_name}"})
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
    return jsonify({"Failed": "User not signed in"})

#TODO: returns all the fall courses in a distionary {2024: [fall_courses],2025: [fall_courses], ...: [...]}
@app.route("/user/plan/get-fall-courses", methods=["GET"])
def get_all_fall():
    pass

@app.route("/user/plan/get-winter-courses", methods=["GET"])
def get_all_winter():
    pass

@app.route("/user/plan/get-spring-courses", methods=["GET"])
def get_all_spring():
    pass

@app.route("/user/plan/get-summer-courses", methods=["GET"])
def get_all_summer():
    pass


@app.route("/user/plan/delete-course-from-plan", methods=["DELETE"])
def user_delete_course(crs_id=None):
    if request.method == "DELETE" and "course_id" in request.json and "curr_plan_id" in session:
        course_id = request.json["course_id"]
        curr_plan_id = session["curr_plan_id"]

        #Checks if correct 
        if course_id:
            in_taken = taken.query.filter(taken.course_id == course_id, taken.plan_id == curr_plan_id).first()
            crs_obj = course.query.filter(course.course_id == in_taken.course_id).first()
            crs_title = crs_obj.course_id
            in_taken.delete()
            return jsonify({"Success": f"Successfully deleted {crs_title}"})
        
    elif crs_id and "curr_plan_id" in session:
        curr_plan_id = session["curr_plan_id"]

        in_taken = taken.query.filter(taken.course_id == crs_id, taken.plan_id == curr_plan_id).first()
        crs_obj = course.query.filter(course.course_id == in_taken.course_id).first()
        crs_title = crs_obj.course_id
        in_taken.delete()
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
    courses_dump = courses_schema.dump(all_courses)
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
def view_plan():
    if request.method == "GET" and "curr_plan_id" in session and "user_email" in session:
        curr_user = users(session["user_email"])
        plan_id = session["curr_plan_id"]
        plans_courses = curr_user.view_plan(plan_id)
        courses_dump = courses_schema.dump(plans_courses)
        return jsonify(courses_dump)
    
    elif "user_email" not in session:
        client.auth.sign_out()
        return jsonify({"Failed": "User not signed in"})
    
    elif "curr_plan_id" not in session:
        return jsonify({"Failed": "No plan in session"})
    
    else:
        return jsonify({"Failed": "Wrong method needs \"GET\" method"})


"""
Get all the plan ids for the current user
To be used in combination with view plan route to view all plans
Return: a list of plan ids
"""
@app.route("/user/plan/get-plan-ids", methods=["GET"])
def get_plan_ids():
    if "user_email" in session:
        num_plans = session["plan_ids"]
        return num_plans
    client.auth.sign_out()
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
