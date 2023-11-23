from flask import Flask, request, session, jsonify
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

app = Flask(__name__)
CORS(app)
app.secret_key = secret_key #Secret key needed for sessions to get the encrypted data
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
app.permanent_session_lifetime = timedelta(hours = 1) #How long the session data will be saved for

db = SQLAlchemy(app)
ma = Marshmallow(app)

FAILED_EMAIL = {"Failed": "Incorrect Email given or missing"}
FAILED_PLAN = {"Failed": "User doesn't have plan"}
FAILED_GET = {"Failed": "Wrong method given expected GET"}
FAILED_POST = {"Failed": "Wrong method given expected POST"}
FAILED_DELETE = {"Failed": "Wrong method given expected DELETE"}
FAILED_PUT = {"Failed": "Wrong method given expected PUT"}
BLACKLIST = [";", "&", "\\", "$", ">", "<", "`", "!", "|", ",", "#", ".", "'"]

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
    max_plans = 10
    max_sem = 32 #Zach Limit
    max_sem_crs = 7 #Brandon Limit
    soft_cap_credits = 18
    hard_cap_credits = 24

    #Makes a user if user given
    def __init__(self, new_email=None, admin=False):
        if new_email:
            self.email = new_email
            self.admin = admin

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()

    def delete_term(self, plan_id, sem_id):
        usr_plan = plan(plan_id)
        pln_courses = usr_plan.get_taken_courses()
        to_delete = []
        sem = semester.query.get(sem_id)
        term = sem.term

        for obj in pln_courses:
            if obj.semester_id == sem_id:
                to_delete.append(obj)

        if to_delete:
            for crs in to_delete:
                crs.delete_commit()
            return {"Success": f"{term} term deleted"}
        
        else:
            return {"Failed": "Semester not found"}

    def get_user_id(self):
        pub_usr = public_user_info()
        usr_id = pub_usr.get_user_id(self.email)
        return usr_id
    
    def update_campus_id(self, new_c_id):
        pub_user = public_user_info()
        result = pub_user.update_campus_id(new_c_id, self.email)
        return result

    def user_make_plan(self):
        user_plans = self.get_plans()
        if len(user_plans) < self.max_plans:
            user_id = self.get_user_id()
            new_plan = plan()
            result = new_plan.make_plan(user_id)
            if result:
                new_plan.add_commit()
                return {"Success": "Plan added successfully"}
            
            return {"Failed": "Error adding plan"}
        
        return {"Failed": "User has reached plan limit"}

    #TODO: Have it check for credits instead
    def add_course(self, plan_id, crs_id, req_id, sem_id, grade):
        in_plan = plan.query.filter(plan.plan_id == plan_id).order_by(plan.plan_id.desc()).first()
        in_course = course.query.filter(course.course_id == crs_id).order_by(course.course_id.desc()).first()
        in_req = requirement.query.filter(requirement.requirement_id == req_id).order_by(requirement.requirement_id.desc()).first()
        in_sem = semester.query.filter(semester.semester_id == sem_id).order_by(semester.semester_id.desc()).first()

        crs_in_taken = taken.query.filter(taken.plan_id == plan_id, taken.course_id == crs_id).order_by(taken.course_id.desc()).first()

        if in_plan and in_course and in_req and in_sem:
            
            usr_plan = plan(plan_id)
            pln_courses = usr_plan.get_taken_courses()
            pln_semesters = set()
            num_sem_courses = 0

            for obj in pln_courses:
                pln_semesters.add(obj.semester_id)
                if obj.semester_id == sem_id:
                    num_sem_courses += 1
            num_sem = len(pln_semesters)

            if num_sem_courses < self.max_sem_crs and num_sem <= self.max_sem:
                add_to_plan = taken()
                add_to_plan.add_course(plan_id, crs_id, req_id, sem_id, grade)
                add_to_plan.add_commit()
                return {"Success": f"Added {in_course.course_title} to {in_plan.plan_name} for {in_sem.term}"}
        
            elif num_sem_courses >= self.max_sem_crs:
                return {"Failed": "User has reached the course limit"}
            
            elif crs_in_taken:
                return {"Failed": "Course already in chosen plan"}
        
            else:
                return {"Failed": "User has reached the semester limit"}

        elif not in_plan:
            return {"Failed": "Failed Plan id not in database"}
        elif not in_course:
            return {"Failed": "Failed Course id not in database"}
        elif not in_req:
            return {"Failed": "Failed Requirement id not in database"}
        else:
            return {"Failed": "Failed Semester id not in database"}

    #Gets the course objects of a users plan
    def get_pln_courses(self, plan_id):
        usr_plan = plan(plan_id)
        usr_courses = usr_plan.get_courses()
        return usr_courses

    #User views all of their plans
    def get_plans(self):
        user_id = self.get_user_id()
        plan_objs = plan.query.filter(plan.user_id == user_id)
        usr_plans = []
        
        if plan_objs:
            #gets the list of plan objects <plan id>
            for obj in plan_objs:
                usr_plans.append(obj)
            return usr_plans
        
        return None
    
    def user_has_plan(self, plan_id):
        user_plans = self.get_plans()
        usr_has = False
        for obj in user_plans:
            if plan_id == obj.plan_id:
                usr_has = True
        return usr_has

    def get_term_courses(self, plan_id, term):
        usr_plan = plan(plan_id)
        taken_courses = usr_plan.get_taken_courses()
        sem = semester()

        if term == "Fall":
            usr_fall = []

            fall_sems = sem.get_fall_objs()
            for t_crs in taken_courses:
                for sem_obj in fall_sems:
                    if t_crs.semester_id == sem_obj.semester_id:
                        usr_fall.append(t_crs)

            return usr_fall

        elif term == "Winter":
            usr_winter = []

            winter_sems = sem.get_winter_objs()
            for t_crs in taken_courses:
                for sem_obj in winter_sems:
                    if t_crs.semester_id == sem_obj.semester_id:
                        usr_winter.append(t_crs)

            return usr_winter

        elif term == "Spring":
            usr_spring = []

            spring_sems = sem.get_spring_objs()
            for t_crs in taken_courses:
                for sem_obj in spring_sems:
                    if t_crs.semester_id == sem_obj.semester_id:
                        usr_spring.append(t_crs)

            return usr_spring

        elif term == "Summer":
            usr_summer = []

            summer_sems = sem.get_summer_objs()
            for t_crs in taken_courses:
                for sem_obj in summer_sems:
                    if t_crs.semester_id == sem_obj.semester_id:
                        usr_summer.append(t_crs)

            return usr_summer
        
        else:
            return None

    """
    Adds courses to the users plan dictionary
    Inputs: list of years, dictionary of users plan, schema dump of plan additions
    Returns: A dictionary of years with a dictionary of term keys for a list of courses
    ex. { 2023: {"Fall": [crs1, crs2]}, ... }
    """
    def to_dict(self, years, usr_plan, dump):
        for year in years:
            if year not in usr_plan:
                usr_plan[year] = {}
            for dump_obj in dump:
                obj_year = dump_obj.get('year')
                if obj_year == year:
                    crs_id = dump_obj.get('course_id')
                    crs = course()
                    obj_crs = crs.get_course(crs_id)
                    if dump_obj.get('term') in usr_plan[year]:
                        usr_crs = user_course_schema.dump(obj_crs)
                        usr_plan[year][dump_obj.get('term')].append(usr_crs)
                    else:
                        usr_plan[year][dump_obj.get('term')] = []
                        usr_crs = user_course_schema.dump(obj_crs)
                        usr_plan[year][dump_obj.get('term')].append(usr_crs)
        return usr_plan


