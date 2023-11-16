"""
Authors: Amir Hawkins-Stewart & Zach Margulies

Description: Makes objects of the databse tables, sends and recieves data from the supabase databse.

TODO: Finish the classes, app.routes to send and receive from site 
"""

from setup import session, app, jsonify, request, admin_course_schema, admin_courses_schema, plan_schema, user_courses_schema, db, plans_schema
from setup import course, subject, users, public_user_info, plan, taken, semester, requirement
from setup import FAILED_EMAIL, FAILED_DELETE, FAILED_GET, FAILED_POST
from view_all import view_all_api
from admin import admin_api

app.register_blueprint(view_all_api)
app.register_blueprint(admin_api)


#TODO: Update route to not use session
@app.route("/user/update-campus-id/<user_email>", methods=["POST"])
def update_campus_id(user_email):
    if user_email and request.method == "POST":
        new_c_id = request.form["campus_id"]
        usr_email = session["user_email"]
        curr_user = public_user_info(usr_email)
        curr_user.update_campus_id(new_c_id)
        curr_user.add_commit()
        return jsonify({"Success": "Successful campus id change"})
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    else:
        return jsonify(FAILED_POST)


"""
Makes an empty plan for the user
"""
@app.route("/user/plan/make-plan/<user_email>", methods=["POST"])
def user_make_plan(user_email):
    if user_email and request.method == "POST":
        curr_user = users(user_email)
        usr_id = curr_user.get_user_id()
        new_plan = plan()
        new_plan.make_plan(usr_id)
        if new_plan:
            new_plan.add_commit()
            return jsonify({"Success": "Successfully made plan"})
    elif not user_email:
        return jsonify(FAILED_EMAIL)
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
#TODO: Use def that checks if given user has plan
@app.route("/user/plan/add-course-to-plan/<user_email>/<plan_id>/<crs_id>/<sem_id>", methods=["POST"])
def user_add_course_to_plan(user_email, plan_id, crs_id, sem_id):
    if user_email:
        if request.method == "POST":
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
    
            return jsonify({"Failed": "Failed necessary field(s) left empty"})
    
        return jsonify({"Failed": "Forms Missing"})
    
    return jsonify(FAILED_EMAIL)


"""
Deletes the given users course from selected plan
Inputs: users email, plan id, course id
"""
#TODO: Have it check if given user has plan
@app.route("/user/plan/delete-course-from-plan/<user_email>/<plan_id>/<crs_id>", methods=["DELETE"])
def user_delete_planned_course(user_email, crs_id, plan_id):
    if request.method == "DELETE" and crs_id and plan_id:
        in_taken = taken.query.filter(taken.course_id == crs_id, taken.plan_id == plan_id).first()
        if in_taken:
            usr_plan = plan(plan_id)
            crs_obj = course.query.get(in_taken.course_id)
            crs_title = crs_obj.course_title
            in_taken.delete_commit()
            return jsonify({"Success": f"Successfully deleted {crs_title} from {usr_plan.get_plan_name()}"})
        return jsonify({"Failed": "Course not in plan"})
                
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
Returns: a json of courses in plan {course title, course number, credits, subject code}
"""
#TODO: make a guest user check and make it check if user has plan
@app.route("/user/plan/view-plan/<user_email>/<plan_id>", methods=["GET"])
def user_view_plan(user_email, plan_id):
    if request.method == "GET" and user_email and plan_id:
        user = users(user_email)
        if user.user_has_plan(plan_id):
            curr_plan = plan(plan_id)
            plans_courses = curr_plan.get_courses()
            courses_dump = user_courses_schema.dump(plans_courses)
            return jsonify(courses_dump)
        
        return jsonify({"Failed": "User doesn't have plan"})
    
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
