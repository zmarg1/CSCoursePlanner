from flask import Blueprint
from setup import course, subject, semester, public_user_info, degree, prereq
from setup import admin_course_schema, admin_courses_schema, semester_schema, semesters_schema, subject_schema, subjects_schema, degree_schema, degrees_schema, prereq_schema, prereqs_schema, public_user_schema, public_users_schema
from setup import session, db, jsonify, request
from setup import FAILED_GET, FAILED_DELETE, FAILED_POST, FAILED_PUT

admin_api = Blueprint('admin_api', __name__)

FAILED_ADMIN = {"Failed": "User is not admin"}

def route_reponse(admin, method):
    if not admin:
        return jsonify(FAILED_ADMIN)
    elif method == "GET":
        return jsonify(FAILED_GET)
    elif method == "PUT":
        return jsonify(FAILED_PUT)
    elif method == "DELETE":
        return jsonify(FAILED_DELETE)
    else:
        return jsonify(FAILED_POST)


"""
Enters main admin page for admin functionality
Returns:
string: A welcome message
"""
@admin_api.route('/admin')
def admin_pg():
    return "Welcome to the Admin page"


"""
Endpoint for getting one courses
"""
@admin_api.route('/admin/courses/<admin>/<course_id>', methods = ['GET'])
def admin_get_course(admin, course_id):
    if admin:
        my_course = course.query.get(course_id)
        return admin_course_schema.jsonify(my_course)
    
    return route_reponse(admin, request.method)


"""
Endpoint for getting all course
"""
@admin_api.route('/admin/view-courses/<admin>', methods = ['GET'])
def admin_get_all_courses(admin):
    if admin and request.method == "GET":
        all_courses = course.query.order_by(course.course_id.asc()).all()
        courses_dump = admin_courses_schema.dump(all_courses)
        return jsonify(courses_dump)
    
    return route_reponse(admin, request.method)


"""
Endpoint for creating a course
Inputs:
course_title - Title of course to be added
subject - Id/Code/Name of subject to be added
crs_num - Course numerical level
credits - Credits course is worth
"""
@admin_api.route('/admin/courses/create_course/<admin>', methods = ['POST'])
def admin_create_course(admin):
    if admin and request.method == "POST":
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
    
        return admin_course_schema.jsonify(new_course)
        
    return route_reponse(admin, request.method)


# endpoint for updating a course
@admin_api.route('/admin/courses/update_course/<admin>/<course_id>', methods = ['PUT'])
def admin_update_course(admin, course_id):
    if admin and request.method == "PUT":
        updated_course = course.query.get(course_id)

        updated_course.subject_id = request.json['subject_id']
        updated_course.crs_title = request.json['crs_title']
        updated_course.crs_num = request.json['crs_num']
        updated_course.credits = request.json['credits']

        db.session.commit()
        return admin_course_schema.jsonify(updated_course)
    
    return route_reponse(admin, request.method)


# endpoint for deleting a course
@admin_api.route('/admin/courses/delete/<admin>/<course_id>', methods = ['DELETE'])
def admin_delete_course(admin, course_id):
    if admin and request.method == "DELETE":
        deleted_course = course.query.get(course_id)

        db.session.delete(deleted_course)
        db.session.commit()
        return admin_course_schema.jsonify(deleted_course)
    
    return route_reponse(admin, request.method)


# endpoint for getting all subjects
@admin_api.route('/admin/subjects/<admin>', methods = ['GET'])
def admin_get_all_subjects(admin):
    if admin and request.method == "GET":
        all_subjects = subject.query.order_by(subject.subject_id.asc()).all()
        subjects_dump = subjects_schema.dump(all_subjects)
        return jsonify(subjects_dump)
    
    return route_reponse(admin, request.method)


# endpoint for getting one subject
@admin_api.route('/admin/subjects/<admin>/<subject_id>', methods = ['GET'])
def admin_get_subject(admin, subject_id):
    if admin and request.method == "GET":
        my_subject = subject.query.get(subject_id)
        return subject_schema.jsonify(my_subject)
    
    return route_reponse(admin, request.method)


# endpoint for creating a subject
@admin_api.route('/admin/subjects/<admin>/create_subject', methods = ['POST'])
def admin_create_subject(admin):
    if admin and request.method == "POST":
        subject_id = request.json['subject_id']
        subject_code = request.json['subject_code']
        subject_name = request.json['subject_name']
        new_subject = subject(subject_id, subject_code, subject_name)

        db.session.add(new_subject)
        db.session.commit()
        return subject_schema.jsonify(new_subject)
    
    return route_reponse(admin, request.method)


# endpoint for updating a subject
@admin_api.route('/admin/subjects/update_subject/<admin>/<subject_id>', methods = ['PUT'])
def admin_update_subject(admin, subject_id):
    if admin and request.method == "PUT":
        updated_subject = subject.query.get(subject_id)

        updated_subject.subject_code = request.json['subject_code']
        updated_subject.subject_name = request.json['subject_name']
    
        db.session.commit()
        return subject_schema.jsonify(updated_subject)
    
    return route_reponse(admin, request.method)