class public_user_info(db.Model):
    public_user_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)
    email = db.Column(db.String)
    campus_id = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_user_id(self, email):
        user = public_user_info.query.filter(public_user_info.email == email).first()
        user_id = user.user_id
        return user_id
    
    def get_all_users():
        all_users = public_user_info.query.all()
        users_list = []
        for obj in all_users:
            users_list.append(obj)
        
        return users_list

    def update_campus_id(self, new_c_id, email):
        user = public_user_info.query.filter(public_user_info.email == email).first()
        if user:
            user.campus_id = new_c_id
            db.session.commit()
            return {"Success": "Updated Campus ID"}
        else:  
            return {"Failed": "Failed to Update Campus ID"}

    def update_name(self,email, new_f_name=None, new_l_name=None):
        user = public_user_info.query.filter(public_user_info.email == email).first()

        if user and new_f_name and new_l_name:
            user.first_name = new_f_name
            user.last_name = new_l_name
            db.session.commit()
            return True
        
        elif user and new_f_name and not new_l_name:
            user.first_name = new_f_name
            db.session.commit()
            return True
        
        elif user and not new_f_name and new_l_name:
            user.last_name = new_l_name
            db.session.commit()
            return True
        
        else:
            return False

# Defines your user output
class PublicUserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("user_id", "email", "campus_id", "first_name","last_name")

