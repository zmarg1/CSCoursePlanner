from flask import Blueprint
from setup import user_courses_schema, course, semester, semesters_schema
from setup import jsonify, request
from setup import FAILED_EMAIL, FAILED_GET

view_all_api = Blueprint('view_all_api', __name__)

"""
Returns all the courses in the database for a user to see
"""
#TODO: make it show only necessary courses and able to update when required course added to plan
@view_all_api.route("/user/view-all-courses", methods=["GET"])
def view_all_courses():
    if request.method == "GET":
        all_courses = course.query.all()
        courses_dump = user_courses_schema.dump(all_courses)
        return jsonify(courses_dump)
    
    return jsonify(FAILED_GET)


"""
Views all relevant semesters starting at current year and approximate term
"""
@view_all_api.route("/user/view-all-semesters", methods=["GET"])
def user_view_all_semesters():
    sem = semester()
    all_semesters = sem.get_year_order_objs()
    semester_dump = semesters_schema.dump(all_semesters)
    return jsonify(semester_dump)



#TODO: Show all courses of given term
@view_all_api.route("/user/view-all-past-fall-courses", methods=["GET"])
def view_all_past_fall():
    if request.method == "GET":
        sem = semester()
        fall_courses = sem.get_past_courses_ids()
        return jsonify(fall_courses)
    
    return jsonify(FAILED_GET)


#TODO: Update route to not use session
@view_all_api.route("/user/view-all-winter-courses", methods=["GET"])
def view_all_winter():
    pass

#TODO: Update route to not use session
@view_all_api.route("/user/view-all-spring-courses", methods=["GET"])
def view_all_spring():
    pass

#TODO: Update route to not use session
@view_all_api.route("/user/view-all-summer-courses", methods=["GET"])
def view_all_summer():
    pass