# endpoint for deleting a subject
@admin_api.route('/admin/subjects/delete/<admin>/<subject_id>', methods = ['DELETE'])
def admin_delete_subject(admin, subject_id):
    if admin and request.method == "DELETE":
        deleted_subject = subject.query.get(subject_id)

        db.session.delete(deleted_subject)
        db.session.commit()
        return subject_schema.jsonify(deleted_subject)
    
    return route_reponse(admin, request.method)


# endpoint for getting all semesters
@admin_api.route('/admin/semesters/<admin>', methods = ['GET'])
def admin_get_all_semesters(admin):
    if admin and request.method == "GET":
        all_semesters = semester.query.order_by(semester.semester_id.asc()).all()
        semesters_dump = semesters_schema.dump(all_semesters)
        return jsonify(semesters_dump)
    
    return route_reponse(admin, request.method)


# endpoint for getting one semester
@admin_api.route('/admin/semesters/<admin>/<semester_id>', methods = ['GET'])
def admin_get_semester(admin, semester_id):
    if admin and request.method == "GET":
        my_semester = semester.query.get(semester_id)
        return semester_schema.jsonify(my_semester)
    
    return route_reponse(admin, request.method)


# endpoint for creating a semester
@admin_api.route('/admin/semesters/create_semester/<admin>', methods = ['POST'])
def admin_create_semester(admin):
    if admin and request.method == "POST":
        semester_id = request.json['semester_id']
        term = request.json['term']
        year = request.json['year']
        new_semester = semester()
        new_semester.add_semester(term, year)

        db.session.add(new_semester)
        db.session.commit()
        return semester_schema.jsonify(new_semester)
    
    return route_reponse(admin, request.method)


# endpoint for updating a semester
@admin_api.route('/admin/semesters/update_semester/<admin>/<semester_id>', methods = ['PUT'])
def admin_update_semester(admin, semester_id):
    if admin and request.method == "PUT":
        updated_semester = semester.query.get(semester_id)

        updated_semester.term = request.json['term']
        updated_semester.year = request.json['year']
    
        db.session.commit()
        return semester_schema.jsonify(updated_semester)
    
    return route_reponse(admin, request.method)


# endpoint for deleting a semester
@admin_api.route('/admin/semesters/delete/<admin>/<semester_id>', methods = ['DELETE'])
def admin_delete_semester(admin, semester_id):
    if admin and request.method == "DELETE":
        deleted_semester = semester.query.get(semester_id)
        db.session.delete(deleted_semester)
        db.session.commit()
        return semester_schema.jsonify(deleted_semester)
    
    return route_reponse(admin, request.method)

# Users
# endpoint for getting all public users
@admin_api.route('/admin/users/<admin>', methods = ['GET'])
def admin_get_all_users(admin):
    if admin and request.method == "GET":
        all_users = public_user_info.query.order_by(public_user_info.user_id.asc()).all()
        users_dump = public_users_schema.dump(all_users)
        return jsonify(users_dump)
    
    return route_reponse(admin, request.method)


# endpoint for getting one public user
@admin_api.route('/admin/users/<admin>/<user_id>', methods = ['GET'])
def admin_get_user(admin, user_id):
    if admin and request.method == "GET":
        my_user = public_user_info.query.get(user_id)
        return public_user_schema.jsonify(my_user) 
    
    return route_reponse(admin, request.method)


