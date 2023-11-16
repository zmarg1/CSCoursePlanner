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



#TODO: returns all the fall courses in a distionary fall_dict = {2024: [fall_courses],2025: [fall_courses], ...: [...]}
@view_all_api.route("/user/view-all-fall-courses", methods=["GET"])
def view_all_fall(user_email):
    if user_email:
        sem = semester()
        all_fall_objs = sem.get_fall_objs()
        crs = course()
        courses = crs.get_courses_offered()
        fall_courses = {}

        for sem in all_fall_objs:
            fall_courses[sem.year] = []
            for offr_id, crs_id, sem_id, freq in courses:
                if sem_id == sem.semester_id:
                    fall_courses[sem.year].append(crs_id)
        print("FALL COURSES ", fall_courses)
        return jsonify(fall_courses)
    
    return jsonify(FAILED_EMAIL)

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