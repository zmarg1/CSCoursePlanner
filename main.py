"""
Authors: Amir Hawkins-Stewart & Zach Margulies

Description: Makes objects of the databse tables, sends and recieves data from the supabase databse.
"""

from setup import session, app, jsonify, request, db, requests
from setup import admin_course_schema, admin_courses_schema, plan_schema, user_courses_schema, user_course_schema , plans_schema, taken_courses_schema
from setup import course, subject, users, public_user_info, plan, taken, semester, requirement
from setup import FAILED_EMAIL, FAILED_DELETE, FAILED_GET, FAILED_POST, FAILED_PLAN, FAILED_PLAN_ID
from view import view_api
from admin import admin_api

app.register_blueprint(view_api)
app.register_blueprint(admin_api)

"""
Deletes the Clerk user from the database
"""
@app.route("/delete-user", methods=["POST"])
def delete_webhook():
    try:
        event = request.json
        event_type = event.get('type')

        if event_type == 'user.deleted':
            user_id = event['data']['id']
            user = users(None, False, user_id)
            result = user.delete_user_data()
            if "Error" not in result:
                print(f"Deleted user with email: {user.email} and user_id: {user_id}")
                return jsonify({"Success": f"Successfully deleted user {user.email}"})
            
            print("Failed not in database")
            return jsonify({"Success": f"User not in database"})
        
        else:
            print("Ignored: Event not user.deleted")
            return jsonify({'status': 'ignored', 'reason': 'Event not user.deleted'}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'error'}), 500


"""
When a new clerk user is made it updates there private metadata
if they have none
"""
@app.route("/update-user", methods=["POST"])
def update_user_webhook():
    try:
        event = request.json
        event_type = event.get('type')

        if event_type == 'user.created':
            event_data = event.get('data')
            priv_meta = event_data.get('private_metadata')
            user_id = event_data.get('id')
            user_email = event_data.get('email_addresses', [{}])[0].get('email_address')

            if 'admin' not in priv_meta and public_user_info.check_user(user_id):

                # Fetch the user data from Clerk using the user_id
                clerk_api_url = f'https://api.clerk.dev/v1/users/{user_id}'
                clerk_api_key = 'sk_test_8Fvp5UH4vZplPHK24IdPQXnFqMipUQGYN7WmkomiHG'  # Replace with your Clerk API key
                headers = {'Authorization': f'Bearer {clerk_api_key}'}

                # Update the private_metadata making a new admin bool
                admin = {"private_metadata": {"admin": False}}

                # Updates user with new metadata
                response = requests.patch(clerk_api_url, json=admin, headers=headers)

                pub_user = public_user_info(user_id, user_email)
                pub_user.add_commit()

                if response.status_code == 200:
                    print("User updated")
                    return jsonify({'status': 'success', 'user_id': user_id, 'user_email': user_email})
                else:
                    print(f"Failed to update user. Clerk API returned status code: {response.status_code}")
                    return jsonify({'status': 'error', 'reason': 'Failed to update user'}), response.status_code
            else:
                print("User has admin")
                return jsonify({'status': 'success', 'reason': 'User has admin'})
        else:
            print("Ignored")
            return jsonify({'status': 'ignored', 'reason': 'Event not user.created'})
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'error'}), 500


@app.route("/user/update-campus-id/<user_email>", methods=["POST"])
def update_campus_id(user_email):
    if user_email and request.method == "POST":
        new_c_id = request.json["campus_id"]
        curr_user = users(user_email)
        result = curr_user.update_campus_id(new_c_id)
        return jsonify(result)
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    else:
        return jsonify(FAILED_POST)


"""
Makes an empty plan for the user if they have not reached the plan limit
"""
@app.route("/user/plan/make-plan/<user_email>", methods=["POST"])
def user_make_plan(user_email):
    if user_email and request.method == "POST" and  "plan_name" in request.json:
        plan_name = request.json["plan_name"]

        curr_user = users(user_email)

        if plan_name:
            result = curr_user.user_make_plan(plan_name)
        else:
            result = curr_user.user_make_plan()

        return jsonify(result)
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif "plan_name" in request.json:
        return jsonify({"Failed": "Missing json \'plan_name\'"})

    else:
        return jsonify(FAILED_POST)


@app.route("/user/plan/rename-plan/<user_email>/<plan_id>", methods=["POST"])
def rename_plan(user_email, plan_id):
    if user_email and request.method == "POST" and "new_name" in request.json and plan_id:
        new_name = request.json["new_name"]
        user = users(user_email)
        plan_id = int(plan_id)
        user_has = user.user_has_plan(plan_id)

        if user_has and new_name:
            usr_plan = plan(plan_id)
            result = usr_plan.rename_plan(user.get_user_id(), new_name)
            return jsonify(result)
        
        elif not new_name:
            return jsonify({"Failed": "No name entered"})

        else:
            return jsonify(FAILED_PLAN)

    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify(FAILED_PLAN_ID)
    
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
        sem_id = int(sem_id)
        crs_id = int(crs_id)
        usr_has = user.user_has_plan(plan_id)

        if usr_has:
            req_id = 1
            grade = None

            #Checks if correct 
            if plan_id and crs_id and req_id and sem_id:
                result = user.add_course(plan_id, crs_id, req_id, sem_id, grade)
                return jsonify(result)
            
            else:
                return jsonify({"Failed": "Failed missing inputs expected plan_id, course_id, semester_id"})
        
        else:
            return jsonify(FAILED_PLAN)
        
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
        user_has = user.user_has_plan(plan_id)

        if user_has:
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
Deletes a term given its a Fall, Spring, Summer, Winter term from a year
"""
@app.route("/user/plan/delete-term/<user_email>/<plan_id>/<sem_id>", methods=["DELETE"])
def delete_term(user_email, plan_id, sem_id):
    if request.method == "DELETE" and user_email and plan_id:
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
    
    elif not plan_id:
        return jsonify(FAILED_PLAN_ID)
    
    else:
        return jsonify(FAILED_DELETE)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
