import React, {useEffect, useState } from 'react';
import axios from "axios"
import {Link} from 'react-router-dom';

export default function ListCoursePage(){
    const [courses, setCourses] = useState([]);
    useEffect(() => {
        getCourses();
    }, []);

    function getCourses() {
        axios.get('http://127.0.0.1:5000/admin/courses').then(function(response) {
            console.log(response.data);
            setCourses(response.data);
        });
    }

    const deleteCourse = (id) => {
        axios.delete(`http://127.0.0.1:5000/admin/courses/delete/${id}`).then(function(response){
            console.log(response.data);
            getCourses();
        });
        alert("Successfully Deleted");
    }

    return (
    <div>
        <div className="container h-100">
            <div className="row h-100">
                <div className="col-12">
                    <p><Link to ="/create_course" className = "btn btn-success">Add New Course</Link> </p>
                    <h1>List Courses</h1>
                    <table class = "table table-bordered table-striped">
                        <thead>
                            <tr>
                                <th>Course_ID</th>
                                <th>Subject_ID</th>
                                <th>Course Title</th>
                                <th>Course Number</th>
                                <th>Credits</th>
                            </tr>
                        </thead>
                        <tbody>
                            {courses.map((course,key) =>
                                <tr key = {key}>
                                    <td>{course.course_id}</td>
                                    <td>{course.subject_id}</td>
                                    <td>{course.crs_title}</td>
                                    <td>{course.crs_num}</td>
                                    <td>{course.credits}</td>
                                <td>
                                    <Link to={`course/${course.course_id}/edit`} className="btn btn-success" style={{marginRight: "10px"}}>Edit</Link>
                                    <button onClick={() => deleteCourse(course.course_id)} className="btn btn-danger">Delete</button>

                                </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    );
}