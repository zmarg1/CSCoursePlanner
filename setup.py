"""
Author: Amir Hawkins-Stewart

Description: Contains the impoprts, constant variables, and functions used to run the app. Has the functions to interact with the Supabase tables.
"""

from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
from marshmallow import fields
from flask_marshmallow import Marshmallow
from supabase import Client
import datetime
from datetime import timedelta, datetime

client_key ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTU0MDcxNjcsImV4cCI6MjAxMDk4MzE2N30.UNZJCMI1NxpSyFr8bBooIIGPqTbDe3N-_YV9ZHbE_1g"
secret_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5NTQwNzE2NywiZXhwIjoyMDEwOTgzMTY3fQ.5IP6Kh6jI3mL_3poMSKcjE_cANIjhqvGHJVjK5RNVMw"
url = "https://qwydklzwvbrgvdomhxjb.supabase.co"
client = Client(url, client_key)

clerk_api_key = 'sk_test_8Fvp5UH4vZplPHK24IdPQXnFqMipUQGYN7WmkomiHG'

app = Flask(__name__)
CORS(app)
app.secret_key = secret_key #Secret key needed for sessions to get the encrypted data
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres'
app.permanent_session_lifetime = timedelta(hours = 1) #How long the session data will be saved for

db = SQLAlchemy(app)
ma = Marshmallow(app)

FAILED_EMAIL = {"status": "Failed", "reason": "Incorrect Email given or missing"}
FAILED_PLAN_ID = {"status": "Failed", "reason": "Plan ID missing"}
FAILED_SEM_ID = {"status": "Failed", "reason": "Semester ID missing"}
FAILED_CRS_ID = {"status": "Failed", "reason": "Course ID missing"}
FAILED_PLAN = {"status": "Failed", "reason": "User doesn't have plan"}
FAILED_GET = {"status": "Failed", "reason": "Wrong method given expected GET"}
FAILED_POST = {"status": "Failed", "reason": "Wrong method given expected POST"}
FAILED_DELETE = {"status": "Failed", "reason": "Wrong method given expected DELETE"}
FAILED_PUT = {"status": "Failed", "reason": "Wrong method given expected PUT"}
BLACKLIST = [";", "&", "\\", "$", ">", "<", "`", "!", "|", ",", "#", ".", "'", "/", "+", "\""]
FAILED_BLACKLIST = {"status": "Failed", "reason": "A Blacklisted charachter was input"}

"""
Check user input to make sure its valid
"""
def check_user_input(usr_input):
    valid = True
    for char in usr_input:
        if char in BLACKLIST:
            valid = False
    
    return valid

