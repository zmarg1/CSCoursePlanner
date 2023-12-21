"""
Authors: Amir Hawkins-Stewart

Description: Makes objects of the database tables, sends and recieves data from the supabase databse.
"""

from setup import session, app, jsonify, request, db, requests
from setup import course, users, public_user_info, plan, taken
from setup import FAILED_EMAIL, FAILED_DELETE, FAILED_POST, FAILED_PLAN, FAILED_PLAN_ID, clerk_api_key
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
                return jsonify({'status': "Success", 'reason': f"Successfully deleted user {user.email}"})
            
            print("Failed not in database")
            return jsonify({'status': "Success", 'reason': f"User not in database"})
        
        else:
            print("Ignored: Event not user.deleted")
            return jsonify({'status': 'Ignored', 'reason': 'Event not user.deleted'}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'Error'}), 500

"""
When a new clerk user is made it updates there private metadata
if they have none and adds them to the Supabase databse
"""
@app.route("/user-created", methods=["POST"])
def user_created_webhook():
    try:
        event = request.json
        event_type = event.get('type')

        if event_type == 'user.created':
            event_data = event.get('data')
            pub_meta = event_data.get('public_metadata')
            user_id = event_data.get('id')
            user_email = event_data.get('email_addresses', [{}])[0].get('email_address')
            user_first_name = event_data.get('first_name')
            user_last_name = event_data.get('last_name')
            result = public_user_info.check_user(user_id)

            if 'admin' not in pub_meta and result['status'] == 'Failed':

                # Fetch the user data from Clerk using the user_id
                clerk_api_url = f'https://api.clerk.dev/v1/users/{user_id}'
                headers = {'Authorization': f'Bearer {clerk_api_key}'}

                # Update the private_metadata making a new admin bool
                admin = {"public_metadata": {"admin": False}}
                

                # Updates user with new metadata
                response = requests.patch(clerk_api_url, json=admin, headers=headers)

                pub_user = public_user_info(user_id, user_email)
                pub_user.add_commit()
                if user_first_name or user_first_name:
                    pub_user.update_name(user_email, user_first_name, user_last_name)

                if response.status_code == 200:
                    print("User updated")
                    return jsonify({'status': 'Success', 'user_id': user_id, 'user_email': user_email})
                else:
                    print(f"Failed to update user. Clerk API returned status code: {response.status_code}")
                    return jsonify({'status': 'Error', 'reason': 'Failed to update user'}), response.status_code
            
            elif result['status'] == 'Failed':
                pub_user = public_user_info(user_id, user_email)
                pub_user.add_commit()
                if user_first_name or user_first_name:
                    pub_user.update_name(user_email, user_first_name, user_last_name)

            elif user_first_name or user_first_name and result['status'] == 'Success':
                    pub_user.update_name(user_email, user_first_name, user_last_name)

            else:
                print("User has admin")
                return jsonify({'status': 'Failed', 'reason': 'User has admin'})
        else:
            print("Ignored")
            return jsonify({'status': 'Ignored', 'reason': 'Event not user.created'})
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'Error'}), 500

"""
When a user updates their Clerk profile name it sends the update to Supabase
"""
@app.route("/user-updated", methods=["POST"])
def user_updated_webhook():
    try:
        event = request.json
        event_type = event.get('type')

        if event_type == 'user.updated':
            event_data = event.get('data')

            user_email = event_data.get('email_addresses', [{}])[0].get('email_address')
            user_first_name = event_data.get('first_name')
            user_last_name = event_data.get('last_name')

            pub_user = public_user_info()
            result = pub_user.update_name(user_email, user_first_name, user_last_name)

            if result['status'] == 'Success':
                return jsonify(result)
            else:
                return jsonify(result)


    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({'status': 'Error'}), 500


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
        return jsonify({"status": "Failed", "result":  "Missing json \'plan_name\'"})

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
            return jsonify({"status": "Failed", "result":  "No name entered"})

        else:
            return jsonify(FAILED_PLAN)

    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify(FAILED_PLAN_ID)
    
    elif not "new_name" in request.json:
        return jsonify({"status": "Failed", "result":  "Missing json data \"new_name\""})
    
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
            return jsonify({"status": "Success", "result":  f"Successfully deleted {plan_name}"})
            
        return jsonify({"status": "Failed", "result":  "Current user can't delete this plan or plan not found"})
    
    elif not user_email:
        return jsonify(FAILED_EMAIL)
    
    elif not plan_id:
        return jsonify({"status": "Failed", "result":  "Missing \"plan_id\""})
    
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
                return jsonify({"status": "Failed", "result":  "Failed missing inputs expected plan_id, course_id, semester_id"})
        
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
                return jsonify({"status": "Success", "result": f"Successfully deleted {crs_title} from {usr_plan.get_plan_name()}"})
            
            return jsonify({"status": "Failed", "result": "Course not in plan"})
        
        return jsonify(FAILED_PLAN)
                
    elif "curr_plan_id" not in session:
        return jsonify({"status": "Failed", "result": "No plan in session"})  
      
    elif "course_id" not in request.json:
        return jsonify({"status": "Failed", "result": "Missing \"course_id\" field in json"})
    
    else:
        return jsonify({"status": "Failed", "result": "No Form"})


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