public_user_schema = PublicUserSchema()
public_users_schema = PublicUserSchema(many=True)


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
    plan_limit = 10

    def __init__(self, new_plan_id=None):
        if new_plan_id:
            self.plan_id = new_plan_id

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()

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
            return True
        return False

    def get_plan_name(self):
        plan_name = plan.query.filter(plan.plan_id == self.plan_id).order_by(plan.plan_name).first()
        return plan_name.plan_name

    def rename_plan(self, usr_id, new_name):
        bad_input = False
        for char in new_name:
            if char in BLACKLIST:
                bad_input =True
        
        if bad_input:
            return {"Failed": "A Blacklisted charachter was input"}

        usr_plan = plan.query.filter(plan.user_id == usr_id, plan.plan_id == self.plan_id).first()
        if usr_plan:
            usr_plan.plan_name = new_name
            usr_plan.add_commit()
            return {"Success": f"Plan nam changed to {new_name}"}
        else:
            return {"Failed": "User doesn't have that plan"}


    """"
    Views current plan
    Gets users plan by going through taken
    makes a list of all the courses that match plan id
    returns the list of courses from taken table if their is a plan
    returns None if no plan
    """
    def get_taken_courses(self):
        taken_plan_objs = taken.query.filter(self.plan_id == taken.plan_id)
        taken_list = []

        if taken_plan_objs:
            for obj in taken_plan_objs:
                taken_list.append(obj)
            return taken_list
        
        return None
    
    """
    View the course objects of the current plan
    returns the list of courses from the course table if plan exists
    returns None if no plan
    """
    def get_courses(self):
        taken_crs_ids = []
        taken_plan_objs = self.get_taken_courses()

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

    def get_years(self, term=None):
        plan_years = set()
        taken_plan_objs = taken.query.filter(self.plan_id == taken.plan_id)
        taken_dump = taken_courses_schema.dump(taken_plan_objs)
        if term == None:
            for obj in taken_dump:
                obj_year = obj.get('year')
                if obj_year:
                    plan_years.add(obj_year)
            if plan_years:
                plan_years = sorted(plan_years)

        else:
            for obj in taken_dump:
                obj_year = obj.get('year')
                obj_term = obj.get("term")
                if obj_year and obj_term == term:
                    plan_years.add(obj_year)
            if plan_years:
                plan_years = sorted(plan_years)

        return plan_years


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

# Defines your degree output
class DegreeSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("degree_id", "deg_name", "deg_type")

degree_schema = DegreeSchema()
degrees_schema = DegreeSchema(many=True)


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

# Defines your prereq output
class PrereqSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("prereq_id","crs_id", "prereq_courses", "grade_required")

