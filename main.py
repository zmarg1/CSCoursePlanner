"""
Authors: Amir Hawkins-Stewart & Zach Margulies

Description: Makes objects of the databse tables, sends and recieves data from the supabase databse.

TODO: Finish the classes, app.routes to send and receive from site 
"""

from setup import session, app, jsonify, request, db
from setup import admin_course_schema, admin_courses_schema, plan_schema, user_courses_schema, user_course_schema , plans_schema, taken_courses_schema
from setup import course, subject, users, public_user_info, plan, taken, semester, requirement
from setup import FAILED_EMAIL, FAILED_DELETE, FAILED_GET, FAILED_POST, FAILED_PLAN
from view_all import view_all_api
from admin import admin_api

app.register_blueprint(view_all_api)
app.register_blueprint(admin_api)


#TODO: Test it
@app.route("/user/update-campus-id/<user_email>", methods=["POST"])
def update_campus_id(user_email):
    if user_email and request.method == "POST":
        new_c_id = request.form["campus_id"]
        curr_user = users(user_email)
        changed = curr_user.update_campus_id(new_c_id)
        if changed:
            return jsonify({"Success": "Updated Campus ID"})
        
        return jsonify({"Failed": "Failed to Update Campus ID"})
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    else:
        return jsonify(FAILED_POST)


"""
Makes an empty plan for the user if they have not reached the plan limit
"""
@app.route("/user/plan/make-plan/<user_email>", methods=["POST"])
def user_make_plan(user_email):
    if user_email and request.method == "POST":
        curr_user = users(user_email)
        result = curr_user.user_make_plan()
        if "Success" in result:
            return jsonify(result)
        
        return jsonify(result)
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    else:
        return jsonify(FAILED_POST)


#TODO: Implement
@app.route("/user/plan/rename-plan/<user_email>/<plan_id>", methods=["POST"])
def rename_plan(user_email, plan_id):
    if user_email and request.method == "POST" and "new_name" in request.json:
        new_name = request.json["new_name"]
        user = users(user_email)
        plan_id = int(plan_id)
        user_has = user.user_has_plan(plan_id)

        if user_has and new_name:
            usr_plan = plan(plan_id)
            result = usr_plan.rename_plan(user.get_user_id(), new_name)

            if "Success" in result:
                return jsonify(result)
            else:
                return jsonify(result)

        else:
            return jsonify(FAILED_PLAN)

    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not "new_name" in request.json:
        return jsonify({"Failed": "Missing json data \"new_name\""})
    
    else:
        return jsonify(FAILED_POST)


"""
Deletes the users chosen plan
"""
@app.route("/user/plan/delete-plan/<user_email>/<plan_id>", methods=["DELETE"])
def user_delete_plan(user_email, plan_id):
    if user_email and plan_id and request.method == "DELETE":
        curr_user = users(user_email)

        usr_id = curr_user.get_user_id()
        to_delete = plan.query.filter(plan.plan_id == plan_id, plan.user_id == usr_id).first()

        if to_delete:
            plan_name = to_delete.plan_name
            chosen_plan = plan(to_delete.plan_id)
            plan_courses = chosen_plan.get_taken_courses()
            for taken_crs in plan_courses:
                user_delete_planned_course(user_email, taken_crs.course_id, taken_crs.plan_id)
            to_delete.delete_commit()
            return jsonify({"Success": f"Successfully deleted {plan_name}"})
            
        return jsonify({"Failed": "Current user can't delete this plan or plan not found"})
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify({"Failed": "Missing \"plan_id\""})
    
    else:
        return jsonify(FAILED_DELETE)


"""
Adds a course to users plan using taken
"""
@app.route("/user/plan/add-course-to-plan/<user_email>/<plan_id>/<crs_id>/<sem_id>", methods=["POST"])
def user_add_course_to_plan(user_email, plan_id, crs_id, sem_id):
    if user_email and request.method == "POST":
        user = users(user_email)
        plan_id = int(plan_id)
        usr_has = user.user_has_plan(plan_id)

        if usr_has:
            req_id = 1
            grade = None

            #Checks if correct 
            if plan_id and crs_id and req_id and sem_id:
                in_plan = plan.query.filter(plan.plan_id == plan_id).order_by(plan.plan_id.desc()).first()
                in_course = course.query.filter(course.course_id == crs_id).order_by(course.course_id.desc()).first()
                in_req = requirement.query.filter(requirement.requirement_id == req_id).order_by(requirement.requirement_id.desc()).first()
                in_sem = semester.query.filter(semester.semester_id == sem_id).order_by(semester.semester_id.desc()).first()

                crs_in_taken = taken.query.filter(taken.plan_id == plan_id, taken.course_id == crs_id).order_by(taken.course_id.desc()).first()

                if in_plan and in_course and in_req and in_sem and not crs_in_taken:
                    result = user.add_course(plan_id, crs_id, req_id, sem_id, grade)
                    if "Success" in result:
                        return jsonify({"Success": f"Added {in_course.course_title} to {in_plan.plan_name} for {in_sem.term}"})
                    else:
                        return jsonify(result)
                
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

            return jsonify({"Failed": "Failed missing inputs expected plan_id, course_id, semester_id"})
        
        elif not usr_has:
            return jsonify({"Failed": "User doesn't have plan"})
        
    elif not request.method == "POST":
        return jsonify(FAILED_POST)
    else:
        return jsonify(FAILED_EMAIL)