"""
The user object class to interact with the authorization table in supabase
user_obj - Stores the created supabase 'user' object
admin - The users permission level
campus_id - The campus id of the given user
"""
class users():
    email = None
    admin = False
    max_plans = 10
    zach_limit = 32 #max semesters
    brandon_limit = 7 #max courses
    soft_cap_credits = 18
    hard_cap_credits = 24 #to be implemented if we take this furthur

    #Makes a user if user given
    def __init__(self, new_email=None, admin=False, user_id=None):
        if new_email:
            self.email = new_email
            self.admin = admin
        if user_id:
            pub_user = public_user_info()
            response = pub_user.get_user_email(user_id)
            if response['status'] == 'Success':
                self.email = response['user_email']
            self.admin = admin


    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_user_data(self):
        try:
            plans = self.get_plans()
            
            if plans:
                for usr_plan in plans:
                    pln = plan.query.get(usr_plan.plan_id)
                    pln.delete_commit()

            usr_id = self.get_user_id()
            
            pub_usr = public_user_info.query.filter(public_user_info.user_id == usr_id).first()
            pub_usr.delete_commit()

            return {"status": "Success", "result": "User deleted"}
    
        except Exception as e:
            return {"Error": e}

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
        response = pub_usr.get_user_id(self.email)

        if response['status'] == 'Success':
            return response['user_id']
        else:
            return None
    
    def update_campus_id(self, new_c_id):
        pub_user = public_user_info()

        valid = True
        for char in new_c_id:
            if char in BLACKLIST:
                valid = False

        if not valid:
            return FAILED_BLACKLIST
        
        result = pub_user.update_campus_id(new_c_id, self.email)
        return result
            
    def user_make_plan(self, pln_name=None):
        user_plans = self.get_plans()

        if len(user_plans) < self.max_plans:
            user_id = self.get_user_id()
            new_plan = plan()

            if pln_name:
                result = new_plan.make_plan(user_id, pln_name)
            else:
                result = new_plan.make_plan(user_id)

            if result:
                new_plan.add_commit()
                return {"status": "Success", "result": f"{result}"}
            
            return {"status": "Failed", "result": "Error adding plan"}
        
        return {"status": "Failed", "result": "User has reached plan limit"}

    #TODO: Have it check for credits instead
    def add_course(self, plan_id, crs_id, req_id, sem_id, grade):
        in_plan = plan.query.filter(plan.plan_id == plan_id).order_by(plan.plan_id.desc()).first()
        in_course = course.query.filter(course.course_id == crs_id).order_by(course.course_id.desc()).first()
        in_req = requirement.query.filter(requirement.requirement_id == req_id).order_by(requirement.requirement_id.desc()).first()
        in_sem = semester.query.filter(semester.semester_id == sem_id).order_by(semester.semester_id.desc()).first()

        crs_in_taken = taken.query.filter(taken.plan_id == plan_id, taken.course_id == crs_id).order_by(taken.course_id.desc()).first()

        if in_plan and in_course and in_req and in_sem:
            crs = course()
            geps = crs.get_gep_ids()
            exception_titles = ["CMSC Elective", "Spec Topics In Comp Sci"]
            
            usr_plan = plan(plan_id)
            pln_courses = usr_plan.get_taken_courses()
            pln_semesters = set()
            num_sem_courses = 0

            for obj in pln_courses:
                pln_semesters.add(obj.semester_id)
                if obj.semester_id == sem_id:
                    num_sem_courses += 1
            num_sem = len(pln_semesters)

            if num_sem_courses < self.brandon_limit and num_sem <= self.zach_limit and (not crs_in_taken or crs_id in geps or in_course.course_title in exception_titles):
                add_to_plan = taken()
                add_to_plan.add_course(plan_id, crs_id, req_id, sem_id, grade)
                add_to_plan.add_commit()
                return {"status": "Success", "result": f"Added {in_course.course_title} to {in_plan.plan_name} for {in_sem.term} {in_sem.year}"}
        
            elif num_sem_courses >= self.brandon_limit:
                return {"status": "Failed", "result": "User has reached the course limit for this Semester"}
            
            elif crs_in_taken:
                return {"status": "Failed", "result": "Course already in chosen plan"}
        
            else:
                return {"status": "Failed", "result": "User has reached the semester limit"}

        elif not in_plan:
            return {"status": "Failed", "result": "Failed Plan id not in database"}
        elif not in_course:
            return {"status": "Failed", "result": "Failed Course id not in database"}
        elif not in_req:
            return {"status": "Failed", "result": "Failed Requirement id not in database"}
        else:
            return {"status": "Failed", "result": "Failed Semester id not in database"}

    #Gets the course objects of a users plan
    def get_pln_courses(self, plan_id):
        usr_plan = plan(plan_id)
        usr_courses = usr_plan.get_courses()
        return usr_courses

    #Gets a list of plan objects
    def get_plans(self):
        user_id = self.get_user_id()
        plan_objs = plan.query.filter(plan.user_id == user_id)
        usr_plans = []
        
        if plan_objs:
            #Transfers query into a list
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

    #Gets all the Users courses for the matching Term: Fall, Summer, Spring, Winter
    def get_all_terms_courses(self, plan_id, term):
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

    #Gets all users courses for the matching Semester ID to match year and term
    def get_term_courses(self, plan_id, sem_id):
        usr_plan = plan(plan_id)
        taken_courses = usr_plan.get_taken_courses()
        sem = semester(sem_id)

        if sem.term == "Fall":
            usr_fall = []

            fall_sems = sem.get_fall_objs()
            for t_crs in taken_courses:
                for sem_obj in fall_sems:
                    if t_crs.semester_id == sem_obj.semester_id and t_crs.semester_id == sem_id:
                        usr_fall.append(t_crs)

            return usr_fall

        elif sem.term == "Winter":
            usr_winter = []

            winter_sems = sem.get_winter_objs()
            for t_crs in taken_courses:
                for sem_obj in winter_sems:
                    if t_crs.semester_id == sem_obj.semester_id and t_crs.semester_id == sem_id:
                        usr_winter.append(t_crs)

            return usr_winter

        elif sem.term == "Spring":
            usr_spring = []

            spring_sems = sem.get_spring_objs()
            for t_crs in taken_courses:
                for sem_obj in spring_sems:
                    if t_crs.semester_id == sem_obj.semester_id and t_crs.semester_id == sem_id:
                        usr_spring.append(t_crs)

            return usr_spring

        elif sem.term == "Summer":
            usr_summer = []

            summer_sems = sem.get_summer_objs()
            for t_crs in taken_courses:
                for sem_obj in summer_sems:
                    if t_crs.semester_id == sem_obj.semester_id and t_crs.semester_id == sem_id:
                        usr_summer.append(t_crs)

            return usr_summer
        
        else:
            return None

    #Views courses that user hasn't taken and relevant to term
    def view_courses(self, plan_id, sem_id):
        term_courses = self.get_offered_courses(sem_id)
        user_plan = self.get_pln_courses(plan_id)
        not_taken = True
        view_courses = []

        if user_plan:
            crs = course()
            geps = crs.get_gep_ids()
            exception_titles = ["CMSC Elective", "Spec Topics In Comp Sci"]

            #Iterates through all available courses
            for crs in term_courses:
                not_taken = True

                #Iterates through all users taken courses
                for taken_crs in user_plan:
                    if crs.course_id == taken_crs.course_id and crs.course_id not in geps and crs.course_title not in exception_titles:
                        not_taken = False
                        break

                if not_taken:
                    view_courses.append(crs)
        
        else:
            view_courses = term_courses

        return view_courses
    
    #Gets all courses offered for a term given a semester id
    def get_offered_courses(self, sem_id):
        sem = semester(sem_id)
        past = True

        if sem.term == "Fall":
            sem_objs = sem.get_fall_objs(past)
        elif sem.term == "Winter":
            sem_objs = sem.get_winter_objs(past)
        elif sem.term == "Spring":
            sem_objs = sem.get_spring_objs(past)
        else:
            sem_objs = sem.get_summer_objs(past)

        crs = course()
        term_course_ids = set()

        for obj in sem_objs:
            offered = crs.get_courses_offered(obj.semester_id)
            for offer in offered:
                term_course_ids.add(offer.course_id)

        #Get Non CMSC subject course ids
        ignore_cmsc = 1
        courses = course.query.all()

        for crs in courses:
            if crs.subject_id != ignore_cmsc:
                term_course_ids.add(crs.course_id)
        
        term_crs_objs = []
        for crs_id in term_course_ids:
            term_crs_objs.append(crs.get_course(crs_id))

        return term_crs_objs

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

    def __init__(self, n_user_id=None, n_email=None):
        if n_user_id and n_email:
            self.user_id = n_user_id
            self.email = n_email

    def check_user(user_id):
        user = public_user_info.query.filter(public_user_info.user_id == user_id).first()

        if user:
            return {'status': 'Success'}
        else:
            return {'status': 'Failed'}

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()
    
    def get_user_id(self, email=None):
        if email:
            user = public_user_info.query.filter(public_user_info.email == email).first()
        else:
            user = public_user_info.query.filter(public_user_info.email == self.email).first()

        try:
            user_id = user.user_id

        except Exception as e:
            print("ERROR getting user ID: ", e)
            err = {'status': "Failed", 'message': e}
            return err
        
        return {'status': 'Success', 'user_id': user_id}
    
    def get_user_email(self, user_id):
        user = public_user_info.query.filter(public_user_info.user_id == user_id).first()
        try:
            user_email = user.email

        except Exception as e:
            print("ERROR getting user Email: ", e)
            err = {'status': "Failed", 'message': e}
            return err
        
        return {'status': 'Success', 'user_email': user_email}


    def update_campus_id(self, new_c_id, email):
        user = public_user_info.query.filter(public_user_info.email == email).first()
        if user:
            user.campus_id = new_c_id
            db.session.commit()
            return {"Success": "Updated Campus ID"}
        else:  
            return {"Failed": "Failed to Update Campus ID"}

    def update_name(self, email, new_f_name=None, new_l_name=None):
        user = public_user_info.query.filter(public_user_info.email == email).first()

        if user and new_f_name and new_l_name:
            user.first_name = new_f_name
            user.last_name = new_l_name
            db.session.commit()
            return {'status': 'Success', 'reason': 'Updated user\'s First and Last name'}
        
        elif user and new_f_name and not new_l_name:
            user.first_name = new_f_name
            db.session.commit()
            return {'status': 'Success', 'reason': 'Updated user\'s First name'}  
        
        elif user and not new_f_name and new_l_name:
            user.last_name = new_l_name
            db.session.commit()
            return {'status': 'Success', 'reason': 'Updated user\'s Last name'}
        
        else:
            return {'status': 'Failed', 'reason': 'Failed to update user information'}

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
        taken_courses = self.get_taken_courses()
        if taken_courses:
            for tkn_crs in taken_courses:
                tkn_crs.delete_commit()

        db.session.delete(self)
        db.session.commit()

    """
    Makes a plan for the user
    """
    def make_plan(self, user_id ,name="Default Plan 0", num=0):
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

            if name == "Default Plan 0":
                self.plan_name = f"Default Plan {last_num.plan_num+1}"
            else:
                trimed_name = name[:25]
                valid = check_user_input(trimed_name)

                if valid:
                    self.plan_name = trimed_name
                else:
                    self.plan_name = f"Default plan {last_num.plan_num+1}"

        else:
            self.plan_num = num
            self.plan_name = "My First Plan"

        self.created_at = datetime.now()
        return self.plan_name

    def get_plan_name(self):
        plan_name = plan.query.filter(plan.plan_id == self.plan_id).order_by(plan.plan_name).first()
        return plan_name.plan_name

    def rename_plan(self, usr_id, new_name):
        valid = check_user_input(new_name)
        
        if not valid:
            return FAILED_BLACKLIST

        usr_plan = plan.query.filter(plan.user_id == usr_id, plan.plan_id == self.plan_id).first()
        if usr_plan:
            usr_plan.plan_name = new_name
            usr_plan.add_commit()
            return {"status": "Success", "result": f"Plan nam changed to {new_name}"}
        else:
            return {"status": "Failed", "result": "User doesn't have that plan"}

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

    #Gets the years a user is taking a course
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
    deg_name = db.Column('degree_name',db.String(100))
    deg_type = db.Column('degree_type',db.String(100))

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

    def __init__(self, course_id=None):
        if course_id:
            self.crs_id = course_id

    def add_commit(self):
        db.session.add(self)
        db.session.commit()

    def delete_commit(self):
        db.session.delete(self)
        db.session.commit()

    #Gets the prereq courses list and converts the string course ids to ints
    def get_prereq_ints(self):
        pre_list = prereq.query.all()

        for obj in pre_list:
            for crs in obj.prereq_courses:
                crs = int(crs)

        return pre_list
    
    #Checks if a course can be taken by checking if one of its prereqs has been taken if it has prereqs
    def check_prereqs(self, taken_courses):
        pre_list = self.get_prereq_ints()
        can_take = True
        course_req = []

        for obj in pre_list:
            if self.crs_id == obj.crs_id:
                course_req.append(obj.prereq_courses)

        #Runs only if a course has prereqs and has taken courses
        if course_req and taken_courses:
            in_req = False
            for pre_obj in course_req:
                for taken_obj in taken_courses:
                    if taken_obj.course_id in pre_obj:
                        in_req = True
                if in_req == False:
                    return in_req
                
        #Has prereqs but has not taken any courses
        elif course_req and not taken_courses:
            can_take = False
        
        return can_take
    
    #Gets the prereqs for the given course
    def get_prereqs(self):
        pre_list = self.get_prereq_ints()
        courses_req = []

        for obj in pre_list:
            if self.crs_id == obj.crs_id:
                courses_req.append(obj.prereq_courses)
        
        return courses_req