prereq_schema = PrereqSchema()
prereqs_schema = PrereqSchema(many=True)
    

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

    def get_course(self, crs_id):
        crs = course.query.get(crs_id)
        return crs

    def add_prereq(self, req):
        self.prereq = req
        db.session.commit()

    def get_courses_offered(self, sem_id):
        stmt = db.select(self.crs_offered).where(
            db.and_(
                self.crs_offered.c.course_id != None, self.crs_offered.c.semester_id == sem_id
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

user_course_schema = UserCourseSchema()
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

# Defines your subject output
class SubjectSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("subject_id", "subject_code", "subject_name")

subject_schema = SubjectSchema()
subjects_schema = SubjectSchema(many=True)


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

    def __init__(self, sem_id=None, year=None, term=None):
        if sem_id:
            sem = semester.query.get(sem_id)
            if sem:
                self.term = sem.term
                self.year = sem.year
        elif year and term:
            sem_obj = semester.query.filter(semester.term == term, semester.year == year).first()
            if sem_obj:
                self.semester_id = sem_obj.semester_id
                self.term = term
                self.year = year

    def add_semester(self, term, year):
        last_id = semester.query.order_by(semester.semester_id.desc()).first()

        if last_id:
            self.semester_id = last_id.semester_id + 1
        else:
                self.semester_id = 1

        self.term = term
        self.year = year
        self.add_commit()

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
    def get_fall_objs(self, curr=True):
        if not curr:
            fall_objs = []
            current = True
            semesters = self.get_year_order_objs(current)
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

    def get_winter_objs(self, curr=True):
        if not curr:
            winter_objs = []
            current = True
            semesters = self.get_year_order_objs(current)
            for sem in semesters:
                if sem.term == "Winter":
                    winter_objs.append(sem)
            return winter_objs
        else:
            winter_objs = []
            semesters = self.get_year_order_objs()
            for sem in semesters:
                if sem.term == "Winter":
                    winter_objs.append(sem)
            return winter_objs

    def get_spring_objs(self, curr=True):
        if not curr:
            spring_objs = []
            current = True
            semesters = self.get_year_order_objs(current)
            for sem in semesters:
                if sem.term == "Spring":
                    spring_objs.append(sem)
            return spring_objs
        else:
            spring_objs = []
            semesters = self.get_year_order_objs()
            for sem in semesters:
                if sem.term == "Spring":
                    spring_objs.append(sem)
            return spring_objs

    def get_summer_objs(self, curr=True):
        if not curr:
            summer_objs = []
            current = True
            semesters = self.get_year_order_objs(current)
            for sem in semesters:
                if sem.term == "Summer":
                    summer_objs.append(sem)
            return summer_objs
        else:
            summer_objs = []
            semesters = self.get_year_order_objs()
            for sem in semesters:
                if sem.term == "Summer":
                    summer_objs.append(sem)
            return summer_objs

    """
    Gets relevant semesters based on current year and approximate term
    Gets all semesters before current year
    Used for checking if a course will be offered
    """
    def get_year_order_objs(self, old = False):
        self.update_year_term()
        curr_year = self.current_year
        curr_term = self.current_term
        all_semesters = semester.query.all()
        order_objs = []
        
        if not old:
            reached_term = False
            for obj in all_semesters:
                if reached_term:
                    order_objs.append(obj)
                    self.last_year = obj.year
                elif obj.year == curr_year and obj.term == curr_term and not reached_term:
                    reached_term = True
                    order_objs.append(obj)
                    self.last_year = obj.year
        else:
            before_term = True
            for obj in all_semesters:
                if before_term:
                    order_objs.append(obj)
                elif obj.year == curr_year and obj.term == curr_term and not before_term:
                    before_term = False
                    order_objs.append(obj)

        return order_objs   

    def get_past_courses_ids(self):
        all_fall_objs = self.get_fall_objs(False)
        crs = course()
        fall_courses = {}

        for sem in all_fall_objs:
            courses = crs.get_courses_offered(sem.semester_id)
            if courses:
                fall_courses[sem.year] = []
            for offr_id, crs_id, sem_id, freq in courses:
                if sem_id == sem.semester_id:
                    fall_courses[sem.year].append(crs_id)

        return fall_courses


class SemesterSchema(ma.Schema):
    class Meta:
        fields = ("semester_id", "term", "year")

semester_schema = SemesterSchema()
semesters_schema = SemesterSchema(many = True)


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

class TakenSchema(ma.Schema):
    subject_code = fields.Function(lambda obj: obj.subject.sub_code if obj.subject else None)
    class Meta:
        fields = ("taken_id", "plan_id", "course_id", "requirement_id", "semester_id", "grade")

taken_schema = TakenSchema()
takens_schema = TakenSchema(many = True)

class TakenCourseSchema(ma.Schema):
    course_title = fields.Function(lambda obj: obj.course.course_title if obj.course else None)
    year = fields.Function(lambda obj: obj.semester.year if obj.semester else None)
    term = fields.Function(lambda obj: obj.semester.term if obj.semester else None)

    class Meta:
        fields = ("taken_id", "course_id", "course_title", "semester_id", "year", "term")

taken_course_schema = TakenCourseSchema()
taken_courses_schema = TakenCourseSchema(many = True)