"""
Deletes the given users course from selected plan
Inputs: users email, plan id, course id
"""
@app.route("/user/plan/delete-course-from-plan/<user_email>/<plan_id>/<crs_id>", methods=["DELETE"])
def user_delete_planned_course(user_email, crs_id, plan_id):
    if request.method == "DELETE" and crs_id and plan_id:
        user = users(user_email)
        plan_id = int(plan_id)
        if user.user_has_plan(plan_id):
            in_taken = taken.query.filter(taken.course_id == crs_id, taken.plan_id == plan_id).first()
            if in_taken:
                usr_plan = plan(plan_id)
                crs_obj = course.query.get(in_taken.course_id)
                crs_title = crs_obj.course_title
                in_taken.delete_commit()
                return jsonify({"Success": f"Successfully deleted {crs_title} from {usr_plan.get_plan_name()}"})
            
            return jsonify({"Failed": "Course not in plan"})
        
        return jsonify({"Failed": "User doesn't have plan"})
                
    elif "curr_plan_id" not in session:
        return jsonify({"Failed": "No plan in session"})  
      
    elif "course_id" not in request.json:
        return jsonify({"Failed": "Missing \"course_id\" field in json"})
    
    else:
        return jsonify({"Failed": "No Form"})


"""
Chooses a plan to view
Gets user from session
Views the current users chosen plan
Returns: a users plan as a dictionary of years with a dictionary of terms storing the array of dictionary course objects
Ex. {"2024": {"Fall": [{corse info}, {course info}] } }
"""
@app.route("/user/plan/view-plan/<user_email>/<plan_id>", methods=["GET"])
def user_view_plan(user_email, plan_id):
    if request.method == "GET" and user_email and plan_id:
        user = users(user_email)
        plan_id = int(plan_id)
        if user.user_has_plan(plan_id):
            curr_plan = plan(plan_id)
            fall_courses = user.get_term_courses(plan_id, "Fall")
            winter_courses = user.get_term_courses(plan_id, "Winter")
            spring_courses = user.get_term_courses(plan_id, "Spring")
            summer_courses = user.get_term_courses(plan_id, "Summer")

            #dump will be [] if no classes in term
            fall_dump = taken_courses_schema.dump(fall_courses)
            winter_dump = taken_courses_schema.dump(winter_courses)
            spring_dump = taken_courses_schema.dump(spring_courses)
            summer_dump = taken_courses_schema.dump(summer_courses)

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
@app.route("/user/plan/view-all-plans/<user_email>", methods=["GET"])
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

@app.route("/user/plan/view-term/<user_email>/<plan_id>/<sem_id>", methods=["GET"])
def user_view_term(user_email, plan_id, sem_id):
    if user_email and request.method == "GET":
        pass

    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    else:
        return jsonify(FAILED_GET)


@app.route("/user/plan/view-all-term/<user_email>/<plan_id>/<term>", methods=["GET"])
def user_all_term(user_email, plan_id, term):
    if user_email and request.method == "GET" and plan_id and term:
        user = users(user_email)
        plan_courses = user.get_term_courses(plan_id, term)
        plan_id = int(plan_id)

        if plan_courses and user.user_has_plan(plan_id):
            curr_plan = plan(plan_id)
            years = curr_plan.get_years(term)
            fall_dump = taken_courses_schema.dump(plan_courses)
            fall_plan = {}
            fall_plan = user.to_dict(years, fall_plan, fall_dump)
            return jsonify(fall_plan)
        
        elif not plan_courses:
            return jsonify({"Failed": f"{term} courses not in plan"})
        
        else:
            return(FAILED_PLAN)

    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify({"Failed": "Expected plan ID"})
    
    elif not term:
        return jsonify({"Failed": "Term is expected"})
    
    else:
        return jsonify(FAILED_GET)


""" 
Deletes a term given its a Fall, Spring, Summer, Winter term from a year
"""
@app.route("/user/plan/delete-term/<user_email>/<plan_id>/<sem_id>", methods=["DELETE"])
def delete_term(user_email, plan_id, sem_id):
    if request.method == "DELETE" and user_email:
        user = users(user_email)
        plan_id = int(plan_id)
        user_has = user.user_has_plan(plan_id)

        if user_has:
            sem_id = int(sem_id)
            result = user.delete_term(plan_id, sem_id)
            if "Success" in result:
                return jsonify(result)
            else:
                return jsonify(result)
        else:
            return jsonify(FAILED_PLAN)

    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    else:
        return jsonify(FAILED_DELETE)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
