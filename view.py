from flask import Blueprint
from setup import course, semester, users, plan, prereq
from setup import jsonify, request, taken_courses_schema, plans_schema, semesters_schema, user_courses_schema, user_course_schema, prereqs_schema
from setup import FAILED_EMAIL, FAILED_GET, FAILED_PLAN, FAILED_PLAN_ID, FAILED_SEM_ID, FAILED_CRS_ID

view_api = Blueprint('view_api', __name__)

"""
Returns all the courses in the database for a user to see
"""
@view_api.route("/user/view-term-courses/<user_email>/<plan_id>/<sem_id>", methods=["GET"])
def view_term_courses(user_email, plan_id, sem_id):
    if request.method == "GET" and user_email and plan_id and sem_id:
        user = users(user_email)
        plan_id = int(plan_id)
        has_plan = user.user_has_plan(plan_id)
        
        if has_plan:
            sem_id = int(sem_id)
            all_courses = user.view_courses(plan_id, sem_id)
            courses_dump = user_courses_schema.dump(all_courses)
            return jsonify(courses_dump)
        
        elif plan_id == -1:
            all_courses = course.query.all()
            courses_dump = user_courses_schema.dump(all_courses)
            return jsonify(courses_dump)
        
        else:
            return jsonify(FAILED_PLAN)
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify(FAILED_PLAN_ID)
    
    elif not sem_id:
        return jsonify(FAILED_SEM_ID)
    
    else:
        return jsonify(FAILED_GET)


"""
Views all relevant semesters starting at current year and approximate term
"""
@view_api.route("/user/view-all-semesters", methods=["GET"])
def user_view_all_semesters():
    sem = semester()
    all_semesters = sem.get_year_order_objs()
    semester_dump = semesters_schema.dump(all_semesters)
    return jsonify(semester_dump)


"""
Chooses a plan to view
Gets user from session
Views the current users chosen plan
Returns: a users plan as a dictionary of years with a dictionary of terms storing the array of dictionary course objects
Ex. {"2024": {"Fall": [{corse info}, {course info}] } }
"""
@view_api.route("/user/plan/view-plan/<user_email>/<plan_id>", methods=["GET"])
def user_view_plan(user_email, plan_id):
    if request.method == "GET" and user_email and plan_id:
        user = users(user_email)
        plan_id = int(plan_id)
        if user.user_has_plan(plan_id):
            fall_courses = user.get_all_terms_courses(plan_id, "Fall")
            winter_courses = user.get_all_terms_courses(plan_id, "Winter")
            spring_courses = user.get_all_terms_courses(plan_id, "Spring")
            summer_courses = user.get_all_terms_courses(plan_id, "Summer")

            #dump will be [] if no classes in term
            fall_dump = taken_courses_schema.dump(fall_courses)
            winter_dump = taken_courses_schema.dump(winter_courses)
            spring_dump = taken_courses_schema.dump(spring_courses)
            summer_dump = taken_courses_schema.dump(summer_courses)

            curr_plan = plan(plan_id)
            years = curr_plan.get_years()
            usr_plan = {}
            usr_plan = user.to_dict(years, usr_plan, fall_dump)
            usr_plan = user.to_dict(years, usr_plan, winter_dump)
            usr_plan = user.to_dict(years, usr_plan, spring_dump)
            usr_plan = user.to_dict(years, usr_plan, summer_dump)
                
            return jsonify(usr_plan)
        
        return jsonify(FAILED_PLAN)
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify({"Failed": "Plan Id not given"})
    
    else:
        return jsonify({"Failed": "Wrong method needs \"GET\" method"})

"""
Views all the users plans 
Return: plan obj on success
"""
@view_api.route("/user/plan/view-all-plans/<user_email>", methods=["GET"])
def user_view_all_plans(user_email):
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
View all the classes in a selected term
"""
@view_api.route("/user/plan/view-semester-courses/<user_email>/<plan_id>/<sem_id>", methods=["GET"])
def view_semester_courses(user_email, plan_id, sem_id):
    if user_email and request.method == "GET" and plan_id and sem_id:
        user = users(user_email)
        plan_id = int(plan_id)
        sem_id = int(sem_id)

        if user.user_has_plan(plan_id):
            plan_courses = user.get_term_courses(plan_id, sem_id)

            if plan_courses:
                sem = semester(sem_id)
                term_dump = taken_courses_schema.dump(plan_courses)
                term_plan = {}
                years = [sem.year]
                term_plan = user.to_dict(years, term_plan, term_dump)
                return jsonify(term_plan)
        
            elif not plan_courses:
                return jsonify({"Failed": "Semester not in plan"})
        
        else:
            return(FAILED_PLAN)

    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify({"Failed": "Expected Plan ID"})
    
    elif not sem_id:
        return jsonify({"Failed": "Expected Semester ID"})
    
    else:
        return jsonify(FAILED_GET)
    

@view_api.route("/user/course/view-prereqs/<crs_id>", methods=["GET"])
def view_prereqs(crs_id):
    if crs_id and request.method == "GET":
        crs_id = int(crs_id)
        preqs = prereq(crs_id)
        all_prereqs = preqs.get_prereqs()

        _course = course()
        preq_crs_dump = {}
        i = 0
        for preq in all_prereqs:
            key = f"req{i}"
            preq_crs_dump[key] = []
            for crs in preq:
                crs_obj = _course.get_course(crs)
                preq_crs_dump[key].append(user_course_schema.dump(crs_obj))
            i += 1

        return preq_crs_dump

    elif not crs_id:
        return jsonify(FAILED_CRS_ID)
    
    else:
        return jsonify(FAILED_GET)
    

@view_api.route("/user/course/view-description/<crs_id>", methods=["GET"])
def view_description(crs_id):
    if request.method == "GET" and crs_id:
        crs_id = int(crs_id)
        crs = course(crs_id)
        desc = crs.get_description()
        if desc:
            return jsonify(desc)
        else:
            return jsonify({"Failed": "Course has no description"})

    elif not crs_id:
        return jsonify(FAILED_CRS_ID)
    
    else:
        return jsonify(FAILED_GET)
    
@view_api.route("/user/course/view-description-and-prereqs/<crs_id>", methods=["GET"])
def view_desc_prereqs(crs_id):
    if crs_id and request.method == "GET":
        crs_id = int(crs_id)
        crs = course(crs_id)
        desc = crs.get_description()

        if not desc:
            return jsonify({"Failed": "Course has no description"})
        
        preqs = prereq(crs_id)
        all_prereqs = preqs.get_prereqs()

        _course = course()
        crs_info_dump = {}
        crs_info_dump["desc"] = desc

        i = 0
        for preq in all_prereqs:
            key = f"req{i}"
            crs_info_dump[key] = []
            for crs in preq:
                crs_obj = _course.get_course(crs)
                crs_info_dump[key].append(user_course_schema.dump(crs_obj))
            i += 1

        return jsonify(crs_info_dump)
        

    elif not crs_id:
        return jsonify(FAILED_CRS_ID)
    
    else:
        return jsonify(FAILED_GET)