# Defines your prereq output
class PrereqSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("prereq_id", "crs_id", "prereq_courses", "grade_required")

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
class course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'))
    subject = db.relationship('subject', primaryjoin='course.subject_id == subject.subject_id', backref=db.backref('subject', lazy='dynamic'))

    course_title = db.Column(db.String(100))
    course_num = db.Column(db.Integer)
    credits = db.Column(db.Integer)
    description = db.Column(db.String(300))


    crs_offered = db.Table('course_offered',
    db.Column('offered_id', db.Integer, primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('semester_id', db.Integer, db.ForeignKey('semester.semester_id')),
    db.Column('frequency', db.Integer) )

    crs_required = db.Table('courses_required',
    db.Column('requirement_id', db.Integer, db.ForeignKey('requirement.requirement_id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.course_id')),
    db.Column('course_options', db.ARRAY(db.Integer)))

    def __init__(self,crs_id=None, title=None, subject_id=None, crs_num=None, credits=None):
        
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
        elif crs_id:
            self.course_id = crs_id

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


    #Returns a course object based on ID
    def get_course(self, crs_id=None):
        if crs_id:
            crs = course.query.get(crs_id)
        else:
            crs = course.query.get(self.course_id)
        return crs

    def get_description(self, crs_id=None):
        if crs_id:
            crs_obj = self.query.get(crs_id)
        else:
            crs_obj = self.query.get(self.course_id)
        
        crs_desc = crs_obj.description
        return crs_desc

    #Get courses offered for a term
    def get_courses_offered(self, sem_id):
        stmt = db.select(self.crs_offered).where(
            db.and_(
                self.crs_offered.c.course_id != None, self.crs_offered.c.frequency != None, self.crs_offered.c.semester_id == sem_id
            )
        )
        result = db.session.execute(stmt).fetchall()
        return result

    def get_gep_ids(self):
        geps = course.query.filter(course.subject_id == 11)
        gep_ids = []

        for obj in geps:
            gep_ids.append(obj.course_id)

        return gep_ids

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
        fields = ("subject_id", "sub_code", "sub_name")

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
        elif not sem_id and year and term:
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
    Gets all semester objects for a specific term
    Fall, Winter, Spring, Summer
    Input: a list of courses in a plan
    Return: if input given 
    """
    def get_fall_objs(self, past=False):
        if past:
            fall_objs = []
            semesters = self.get_year_order_objs(past)
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

    def get_winter_objs(self, past=False):
        if past:
            winter_objs = []
            semesters = self.get_year_order_objs(past)
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

    def get_spring_objs(self, past=False):
        if past:
            spring_objs = []
            semesters = self.get_year_order_objs(past)
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

    def get_summer_objs(self, past=False):
        if past:
            summer_objs = []
            semesters = self.get_year_order_objs(past)
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
    Gets relevant semesters based on current year and approximate term if 'past' is False
    Gets all semesters before current year if 'past' is True
    Return: list of semester objs
    """
    def get_year_order_objs(self, past = False):
        self.update_year_term()
        curr_year = self.current_year
        curr_term = self.current_term
        all_semesters = semester.query.all()
        order_objs = []
        
        if past:
            before_curr_term = True
            for obj in all_semesters:
                if obj.year == curr_year and obj.term == curr_term:
                    before_curr_term = False
                    order_objs.append(obj)
                    break
                elif before_curr_term:
                    order_objs.append(obj)

        else:
            reached_curr_term = False
            for obj in all_semesters:
                if reached_curr_term:
                    order_objs.append(obj)
                    self.last_year = obj.year
                elif obj.year == curr_year and obj.term == curr_term:
                    reached_curr_term = True
                    order_objs.append(obj)
                    self.last_year = obj.year

        return order_objs


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

