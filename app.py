import sqlite3  # to use sqlite
import psycopg2
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# create a flask app instance
app = Flask(__name__)

# SQLALCHEMY configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:2&?jL!Un?SV$Q5j@db.qwydklzwvbrgvdomhxjb.supabase.co:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

# maps the database to an object
db = SQLAlchemy(app)


class Course(db.Model):
    __tablename__ = 'course'  # Specify the table name

    # Define the columns of the 'course' table
    course_id = db.Column('course_id', db.Integer, primary_key = True)
    subject_id = db.Column('subject_id', db.Integer,nullable = False)
    course_title = db.Column('course_title', db.String(100), nullable = True)
    course_num = db.Column('course_num', db.Integer,nullable = True)
    credits = db.Column('credits', db.Integer,nullable = True)

    # Add more columns here as needed

    def __init__(self,course_title):
        self.course_title = course_title
        self.subject_id = subject_id
        self.course_num = course_num
        self.credits = credits


    def __repr__(self):
        return f"Course_ID: {self.course_id} ({self.subject_id}), Course: {self.course_num} - {self.course_title} ({self.credits})"
        
@app.route('/')
def hello():
    print("Hey")

# endpoint for getting one courses
@app.route('/courses/<course_id>', methods = ['GET'])
def get_course(course_id):
    course = Course.query.filter_by(course_id = course_id).one()
    return {'course:': repr(course)}

# endpoint for getting all course
@app.route('/courses/get_all_courses', methods = ['GET'])
def get_all_courses():
    courses = Course.query.order_by(Course.course_id.asc()).all() 
    course_list = []
    for course in courses:
        course_list.append(repr(course))
    return {'course:': course_list}

# endpoint for creating a course
@app.route('/courses/create_course', methods = ['POST'])
def create_course():
    new_course = Course(request.json['course_title'])
    #db.session.add(new_course)
    #db.session.commit()
    return jsonify ({"success": "Success Post"})

"""def connect_database():

    conn = psycopg2.connect(
        host='db.qwydklzwvbrgvdomhxjb.supabase.co',
        port=5432,
        user='postgres',
        password='2&?jL!Un?SV$Q5j',
        database='postgres'
    )

    conn.autocommit = True

    cursor = conn.cursor()

    # insert_query = "insert into course (course_id, course_num) values (%s,%s)"
    # cursor.execute(insert_query, (2, 313))
    conn.commit()

    cursor.execute("select * from course")

    names = list(map(lambda x: x[0], cursor.description))

    # retrieve the records from the database
    records = cursor.fetchall()

    print(names)
    for row in records:
        print(row)

    # Closing the connection
    conn.close()
"""


if __name__ == '__main__':
    app.run(debug=True)
      
