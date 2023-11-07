"""
Authors: Amir Hawkins-Stewart & Zach Margulies

Description: Makes objects of the databse tables, sends and recieves data from the supabase databse.

TODO: Finish the classes, app.routes to send and receive from site 
"""
import secret_keys
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from flask_marshmallow import Marshmallow
from supabase import Client #import supabase.py not supabase
from datetime import timedelta, datetime
import time

url = "https://qwydklzwvbrgvdomhxjb.supabase.co"
client = Client(url, secret_keys.client_key)
client_admin = Client(url, secret_keys.secret_key)

app = Flask(__name__)
app.secret_key = secrets.secret_key #Secret key needed for sessions to get the encrypted data
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
app.permanent_session_lifetime = timedelta(minutes = 10) #How long the session data will be saved for

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
    admin = False

    #Makes a user from the session if user given
    def __init__(self, user=None):
        if user:
            self.user_obj = user
            self.admin = user.user.app_metadata.get('admin')

    #Signs up a new user
    def signup(self, email, password, admin=False):
        max_retries = 3
        retry_count = 0

        #Tries 3 times to signup a user and prints the error for each failure in 10sec intervals
        while retry_count < max_retries:
            try:
                in_public = public_user_info.query.filter(email == public_user_info.email).first()

                #If user not in session signs them up and fills class variables
                if not in_public:
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
    email = db.Column(db.String, primary_key=True)
    campus_id = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    def __init__(self, new_email=None, new_campus_id=None, new_f_name=None, new_l_name=None):
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

    def get_user_id(self):
        usr_obj = client_admin.auth.get_user(self.email == "email")
        usr_id = usr_obj.user.id
        return usr_id
    
    def get_user(email):
        user = public_user_info.query.filter("email" == email).first()
        return user
    
    def get_all_users():
        all_users = public_user_info.query.all()
        return all_users

    def update_campus_id(self, email, new_c_id):
        pass

    def update_name(self, email, new_f_name=None, new_l_name=None):
        pass

    def update_email(self, email=None):
        pass
    
    
    """"
    User views current plan
    Gets users plan 
    uses plan id to go through taken
    makes a list of all the courses that match plan id
    returns the list if their is a plan
    returns None if no plans
    """
    def view_plan(self, plan_id):
        crs_ids_in_plan = []
        courses_in_plan = taken.query.filter(plan_id == taken.plan_id).order_by(taken.course_id)
        if courses_in_plan:
            for crs in courses_in_plan:
                crs_ids_in_plan.append(crs.course_id)

            crs_in_plan = []
            for crs in crs_ids_in_plan:
                crs_title = course.query.filter(crs == course.course_id).order_by(course.course_title).first()
                crs_in_plan.append(crs_title)

            crs_titles = []
            for crs in crs_in_plan:
                title = crs.course_title
                crs_titles.append(title)
            return crs_titles
        return None

    #User views all of their plans
    def get_plans(self, usr_id):
        plan_ids = plan.query.filter(plan.user_id == usr_id).order_by(plan.plan_id.desc())
        return plan_ids

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
class AdminCourseSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("course_id", "subject_id", "course_title","course_num","credits")

admin_course_schema = AdminCourseSchema()
admin_courses_schema = AdminCourseSchema(many=True)

"""
Defines course output for Users
"""
class UserCourseSchema(ma.Schema):
    subject_code = fields.Function(lambda obj: obj.subject.sub_code if obj.subject else None)
    class Meta:
        fields = ("subject_code", "course_title", "course_num", "credits")

view_schema = UserCourseSchema(many = True)

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

    def __init__(self, term, year):
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
Takes the planned course and assigns it to the plan with the semester of the plan and the chosen requirement type from the course
Columns:
taken_id (PrimaryKey) - Unique id of taken in database
plan_id (ForeignKey) - Unique id of the plan in database
course_id (ForeignKey) - Unique id of the course in database
requirement_id (ForeignKey) - Unique id of the requirement in database
semester_id (ForeignKey) - Unique id of the semester in database
grade - A courses grade is used to check if a course is taken or not
"""
#TODO: add def requirment_choice to check if course can be taken
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
Flask Routes
"""
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


"""
Endpoint for getting one courses
"""
@app.route('/admin/courses/<course_id>', methods = ['GET'])
def admin_get_course(course_id):
    user = session["user_email"]
    if user.user.app_metadata['admin']:
        my_course = course.query.get(course_id)
        return admin_course_schema.jsonify(my_course)
    return jsonify({"failed": "User is not admin"}) 


"""
Endpoint for getting all course
"""
@app.route('/admin/courses', methods = ['GET'])
def admin_get_all_courses():
    all_courses = course.query.order_by(course.course_id.asc()).all()
    courses_dump = admin_courses_schema.dump(all_courses)
    return jsonify(courses_dump)


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
    
    return jsonify ({"success": "Success Post"}) 


"""
Signs up the user
Inputs:
email - New users email
password - New users password
"""
@app.route("/user/signup", methods=["POST"])
def user_signup():
    email = request.form["email"]
    password = request.form["password"]

    if email and password:
        cur_user = users()
        result = cur_user.signup(email, password)
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
@app.route("/user/signin", methods=["POST"])
def user_signin():
    email = None 
    password = None

    email = request.form["email"]
    password = request.form["password"]
    
    check_user = client.auth.get_user()

    if email and password and "user_email" not in session and not check_user:
        curr_user = users()
        in_auth = curr_user.signin(email, password)
        if in_auth:
            session["user_email"] = curr_user.user_obj.user.email
            return "Successfully signed in user"
    elif "user_email" in session:
        return "User already in session signed in"
    elif check_user:
        return("User already signed in")
    else:
        return "Failed neccessary fields left empty"
   
    return "Failed to sign in user"