# endpoint for creating a user
#TODO: Will need to make new clerk user aswell
@admin_api.route('/admin/users/create_user/<admin>', methods = ['POST'])
def admin_create_user(admin):
    if admin and request.method == "POST":
        user_id = request.json['user_id']
        email = request.json['email']
        campus_id = request.json['campus_id']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        new_user = public_user_info(user_id, email, campus_id, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()
        return public_user_schema.jsonify(new_user)
    
    return route_reponse(admin, request.method)


# endpoint for updating a user
@admin_api.route('/admin/users/update_user/<admin>/<user_id>', methods = ['PUT'])
def admin_update_user(admin, user_id):
    if admin and request.method == "PUT":
        updated_user = public_user_info.query.get(user_id)

        updated_user.email = request.json['email']
        updated_user.campus_id = request.json['campus_id']
        updated_user.first_name = request.json['first_name']
        updated_user.last_name = request.json['last_name']
    
        db.session.commit()
        return public_user_schema.jsonify(updated_user)
    
    return route_reponse(admin, request.method)


# endpoint for deleting a user
@admin_api.route('/admin/users/delete/<admin>/<user_id>', methods = ['DELETE'])
def admin_delete_user(admin, user_id):
    if admin and request.method == "DELETE":
        deleted_user = public_user_info.query.get(user_id)
        db.session.delete(deleted_user)
        db.session.commit()
        return public_user_schema.jsonify(deleted_user)
    
    return route_reponse(admin, request.method)


# Prereq
# endpoint for getting all prereqs
@admin_api.route('/admin/prereqs/<admin>', methods = ['GET'])
def admin_get_all_prereqs(admin):
    if admin and request.method == "GET":
        all_prereqs = prereq.query.order_by(prereq.prereq_id.asc()).all()
        prereqs_dump = prereqs_schema.dump(all_prereqs)
        return jsonify(prereqs_dump)
    
    return route_reponse(admin, request.method)


# endpoint for getting one prereq
@admin_api.route('/admin/prereqs/<admin>/<prereq_id>', methods = ['GET'])
def admin_get_prereq(admin, prereq_id):
    if admin and request.method == "GET":
        my_prereq = prereq.query.get(prereq_id)
        return prereq_schema.jsonify(my_prereq) 
    
    return route_reponse(admin, request.method)


# endpoint for creating a prereq
@admin_api.route('/admin/prereqs/create_prereq/<admin>', methods = ['POST'])
def admin_create_prereq(admin):
    if admin and request.method == "POST":
        prereq_id = request.json['prereq_id']
        crs_id = request.json['crs_id']
        prereq_courses = request.json['prereq_courses']
        grade_required = request.json['grade_required']
        new_prereq = prereq(prereq_id, crs_id, prereq_courses, grade_required)

        db.session.add(new_prereq)
        db.session.commit()
        return prereq_schema.jsonify(new_prereq)
    
    return route_reponse(admin, request.method)


# endpoint for updating a prereq
@admin_api.route('/admin/prereqs/update_prereq/<admin>/<prereq_id>', methods = ['PUT'])
def admin_update_prereq(admin, prereq_id):
    if admin and request.method == "PUT":
        updated_prereq = prereq.query.get(prereq_id)

        updated_prereq.crs_id = request.json['crs_id']
        updated_prereq.prereq_courses = request.json['prereq_courses']
        updated_prereq.grade_required = request.json['grade_required']
    
        db.session.commit()
        return prereq_schema.jsonify(updated_prereq)
    
    return route_reponse(admin, request.method)

# endpoint for deleting a prereq
@admin_api.route('/admin/prereqs/delete/<admin>/<prereq_id>', methods = ['DELETE'])
def admin_delete_prereq(admin, prereq_id):
    if admin and request.method == "DELETE":
        deleted_prereq = prereq.query.get(prereq_id)
        db.session.delete(deleted_prereq)
        db.session.commit()
        return prereq_schema.jsonify(deleted_prereq)
    
    return route_reponse(admin, request.method)


# Degree
# endpoint for getting all degrees
@admin_api.route('/admin/degrees/<admin>', methods = ['GET'])
def admin_get_all_degrees(admin):
    if admin and request.method == "GET":
        all_degrees = degree.query.order_by(degree.degree_id.asc()).all()
        degrees_dump = degrees_schema.dump(all_degrees)
        return jsonify(degrees_dump)
    
    return route_reponse(admin, request.method)


# endpoint for getting one degree
@admin_api.route('/admin/degrees/<admin>/<degree_id>', methods = ['GET'])
def admin_get_degree(admin, degree_id):
    if admin and request.method == "GET":
        my_degree = degree.query.get(degree_id)
        return degree_schema.jsonify(my_degree)
    
    return route_reponse(admin, request.method)


# endpoint for creating a degree
@admin_api.route('/admin/degrees/create_degree/<admin>', methods = ['POST'])
def admin_create_degree(admin):
    if admin and request.method == 'POST':
        degree_id = request.json['degree_id']
        deg_name = request.json['deg_name']
        deg_type = request.json['deg_type']
        new_degree = degree(degree_id, deg_name, deg_type)

        db.session.add(new_degree)
        db.session.commit()
        return degree_schema.jsonify(new_degree)
    
    return route_reponse(admin, request.method)


# endpoint for updating a degree
@admin_api.route('/admin/degrees/update_degree/<admin>/<degree_id>', methods = ['PUT'])
def admin_update_degree(admin, degree_id):
    if admin and request.method == 'PUT':
        updated_degree = degree.query.get(degree_id)

        updated_degree.degree_id = request.json['degree_id']
        updated_degree.deg_name = request.json['deg_name']
        updated_degree.deg_type = request.json['deg_type']
    
        db.session.commit()
        return degree_schema.jsonify(updated_degree)
    
    return route_reponse(admin, request.method)


# endpoint for deleting a degree
@admin_api.route('/admin/degrees/delete/<admin>/<degree_id>', methods = ['DELETE'])
def admin_delete_degree(admin, degree_id):
    if admin and request.method == "DELETE":
        deleted_degree = degree.query.get(degree_id)
        db.session.delete(deleted_degree)
        db.session.commit()
        return degree_schema.jsonify(deleted_degree)
    
    return route_reponse(admin, request.method)


"""
# Endpoint to delete all records and insert new data
@admin_api.route('/admin/courses_offered/update', methods=['POST'])
def update_course_offered():
    try:
        # Delete all records from the "course_offered" table
        CourseOffered.query.delete()

        # Insert new data into the "course_offered" table
        new_data = request.get_json()
        for row in new_data:
            course = CourseOffered(**row)
            db.session.add(course)

        # Commit the changes
        db.session.commit()

        return jsonify({'message': 'Data updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""