"""
Signs out user from supabase and removes them from the session
"""
@app.route("/user/signout", methods=["GET"])
def user_signout():
    is_user = client.auth.get_user()
    if is_user:
        user_email = is_user.user.email
        client.auth.sign_out()
        session.pop("user_email")
        return f"Succesfully signed out {user_email}"
    if "user_email" in session:
        session.pop("user_email")
    
    return "Failed no user signed in"


@app.route("/user/update-campus-id", methods=["POST", "GET"])
def update_campus_id():
    user = client.auth.get_user()
    if user:
        new_c_id = request.form["campus_id"]
        usr_email = user.user["email"]
        curr_user = public_user_info()
        curr_user.update_campus_id(usr_email, new_c_id)
        curr_user.add_commit()
        return "Successful campus id change"
    return "Failed to update campus id"

"""
Makes an empty plan for the user
"""
@app.route("/user/plan/make-plan", methods=["POST", "GET"])
def user_make_plan():
    user = client.auth.get_user()
    if user:
        usr_id = user.user.id
        new_plan = plan(usr_id)
        if new_plan:
            new_plan.add_commit()
            return "Successfully made plan"
    return "Failed need to sing in first"


"""
Deletes the users chosen plan
"""
#TODO: Complete it when supabase emails working
@app.route("/user/plan/delete-plan", methods=["POST", "PUT"])
def user_delete_plan():
    chosen_id = request.json["chosen_id"]
    user = client.auth.get_user()
    print("USER ", user)
    if "user_email" in session:
        print("SESSION ", session["user_email"])
    if user:
        if chosen_id:
            to_delete = plan.query.filter(plan.plan_id == chosen_id).order_by().first()
            print("TO DELETE ", to_delete)
            print("TO DELETE ID", to_delete.user_id)
            print("USER ID     ", user.user.id)
            #TODO:When supabase email working again Add-> or user.user.admin:
            del_id = to_delete.user_id
            usr_id = user.user.id
            if del_id == usr_id:
                chosen_pl_num = to_delete.plan_num
                to_delete.delete()
                return f"Successfully deleted {chosen_pl_num}"
        return "Failed to delete plan"
    return "User not signed in"


"""
Adds a course to users plan using taken
"""
@app.route("/user/plan/add-course-to-plan", methods=["POST", "PUT"])
def user_add_to_plan():
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

        crs_in_taken = taken.query.filter(taken.plan_id == plan_id).order_by(taken.course_id.desc()).first()

        if in_plan and in_course and in_req and in_sem and not crs_in_taken:
            add_to_plan = taken()
            add_to_plan.add_course(plan_id, crs_id, req_id, sem_id, grade)
            add_to_plan.add_commit()
            return "Successfully added planned course"
        elif crs_in_taken:
            return "Course already in chosen plan"
        elif not in_plan:
            return "Failed Plan id not in database"
        elif not in_course:
            return "Failed Course id not in database"
        elif not in_req:
            return "Failed Requirement id not in database"
        else:
            return "Failed Semester id not in database"
    
    return "Failed a necessary field(s) left empty"


"""
Returns all the courses in the database for a user to see
"""
@app.route("/user/view-all-courses", methods=["GET"])
def user_view_all_courses():
    all_courses = course.query.all()
    courses_dump = view_schema.dump(all_courses)
    return jsonify(courses_dump)

@app.route("/view-all-courses", methods=["GET"])
def test_view_all_courses():
    courses = course.query.all()
    result = []

    for crs in courses:
        subj_code = crs.subject.sub_code
        result.append({
            'subject_code': subj_code,
            'course_number': crs.course_num,
            'course_title': crs.course_title ,
            'credits': crs.credits
        })

    return jsonify(result)

"""
Chooses a plan to view
Gets user from session
Views the current users chosen plan
"""
@app.route("/user/view-plan", methods=["POST", "GET"])
def view_plan():
    plan_id = request.form["plan_id"]
    if "user" in session:
        curr_user = session["user"]
        plan = public_user_info()
        plans_courses = plan.view_plan(plan_id)
        return jsonify(plans_courses)
    return jsonify({"failed": "User not signed in"})


@app.route("/user/view-all-plans", methods=["GET"])
def view_all_plans():
    if "user" in session:
        usr = session["user"]
        print("SESSION USR", usr)
        pub_usr = public_user_info(usr)
        print("PUB USR", pub_usr.email)
        usr_id = pub_usr.get_user_id()
        print("USR_ID ", usr_id)
        usr_plan_ids = pub_usr.get_plans(usr_id)
        for plan in usr_plan_ids:
            print("PLAN", plan)
            plans_courses = pub_usr.view_plan(plan.plan_id)
        return jsonify(plans_courses)
    return jsonify({"failed": "User not signed in"})


"""
Used to update any current users data
"""
def update_all_users():
    all_users = public_user_info.get_all_users()
    su = client_admin.auth.admin.list_users()
    for user in su:
        update_data = {
            'app_metadata':{
                'admin': False
            }
        }
        client_admin.auth.admin.update_user_by_id(user.id, update_data)


"""
Adds the auth table supabase user to the public table
"""
@app.route("/dev/add-to-public", methods=["POST"])
def add_to_public(new_email=None, campus_id=None, f_name=None, l_name=None):
    email = request.json["email"]
    in_table = public_user_info.query.filter(email == public_user_info.email).first()
    if not in_table:
        new_user = public_user_info(email)
        new_user.add_commit()
        return jsonify ({"success": "Added to public user table"})
    return jsonify ({"failed": "Email already in table"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
